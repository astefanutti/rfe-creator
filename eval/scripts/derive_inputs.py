#!/usr/bin/env python3
"""Derive initial problem statements from existing RFE descriptions.

Takes bootstrapped eval cases (with rfe_content from Jira) and uses Opus
to reverse-engineer the kind of problem statement a PM would have typed
to start the RFE, plus answers to standard clarifying questions.

Usage:
    # Derive inputs for all cases
    python3 eval/scripts/derive_inputs.py

    # Derive for a specific case
    python3 eval/scripts/derive_inputs.py --case case-001-slug

    # Force re-derive (overwrite existing prompt/clarifying_context)
    python3 eval/scripts/derive_inputs.py --force
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = PROJECT_ROOT / "eval" / "dataset"
CASES_DIR = DATASET_DIR / "cases"

DERIVE_PROMPT = """You are helping create an evaluation dataset for an RFE (Request for Enhancement) creation pipeline.

Given an existing RFE description from Jira, produce two things:

1. **prompt**: A realistic problem statement that a Product Manager would have typed to initiate this RFE. This should be 2-5 sentences describing the business need or pain point — the kind of informal input that starts the RFE creation process. Do NOT include the full RFE structure — just the initial seed idea.

2. **clarifying_context**: Answers to the standard clarifying questions the RFE creation skill would ask. Format as key-value pairs covering:
   - **Customers**: Specific customer names, segments, or partners affected
   - **Business justification**: Revenue impact, customer commitments, strategic investments
   - **User problem**: What users can't do today or what is painful
   - **Scope**: Is this one focused need or multiple? How big is it?
   - **Success criteria**: How would the user know the problem is solved?

Extract these from the RFE content. If the RFE doesn't mention specific customers, invent plausible ones consistent with the domain. The goal is to provide enough context that an RFE creation skill can produce a good RFE without needing to ask any questions.

Respond with valid JSON:
```json
{
  "prompt": "...",
  "clarifying_context": "..."
}
```

The clarifying_context should be a single string with labeled sections, like:
```
Customers: Acme Corp ML team, BigBank data science division
Business justification: 3 enterprise renewal deals worth $2M ARR are blocked on this capability
User problem: Data scientists cannot monitor training progress across distributed nodes...
Scope: Single focused need — training observability across frameworks
Success criteria: Users can see real-time per-node metrics in the dashboard
```"""


def derive_for_case(case_dir: Path, model: str, force: bool = False) -> bool:
    """Derive prompt + clarifying_context for a single case.

    Returns True if derivation was performed, False if skipped.
    """
    input_path = case_dir / "input.yaml"
    if not input_path.exists():
        print(f"  Skipping {case_dir.name}: no input.yaml")
        return False

    with open(input_path) as f:
        input_data = yaml.safe_load(f)

    # Skip if already derived (unless --force)
    if not force and input_data.get("prompt"):
        print(f"  Skipping {case_dir.name}: already has prompt (use --force)")
        return False

    rfe_content = input_data.get("rfe_content", "")
    if not rfe_content.strip():
        print(f"  Skipping {case_dir.name}: empty rfe_content")
        return False

    title = input_data.get("title", "Untitled")

    user_message = f"""## RFE Title
{title}

## RFE Description
{rfe_content}"""

    from anthropic_client import create_client
    client = create_client()

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=DERIVE_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = response.content[0].text

    # Parse JSON from response (handle markdown code blocks)
    json_text = response_text
    if "```json" in json_text:
        json_text = json_text.split("```json")[1].split("```")[0]
    elif "```" in json_text:
        json_text = json_text.split("```")[1].split("```")[0]

    parsed = json.loads(json_text.strip())

    # Update input.yaml
    input_data["prompt"] = parsed["prompt"]
    input_data["clarifying_context"] = parsed["clarifying_context"]
    input_data["pipeline"] = "rfe.speedrun"
    input_data["input_type"] = "derived_prompt"

    with open(input_path, "w") as f:
        yaml.dump(input_data, f, default_flow_style=False, allow_unicode=True,
                  width=120, sort_keys=False)

    return True


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", default=None,
                        help="Specific case directory name (substring match)")
    parser.add_argument("--force", action="store_true",
                        help="Re-derive even if prompt already exists")
    parser.add_argument("--model", default="claude-opus-4-6",
                        help="Model for derivation (default: claude-opus-4-6)")
    args = parser.parse_args()

    if not CASES_DIR.exists():
        print("No dataset found. Run bootstrap_dataset.py first.",
              file=sys.stderr)
        sys.exit(1)

    cases = sorted(d for d in CASES_DIR.iterdir() if d.is_dir())
    if args.case:
        cases = [c for c in cases if args.case in c.name]
        if not cases:
            print(f"No cases matching '{args.case}'", file=sys.stderr)
            sys.exit(1)

    print(f"Deriving inputs for {len(cases)} cases using {args.model}...\n")

    derived = 0
    for case_dir in cases:
        print(f"[{case_dir.name}]", end=" ", flush=True)
        try:
            if derive_for_case(case_dir, args.model, args.force):
                derived += 1
                print("done")
            # else: skip message already printed
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\nDerived {derived}/{len(cases)} cases")


if __name__ == "__main__":
    main()
