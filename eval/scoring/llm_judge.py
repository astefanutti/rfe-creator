"""Layer 3: LLM-as-judge meta-evaluation.

Assesses revision quality, content fidelity, and pipeline calibration
using a strong model (Opus) via the Anthropic API directly.
Not run through the agent pipeline — the judge is independent.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
JUDGE_PROMPT_PATH = CONFIG_DIR / "judge-prompt.md"
JUDGE_PROMPT_FULL_PIPELINE_PATH = CONFIG_DIR / "judge-prompt-full-pipeline.md"

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "revision_quality": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "score": {"type": "integer"},
            },
            "required": ["reasoning", "score"],
        },
        "content_fidelity": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "score": {"type": "integer"},
            },
            "required": ["reasoning", "score"],
        },
        "calibration_accuracy": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "score": {"type": "integer"},
            },
            "required": ["reasoning", "score"],
        },
        "reframing_quality": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "score": {"type": ["integer", "null"]},
            },
            "required": ["reasoning", "score"],
        },
    },
    "required": ["revision_quality", "content_fidelity",
                  "calibration_accuracy", "reframing_quality"],
}


@dataclass
class JudgeResult:
    """LLM judge scores for one eval case."""
    case_id: str
    revision_quality: Optional[int] = None
    content_fidelity: Optional[int] = None
    calibration_accuracy: Optional[int] = None
    reframing_quality: Optional[int] = None  # None = N/A
    reasoning: dict = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def mean_score(self) -> Optional[float]:
        scores = [s for s in (self.revision_quality, self.content_fidelity,
                               self.calibration_accuracy, self.reframing_quality)
                  if s is not None]
        return sum(scores) / len(scores) if scores else None

    @property
    def summary(self) -> dict:
        return {
            "case_id": self.case_id,
            "revision_quality": self.revision_quality,
            "content_fidelity": self.content_fidelity,
            "calibration_accuracy": self.calibration_accuracy,
            "reframing_quality": self.reframing_quality,
            "mean_score": self.mean_score,
            "error": self.error,
        }


def score(
    case_output_dir: Path,
    project_root: Path,
    model: str = "claude-opus-4-6",
    dataset_case_dir: Optional[Path] = None,
) -> JudgeResult:
    """Run the LLM judge on a single eval case.

    Detects pipeline mode:
    - If reference-rfe.md exists in dataset case: compare against gold standard
    - If rfe-originals/ exists in output: review-only mode (revision_quality, etc.)
    - Fallback: assess quality standalone

    Args:
        case_output_dir: eval/runs/{run_id}/cases/{case_id}/ with artifacts.
        project_root: For loading originals and review files.
        model: Model to use for judging (default: Opus).
        dataset_case_dir: eval/dataset/cases/{case_id}/ for reference files.

    Returns:
        JudgeResult with scores and reasoning.
    """
    case_id = case_output_dir.name
    result = JudgeResult(case_id=case_id)

    review = _load_review(case_output_dir)
    revised = _load_revised(case_output_dir)

    if not revised or not review:
        tasks_dir = case_output_dir / "rfe-tasks"
        reviews_dir = case_output_dir / "rfe-reviews"
        task_files = list(tasks_dir.glob("*.md")) if tasks_dir.exists() else []
        review_files = list(reviews_dir.glob("*-review.md")) if reviews_dir.exists() else []
        result.error = (
            f"Missing artifacts — tasks: {len(task_files)} files "
            f"({', '.join(f.name for f in task_files[:3]) or 'none'}), "
            f"reviews: {len(review_files)} files "
            f"({', '.join(f.name for f in review_files[:3]) or 'none'}). "
            f"The pipeline likely failed for this case — check "
            f"{case_output_dir}/stderr.log"
        )
        return result

    # Check for gold standard reference (from gold command)
    reference_path = dataset_case_dir / "reference-rfe.md" if dataset_case_dir else None
    has_reference = reference_path and reference_path.exists()

    # Check for originals (review-only mode)
    has_originals = (case_output_dir / "rfe-originals").exists() and \
        bool(list((case_output_dir / "rfe-originals").glob("*.md")))

    if has_reference:
        # Compare against gold standard (Opus baseline output)
        gold_rfe = reference_path.read_text()
        judge_prompt = JUDGE_PROMPT_FULL_PIPELINE_PATH.read_text()
        user_message = f"""## GROUND TRUTH

{gold_rfe}

## GENERATED RFE

{revised}

## PIPELINE REVIEW

{review}"""
        is_full_pipeline = True
    elif has_originals:
        # Review-only mode: compare original vs revised
        original = _load_original(case_output_dir)
        if not original:
            result.error = "Missing original RFE (review-only mode)"
            return result
        judge_prompt = JUDGE_PROMPT_PATH.read_text()
        user_message = f"""## ORIGINAL RFE

{original}

## REVISED RFE

{revised}

## PIPELINE REVIEW

{review}"""
        is_full_pipeline = False
    else:
        result.error = "No reference or original to compare against"
        return result

    # Call Anthropic API
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        from anthropic_client import create_client
    except ImportError:
        result.error = ("anthropic package not installed. "
                        "Install with: pip install anthropic")
        return result

    try:
        client = create_client()
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=judge_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        # Parse response (strip markdown code blocks if present)
        response_text = response.content[0].text
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]
        parsed = json.loads(json_text.strip())

        result.calibration_accuracy = parsed["calibration_accuracy"]["score"]
        result.reasoning["calibration_accuracy"] = \
            parsed["calibration_accuracy"]["reasoning"]

        if is_full_pipeline:
            # Full-pipeline: coverage maps to content_fidelity,
            # quality maps to revision_quality (reusing fields)
            result.revision_quality = parsed["quality"]["score"]
            result.content_fidelity = parsed["coverage"]["score"]
            result.reasoning["quality"] = parsed["quality"]["reasoning"]
            result.reasoning["coverage"] = parsed["coverage"]["reasoning"]
        else:
            # Review-only: original dimensions
            result.revision_quality = parsed["revision_quality"]["score"]
            result.content_fidelity = parsed["content_fidelity"]["score"]
            result.reframing_quality = parsed["reframing_quality"]["score"]
            result.reasoning["revision_quality"] = \
                parsed["revision_quality"]["reasoning"]
            result.reasoning["content_fidelity"] = \
                parsed["content_fidelity"]["reasoning"]
            result.reasoning["reframing_quality"] = \
                parsed["reframing_quality"]["reasoning"]

    except json.JSONDecodeError as e:
        result.error = f"Failed to parse judge response as JSON: {e}"
    except KeyError as e:
        result.error = f"Missing key in judge response: {e}"
    except Exception as e:
        result.error = f"API call failed: {e}"

    return result


def aggregate(results: list, thresholds: dict) -> dict:
    """Aggregate judge results across all cases.

    Args:
        results: List of JudgeResult objects.
        thresholds: From config/thresholds.yaml llm_judge section.

    Returns:
        Aggregate summary with pass/fail status.
    """
    scored = [r for r in results if r.error is None]
    if not scored:
        return {
            "status": "skip",
            "reason": f"No successful judge runs ({len(results)} errors)",
            "errors": [r.error for r in results if r.error],
        }

    means = [r.mean_score for r in scored if r.mean_score is not None]
    overall_mean = sum(means) / len(means) if means else 0

    cal_scores = [r.calibration_accuracy for r in scored
                  if r.calibration_accuracy is not None]
    cal_mean = sum(cal_scores) / len(cal_scores) if cal_scores else 0

    min_mean = thresholds.get("min_mean_score", 3.5)
    min_cal = thresholds.get("min_calibration_accuracy", 3.0)

    passed = overall_mean >= min_mean and cal_mean >= min_cal

    return {
        "status": "pass" if passed else "fail",
        "cases_judged": len(scored),
        "cases_errored": len(results) - len(scored),
        "mean_score": round(overall_mean, 2),
        "mean_score_threshold": min_mean,
        "calibration_mean": round(cal_mean, 2),
        "calibration_threshold": min_cal,
        "per_dimension": {
            "revision_quality": _dim_mean(scored, "revision_quality"),
            "content_fidelity": _dim_mean(scored, "content_fidelity"),
            "calibration_accuracy": round(cal_mean, 2),
            "reframing_quality": _dim_mean(scored, "reframing_quality"),
        },
    }


def _dim_mean(results: list, dim: str) -> Optional[float]:
    vals = [getattr(r, dim) for r in results if getattr(r, dim) is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


def _load_original(case_dir: Path) -> Optional[str]:
    originals = case_dir / "rfe-originals"
    if not originals.exists():
        return None
    for f in sorted(originals.iterdir()):
        if f.name.endswith(".md"):
            return f.read_text()
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
