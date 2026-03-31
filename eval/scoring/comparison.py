"""Pairwise model/runner comparison using position-swapped LLM judge.

Compares two runs on the same dataset by showing both outputs to a judge
in both orderings. Consistent preference = winner; inconsistent = tie.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


COMPARISON_PROMPT = """You are comparing two RFE review pipeline outputs (A and B) for the same input RFE. Both pipelines reviewed and revised the same original RFE.

Evaluate which pipeline produced a better result across these dimensions:
1. **Revision quality** — Which revision is more substantive and beneficial?
2. **Content fidelity** — Which revision better preserves business-critical information?
3. **Review calibration** — Which review's scores better match the actual quality of its revised RFE?

Output your preference as JSON:

```json
{
  "reasoning": "Brief comparison reasoning",
  "preferred": "A" or "B" or "tie"
}
```

Be decisive. Only declare "tie" if the outputs are genuinely equivalent in quality."""


@dataclass
class PairwiseResult:
    """Comparison result for one case."""
    case_id: str
    pref_ab: Optional[str] = None   # "A", "B", or "tie" (A shown first)
    pref_ba: Optional[str] = None   # "A", "B", or "tie" (B shown first)
    reasoning_ab: str = ""
    reasoning_ba: str = ""
    error: Optional[str] = None

    @property
    def winner(self) -> str:
        """Determine winner from position-swapped judgments."""
        if self.error or not self.pref_ab or not self.pref_ba:
            return "error"

        # Map preferences to original identities
        # In AB ordering: A=run_a, B=run_b
        # In BA ordering: A=run_b, B=run_a
        ab_prefers_a = self.pref_ab == "A"  # Prefers run_a
        ba_prefers_b = self.pref_ba == "B"  # Also prefers run_a (shown as B)

        ab_prefers_b = self.pref_ab == "B"  # Prefers run_b
        ba_prefers_a = self.pref_ba == "A"  # Also prefers run_b (shown as A)

        if ab_prefers_a and ba_prefers_b:
            return "A"  # Consistent preference for run_a
        elif ab_prefers_b and ba_prefers_a:
            return "B"  # Consistent preference for run_b
        else:
            return "tie"  # Inconsistent or both ties


def compare(
    run_a_dir: Path,
    run_b_dir: Path,
    case_ids: list,
    model: str = "claude-opus-4-6",
) -> dict:
    """Compare two runs on shared cases using position-swapped LLM judge.

    Args:
        run_a_dir: eval/runs/{run_a_id}/ directory.
        run_b_dir: eval/runs/{run_b_id}/ directory.
        case_ids: List of case IDs to compare.
        model: Model for the judge.

    Returns:
        Comparison summary with per-case results and aggregate.
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        from anthropic_client import create_client
        client = create_client()
    except ImportError:
        return {"error": "anthropic package not installed"}

    results = []
    for case_id in case_ids:
        case_a = run_a_dir / "cases" / case_id
        case_b = run_b_dir / "cases" / case_id

        if not case_a.exists() or not case_b.exists():
            results.append(PairwiseResult(
                case_id=case_id,
                error=f"Missing case dir: a={case_a.exists()}, b={case_b.exists()}",
            ))
            continue

        result = _judge_pair(client, model, case_id, case_a, case_b)
        results.append(result)

    # Aggregate
    wins_a = sum(1 for r in results if r.winner == "A")
    wins_b = sum(1 for r in results if r.winner == "B")
    ties = sum(1 for r in results if r.winner == "tie")
    errors = sum(1 for r in results if r.winner == "error")

    return {
        "run_a": run_a_dir.name,
        "run_b": run_b_dir.name,
        "cases_compared": len(results),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "errors": errors,
        "per_case": [
            {
                "case_id": r.case_id,
                "winner": r.winner,
                "pref_ab": r.pref_ab,
                "pref_ba": r.pref_ba,
                "error": r.error,
            }
            for r in results
        ],
    }


def _judge_pair(
    client, model: str, case_id: str, case_a: Path, case_b: Path
) -> PairwiseResult:
    """Run position-swapped comparison for one case."""
    result = PairwiseResult(case_id=case_id)

    revised_a = _load_revised(case_a)
    revised_b = _load_revised(case_b)
    review_a = _load_review(case_a)
    review_b = _load_review(case_b)

    if not all([revised_a, revised_b, review_a, review_b]):
        result.error = "Missing revised RFE or review in one or both runs"
        return result

    # Judgment 1: A first, B second
    msg_ab = _build_message(revised_a, review_a, revised_b, review_b)
    pref_ab = _call_judge(client, model, msg_ab)
    if pref_ab:
        result.pref_ab = pref_ab.get("preferred")
        result.reasoning_ab = pref_ab.get("reasoning", "")
    else:
        result.error = "Judge call failed (AB ordering)"
        return result

    # Judgment 2: B first, A second (position swap)
    msg_ba = _build_message(revised_b, review_b, revised_a, review_a)
    pref_ba = _call_judge(client, model, msg_ba)
    if pref_ba:
        result.pref_ba = pref_ba.get("preferred")
        result.reasoning_ba = pref_ba.get("reasoning", "")
    else:
        result.error = "Judge call failed (BA ordering)"

    return result


def _build_message(
    revised_1: str, review_1: str, revised_2: str, review_2: str
) -> str:
    return f"""## Pipeline A — Revised RFE

{revised_1}

## Pipeline A — Review

{review_1}

## Pipeline B — Revised RFE

{revised_2}

## Pipeline B — Review

{review_2}"""


def _call_judge(client, model: str, user_message: str) -> Optional[dict]:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=COMPARISON_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text
        return json.loads(text)
    except Exception:
        return None


def _load_revised(case_dir: Path) -> Optional[str]:
    tasks = case_dir / "rfe-tasks"
    if not tasks.exists():
        return None
    for f in sorted(tasks.iterdir()):
        if (f.name.endswith(".md") and
                not f.name.endswith("-comments.md") and
                not f.name.endswith("-removed-context.md")):
            return f.read_text()
    return None


def _load_review(case_dir: Path) -> Optional[str]:
    reviews = case_dir / "rfe-reviews"
    if not reviews.exists():
        return None
    for f in sorted(reviews.iterdir()):
        if f.name.endswith("-review.md"):
            return f.read_text()
    return None
