#!/usr/bin/env python3
"""RFE Creator evaluation harness -- main CLI.

Usage:
    # Run a single case
    python3 eval/scripts/run_eval.py run --runner claude-code --model opus --case case-001-slug

    # Run full dataset
    python3 eval/scripts/run_eval.py run --runner claude-code --model sonnet --run-id my-run

    # Generate gold standard outputs
    python3 eval/scripts/run_eval.py gold --runner claude-code --model opus

    # Score an existing run (layers 1+2 only by default)
    python3 eval/scripts/run_eval.py score --run-id my-run

    # Score with LLM judge (layer 3)
    python3 eval/scripts/run_eval.py score --run-id my-run --judge

    # Compare two runs
    python3 eval/scripts/run_eval.py compare --run-a run-1 --run-b run-2
"""

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

# Resolve project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_ROOT = PROJECT_ROOT / "eval"

sys.path.insert(0, str(EVAL_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from runners.base import RunResult
from runners.claude_code import ClaudeCodeRunner
from scripts.prepare_workspace import prepare
from scripts.collect_artifacts import collect
from scoring import deterministic, reference
from reporting.report import print_text_report, generate_html_report


RUNNERS = {
    "claude-code": ClaudeCodeRunner,
}

DATASET_DIR = EVAL_ROOT / "dataset"
RUNS_DIR = EVAL_ROOT / "runs"
CONFIG_DIR = EVAL_ROOT / "config"


def cmd_run(args):
    """Run eval on one or more cases."""
    runner_cls = RUNNERS.get(args.runner)
    if not runner_cls:
        print(f"Unknown runner: {args.runner}. Available: {list(RUNNERS.keys())}",
              file=sys.stderr)
        sys.exit(1)

    runner = runner_cls()
    cases = _resolve_cases(args.case)
    run_id = args.run_id or f"{datetime.now():%Y-%m-%d}-{args.model}-{runner.name}"
    run_dir = RUNS_DIR / run_id

    settings_path = CONFIG_DIR / "settings.json"
    if not settings_path.exists():
        settings_path = None

    # Write run manifest
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "runner": runner.name,
        "model": args.model,
        "date": datetime.now().isoformat(),
        "cases": [c.name for c in cases],
        "settings": str(settings_path) if settings_path else None,
        "max_budget_usd": args.max_budget,
    }
    with open(run_dir / "manifest.yaml", "w") as f:
        yaml.dump(manifest, f, default_flow_style=False)

    print(f"Starting eval run: {run_id}")
    print(f"Runner: {runner.name} | Model: {args.model} | Cases: {len(cases)}")
    print()

    # Load eval-mode system prompt for full-pipeline cases
    eval_system_prompt_path = CONFIG_DIR / "eval-system-prompt.md"
    eval_system_prompt = None
    if eval_system_prompt_path.exists():
        eval_system_prompt = eval_system_prompt_path.read_text().strip()

    def _run_case(case_dir):
        """Run a single case. Returns (case_id, result, collected)."""
        case_id = case_dir.name

        with open(case_dir / "input.yaml") as f:
            input_data = yaml.safe_load(f)

        pipeline = input_data.get("pipeline", "rfe.review")
        rfe_id = input_data["rfe_id"]
        case_output = run_dir / "cases" / case_id

        workspace = prepare(
            case_dir=case_dir,
            run_id=run_id,
            project_root=PROJECT_ROOT,
            output_dir=case_output,
        )

        if pipeline == "rfe.speedrun":
            skill_name = "rfe.speedrun"
            prompt_text = input_data.get("prompt", "")
            clarifying = input_data.get("clarifying_context", "")
            skill_args = (f"RFE ID: {rfe_id}\n\n"
                          f"{prompt_text}\n\n"
                          f"Additional context:\n{clarifying}")
            system_prompt = eval_system_prompt
        else:
            skill_name = "rfe.review"
            skill_args = rfe_id
            system_prompt = None

        # Short label for log prefix (e.g. "case-001")
        short_id = "-".join(case_id.split("-")[:2])

        result = runner.run_skill(
            skill_name=skill_name,
            args=skill_args,
            workspace=workspace,
            model=args.model,
            settings_path=settings_path,
            system_prompt=system_prompt,
            max_budget_usd=args.max_budget,
            timeout_s=args.timeout,
            log_prefix=short_id,
        )

        collected = collect(
            workspace=workspace,
            output_dir=case_output,
            project_root=PROJECT_ROOT,
        )

        # Save logs
        run_meta = {
            "exit_code": result.exit_code,
            "duration_s": round(result.duration_s, 1),
            "token_usage": result.token_usage,
            "cost_usd": result.cost_usd,
        }
        with open(case_output / "run_result.json", "w") as f:
            json.dump(run_meta, f, indent=2)
        if result.stdout:
            (case_output / "stdout.log").write_text(result.stdout)
        if result.stderr:
            (case_output / "stderr.log").write_text(result.stderr)

        if not args.keep_workspaces:
            shutil.rmtree(workspace, ignore_errors=True)

        return case_id, result, collected

    # Run cases in parallel
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import os
    parallelism = getattr(args, "parallel", None) or min(len(cases), os.cpu_count() or 4)
    print(f"Running {len(cases)} cases with parallelism={parallelism}\n")

    completed = 0
    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = {pool.submit(_run_case, c): c for c in cases}
        for future in as_completed(futures):
            completed += 1
            try:
                case_id, result, collected = future.result()
            except Exception as e:
                case_id = futures[future].name
                print(f"[{completed}/{len(cases)}] {case_id}... "
                      f"EXCEPTION: {e}")
                continue

            status = "ok" if result.exit_code == 0 else f"exit={result.exit_code}"
            tasks = len(collected.get("tasks", []))
            reviews = len(collected.get("reviews", []))
            print(f"[{completed}/{len(cases)}] {case_id}... "
                  f"{status} ({result.duration_s:.0f}s, "
                  f"tasks={tasks}, reviews={reviews})")

            if result.exit_code != 0:
                stderr_preview = result.stderr.strip()[:300] if result.stderr else ""
                stdout_preview = result.stdout.strip()[:300] if result.stdout else ""
                if stderr_preview:
                    print(f"  stderr: {stderr_preview}")
                elif stdout_preview:
                    print(f"  stdout: {stdout_preview}")
                else:
                    case_output = run_dir / "cases" / case_id
                    print(f"  (no output — check {case_output}/stderr.log)")
            elif args.verbose:
                if result.stderr:
                    print(f"  stderr: {result.stderr.strip()[:200]}")

    print(f"\nRun complete: {run_dir}")

    # Auto-score if requested
    if args.score:
        print("\nScoring...")
        judge = not getattr(args, "no_judge", False)
        baseline = getattr(args, "baseline", None)
        _score_run(run_id, judge=judge, baseline=baseline)


def _save_references(run_id: str):
    """Copy successful outputs from a run to dataset as reference files."""
    run_dir = RUNS_DIR / run_id
    cases_dir = run_dir / "cases"

    if not cases_dir.exists():
        print("No cases found in run output.", file=sys.stderr)
        return 0

    copied = 0
    for case_output in sorted(cases_dir.iterdir()):
        if not case_output.is_dir():
            continue

        # Check if run succeeded
        result_path = case_output / "run_result.json"
        if result_path.exists():
            with open(result_path) as f:
                run_result = json.load(f)
            if run_result.get("exit_code", 1) != 0:
                print(f"  Skipping {case_output.name}: exit={run_result['exit_code']}")
                continue

        dataset_case = DATASET_DIR / "cases" / case_output.name
        if not dataset_case.exists():
            continue

        # Find and copy the generated RFE as reference
        tasks_dir = case_output / "rfe-tasks"
        if tasks_dir.exists():
            for f in sorted(tasks_dir.iterdir()):
                if (f.name.endswith(".md") and
                        not f.name.endswith("-comments.md") and
                        not f.name.endswith("-removed-context.md")):
                    shutil.copy2(f, dataset_case / "reference-rfe.md")
                    break

        # Find and copy the review as reference
        reviews_dir = case_output / "rfe-reviews"
        if reviews_dir.exists():
            for f in sorted(reviews_dir.iterdir()):
                if f.name.endswith("-review.md"):
                    shutil.copy2(f, dataset_case / "reference-review.md")
                    break

        copied += 1

    return copied


def cmd_gold(args):
    """Generate gold-standard outputs from Opus and save as references."""
    args.run_id = args.run_id or f"gold-{datetime.now():%Y-%m-%d}"
    args.score = True
    args.keep_workspaces = False
    args.verbose = False
    cmd_run(args)

    copied = _save_references(args.run_id)
    print(f"\nGold standard: copied {copied} reference files to dataset")
    print(f"These Opus outputs are now the ground truth for future comparisons.")


def cmd_save_gold(args):
    """Save references from an existing run (without re-running)."""
    copied = _save_references(args.run_id)
    print(f"Saved {copied} reference files from {args.run_id} to dataset")


def cmd_score(args):
    """Score an existing run."""
    _score_run(args.run_id, judge=not args.no_judge, baseline=args.baseline)


def _score_run(run_id: str, judge: bool = False, baseline: str = None):
    """Run scoring layers on a completed run."""
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        print(f"Run not found: {run_dir}", file=sys.stderr)
        sys.exit(1)

    with open(run_dir / "manifest.yaml") as f:
        manifest = yaml.safe_load(f)

    cases_dir = run_dir / "cases"
    case_dirs = sorted(d for d in cases_dir.iterdir() if d.is_dir())

    # Layer 1: Deterministic
    det_results = []
    for case_dir in case_dirs:
        det = deterministic.score(case_dir, PROJECT_ROOT)
        det_results.append(det.summary)

    det_summary = {
        "total_cases": len(det_results),
        "total_passed": sum(1 for r in det_results if r["all_pass"]),
        "cases": det_results,
    }

    # Layer 2: Reference
    ref_results = []
    for case_dir in case_dirs:
        dataset_case = DATASET_DIR / "cases" / case_dir.name
        if dataset_case.exists():
            ref = reference.score(case_dir, dataset_case, PROJECT_ROOT)
            ref_results.append(ref.summary)

    with open(CONFIG_DIR / "thresholds.yaml") as f:
        thresholds = yaml.safe_load(f) or {}

    ref_summary = reference.aggregate(
        [reference.ReferenceResult(**r) if isinstance(r, dict)
         else r for r in ref_results],
        thresholds.get("reference", {}),
    )
    ref_summary["per_case"] = ref_results

    # Layer 3: LLM Judge (optional)
    judge_summary = {"status": "skip", "reason": "Skipped (--no-judge)"}
    if judge:
        from scoring import llm_judge
        judge_results = []
        for case_dir in case_dirs:
            print(f"  Judging {case_dir.name}...", end=" ", flush=True)
            dataset_case = DATASET_DIR / "cases" / case_dir.name
            jr = llm_judge.score(
                case_dir, PROJECT_ROOT,
                dataset_case_dir=dataset_case if dataset_case.exists() else None,
            )
            judge_results.append(jr)
            if jr.error:
                print(f"error: {jr.error}")
            else:
                print(f"mean={jr.mean_score:.1f}")

        judge_summary = llm_judge.aggregate(
            judge_results, thresholds.get("llm_judge", {}))

    # Regression detection
    regressions = []
    if baseline:
        from scoring import regression as reg_mod
        baseline_dir = RUNS_DIR / baseline
        if baseline_dir.exists() and (baseline_dir / "summary.yaml").exists():
            with open(baseline_dir / "summary.yaml") as f:
                baseline_summary = yaml.safe_load(f)
            regs = reg_mod.detect(
                {"deterministic": det_summary, "reference": ref_summary,
                 "llm_judge": judge_summary},
                baseline_summary,
                CONFIG_DIR / "thresholds.yaml",
            )
            regressions = [
                {"case_id": r.case_id, "metric": r.metric,
                 "baseline_value": r.baseline_value,
                 "current_value": r.current_value, "detail": r.detail}
                for r in regs
            ]
        else:
            baseline_path = baseline_dir / "summary.yaml"
            if not baseline_dir.exists():
                print(f"  Baseline run '{baseline}' not found at {baseline_dir}")
            elif not baseline_path.exists():
                print(f"  Baseline run '{baseline}' has no summary.yaml — "
                      f"run 'score --run-id {baseline}' first to generate it")
    else:
        from scoring import regression as reg_mod
        regs = reg_mod.detect(
            {"deterministic": det_summary, "reference": ref_summary,
             "llm_judge": judge_summary},
            None,
            CONFIG_DIR / "thresholds.yaml",
        )
        regressions = [
            {"case_id": r.case_id, "metric": r.metric,
             "baseline_value": r.baseline_value,
             "current_value": r.current_value, "detail": r.detail}
            for r in regs
        ]

    # Build summary
    summary = {
        "metadata": {
            "run_id": run_id,
            "runner": manifest.get("runner"),
            "model": manifest.get("model"),
            "date": manifest.get("date"),
            "cases_total": len(case_dirs),
            "dataset": str(DATASET_DIR),
        },
        "deterministic": det_summary,
        "reference": ref_summary,
        "llm_judge": judge_summary,
        "regressions": regressions,
        "baseline_run": baseline,
    }

    # Save summary
    with open(run_dir / "summary.yaml", "w") as f:
        yaml.dump(summary, f, default_flow_style=False, allow_unicode=True)

    # Print text report
    print_text_report(summary)

    # Generate HTML report (with diffs if baseline provided)
    html_path = run_dir / "report.html"
    baseline_run_dir = RUNS_DIR / baseline if baseline else None
    if baseline_run_dir and not baseline_run_dir.exists():
        baseline_run_dir = None
    generate_html_report(
        summary, html_path,
        current_run_dir=run_dir,
        baseline_run_dir=baseline_run_dir,
    )
    print(f"HTML report: {html_path}")


def cmd_compare(args):
    """Compare two runs using pairwise LLM judge."""
    from scoring import comparison

    run_a_dir = RUNS_DIR / args.run_a
    run_b_dir = RUNS_DIR / args.run_b

    for d in (run_a_dir, run_b_dir):
        if not d.exists():
            print(f"Run not found: {d}", file=sys.stderr)
            sys.exit(1)

    # Find shared cases
    cases_a = {d.name for d in (run_a_dir / "cases").iterdir() if d.is_dir()}
    cases_b = {d.name for d in (run_b_dir / "cases").iterdir() if d.is_dir()}
    shared = sorted(cases_a & cases_b)

    if not shared:
        print("No shared cases between runs.", file=sys.stderr)
        sys.exit(1)

    print(f"Comparing {args.run_a} vs {args.run_b} on {len(shared)} cases...")
    result = comparison.compare(
        run_a_dir=run_a_dir,
        run_b_dir=run_b_dir,
        case_ids=shared,
        model=args.judge_model,
    )

    # Print results
    print(f"\n{args.run_a} wins: {result.get('wins_a', 0)}")
    print(f"{args.run_b} wins: {result.get('wins_b', 0)}")
    print(f"Ties: {result.get('ties', 0)}")

    # Save comparison
    comp_path = RUNS_DIR / f"comparison-{args.run_a}-vs-{args.run_b}.json"
    with open(comp_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nDetails: {comp_path}")


def _resolve_cases(case_filters: list = None) -> list:
    """Resolve which cases to run."""
    cases_dir = DATASET_DIR / "cases"
    if not cases_dir.exists():
        print("No dataset found. Run bootstrap_dataset.py first.",
              file=sys.stderr)
        sys.exit(1)

    all_cases = sorted(d for d in cases_dir.iterdir() if d.is_dir())

    if case_filters:
        filtered = [c for c in all_cases
                    if any(f in c.name for f in case_filters)]
        if not filtered:
            print(f"No cases matching {case_filters}", file=sys.stderr)
            sys.exit(1)
        return filtered

    return all_cases


def main():
    parser = argparse.ArgumentParser(
        description="RFE Creator evaluation harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run eval on cases")
    run_parser.add_argument("--runner", default="claude-code",
                            help="Runner to use (default: claude-code)")
    run_parser.add_argument("--model", required=True,
                            help="Model to test (e.g. opus, sonnet)")
    run_parser.add_argument("--case", nargs="*", default=None,
                            help="Filter to specific cases (substring match, multiple allowed)")
    run_parser.add_argument("--run-id", default=None,
                            help="Custom run ID (default: auto-generated)")
    run_parser.add_argument("--max-budget", type=float, default=5.0,
                            help="Max budget per case in USD (default: 5.0)")
    run_parser.add_argument("--timeout", type=int, default=600,
                            help="Timeout per case in seconds (default: 600)")
    run_parser.add_argument("--score", action="store_true",
                            help="Auto-score after run")
    run_parser.add_argument("--keep-workspaces", action="store_true",
                            help="Don't clean up temp workspaces")
    run_parser.add_argument("--parallel", type=int, default=None,
                            help="Max parallel cases (default: all)")
    run_parser.add_argument("--baseline", default=None,
                            help="Baseline run ID for regression detection")
    run_parser.add_argument("--no-judge", action="store_true",
                            help="Skip LLM judge when scoring")
    run_parser.add_argument("--verbose", action="store_true",
                            help="Show stderr on failures")

    # gold command
    gold_parser = subparsers.add_parser("gold",
                                        help="Generate gold standard outputs")
    gold_parser.add_argument("--runner", default="claude-code")
    gold_parser.add_argument("--model", default="opus")
    gold_parser.add_argument("--case", default=None)
    gold_parser.add_argument("--run-id", default=None)
    gold_parser.add_argument("--max-budget", type=float, default=5.0)
    gold_parser.add_argument("--timeout", type=int, default=600)

    # save-gold command
    save_gold_parser = subparsers.add_parser("save-gold",
                                              help="Save references from an existing run")
    save_gold_parser.add_argument("--run-id", required=True,
                                   help="Run ID to save as gold standard")

    # score command
    score_parser = subparsers.add_parser("score", help="Score an existing run")
    score_parser.add_argument("--run-id", required=True)
    score_parser.add_argument("--no-judge", action="store_true",
                              help="Skip LLM judge (layer 3)")
    score_parser.add_argument("--baseline", default=None,
                              help="Baseline run ID for regression detection")

    # compare command
    compare_parser = subparsers.add_parser("compare",
                                           help="Compare two runs")
    compare_parser.add_argument("--run-a", required=True)
    compare_parser.add_argument("--run-b", required=True)
    compare_parser.add_argument("--judge-model", default="claude-opus-4-6",
                                help="Model for comparison judge")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "gold":
        cmd_gold(args)
    elif args.command == "save-gold":
        cmd_save_gold(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "compare":
        cmd_compare(args)


if __name__ == "__main__":
    main()
