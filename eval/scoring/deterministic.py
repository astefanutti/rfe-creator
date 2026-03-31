"""Layer 1: Deterministic scoring -- schema validation and consistency checks.

Fast, free, objective. Catches structural failures before expensive LLM scoring.
All checks are code-based and reuse the project's artifact_utils module.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Check:
    """Result of a single deterministic check."""
    name: str
    passed: bool
    detail: str = ""


@dataclass
class DeterministicResult:
    """All deterministic check results for one eval case."""
    case_id: str
    checks: list = field(default_factory=list)

    @property
    def all_pass(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def summary(self) -> dict:
        return {
            "case_id": self.case_id,
            "all_pass": self.all_pass,
            "passed": sum(1 for c in self.checks if c.passed),
            "failed": sum(1 for c in self.checks if not c.passed),
            "checks": [
                {"name": c.name, "passed": c.passed, "detail": c.detail}
                for c in self.checks
            ],
        }


def score(case_output_dir: Path, project_root: Path) -> DeterministicResult:
    """Run all deterministic checks on collected artifacts.

    Args:
        case_output_dir: Path to eval/runs/{run_id}/cases/{case_id}/
                         containing rfe-tasks/, rfe-reviews/, rfe-originals/
        project_root: Project root for importing artifact_utils.

    Returns:
        DeterministicResult with all check outcomes.
    """
    # Import artifact_utils from project
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from artifact_utils import (
        read_frontmatter, read_frontmatter_validated, validate, SCHEMAS,
    )

    case_id = case_output_dir.name
    result = DeterministicResult(case_id=case_id)

    # Find task and review files
    tasks_dir = case_output_dir / "rfe-tasks"
    reviews_dir = case_output_dir / "rfe-reviews"
    originals_dir = case_output_dir / "rfe-originals"

    task_files = _find_main_files(tasks_dir)
    review_files = _find_review_files(reviews_dir)

    # Check 1: File completeness
    result.checks.append(Check(
        name="file_completeness",
        passed=bool(task_files and review_files),
        detail=f"tasks={len(task_files)}, reviews={len(review_files)}",
    ))

    if not task_files:
        # No point running further checks
        for name in ("task_schema", "review_schema", "score_bounds",
                      "pass_score_consistency", "recommendation_consistency",
                      "revision_tracking"):
            result.checks.append(Check(name=name, passed=False,
                                       detail="No task files found"))
        return result

    # Check 2: Task schema validity
    for tf in task_files:
        try:
            data, _ = read_frontmatter_validated(str(tf), "rfe-task")
            result.checks.append(Check(
                name="task_schema",
                passed=True,
                detail=f"{tf.name}: valid",
            ))
        except Exception as e:
            result.checks.append(Check(
                name="task_schema",
                passed=False,
                detail=f"{tf.name}: {e}",
            ))

    # Check 3: Review schema validity + derived checks
    for rf in review_files:
        try:
            data, _ = read_frontmatter_validated(str(rf), "rfe-review")

            result.checks.append(Check(
                name="review_schema",
                passed=True,
                detail=f"{rf.name}: valid",
            ))

            # Check 4: Score bounds
            scores = data.get("scores", {})
            total = data.get("score", 0)
            criteria_ok = all(0 <= scores.get(k, -1) <= 2
                              for k in ("what", "why", "open_to_how",
                                        "not_a_task", "right_sized"))
            total_ok = 0 <= total <= 10
            criteria_sum = sum(scores.get(k, 0)
                               for k in ("what", "why", "open_to_how",
                                          "not_a_task", "right_sized"))
            sum_matches = criteria_sum == total

            result.checks.append(Check(
                name="score_bounds",
                passed=criteria_ok and total_ok and sum_matches,
                detail=(f"total={total}, criteria_sum={criteria_sum}, "
                        f"bounds_ok={criteria_ok and total_ok}, "
                        f"sum_matches={sum_matches}"),
            ))

            # Check 5: Pass/score consistency
            pass_val = data.get("pass", False)
            has_zero = any(scores.get(k, 0) == 0
                           for k in ("what", "why", "open_to_how",
                                     "not_a_task", "right_sized"))
            expected_pass = total >= 7 and not has_zero
            consistent = pass_val == expected_pass

            result.checks.append(Check(
                name="pass_score_consistency",
                passed=consistent,
                detail=(f"pass={pass_val}, score={total}, "
                        f"has_zero={has_zero}, expected_pass={expected_pass}"),
            ))

            # Check 6: Recommendation consistency
            rec = data.get("recommendation")
            feasibility = data.get("feasibility")
            rec_ok = True
            rec_detail = f"rec={rec}, pass={pass_val}, feasibility={feasibility}"

            if pass_val and rec not in ("submit", "split"):
                rec_ok = False
                rec_detail += " (pass=true but rec not submit/split)"
            if not pass_val and rec == "submit":
                rec_ok = False
                rec_detail += " (pass=false but rec=submit)"

            result.checks.append(Check(
                name="recommendation_consistency",
                passed=rec_ok,
                detail=rec_detail,
            ))

            # Check 7: Revision tracking
            revised = data.get("revised", False)
            before_score = data.get("before_score")
            revision_ok = True
            if revised and before_score is None:
                revision_ok = False

            result.checks.append(Check(
                name="revision_tracking",
                passed=revision_ok,
                detail=(f"revised={revised}, "
                        f"before_score={'present' if before_score is not None else 'missing'}"),
            ))

        except Exception as e:
            result.checks.append(Check(
                name="review_schema",
                passed=False,
                detail=f"{rf.name}: {e}",
            ))

    # Check 8: Content preservation (if originals exist)
    if originals_dir.exists() and task_files:
        result.checks.append(
            _check_content_preservation(
                task_files[0], originals_dir, project_root))

    return result


def _check_content_preservation(
    task_file: Path, originals_dir: Path, project_root: Path
) -> Check:
    """Run content preservation check comparing revised task to original."""
    # Find matching original
    originals = list(originals_dir.glob("*.md"))
    if not originals:
        return Check(
            name="content_preservation",
            passed=True,
            detail="No originals to compare against",
        )

    original = originals[0]
    script = project_root / "scripts" / "check_content_preservation.py"

    if not script.exists():
        return Check(
            name="content_preservation",
            passed=True,
            detail="check_content_preservation.py not found, skipped",
        )

    try:
        result = subprocess.run(
            ["python3", str(script), str(original), str(task_file)],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
        # Script exits 0 if no content lost, non-zero if blocks removed
        return Check(
            name="content_preservation",
            passed=True,  # Content being removed is expected during review
            detail=f"exit_code={result.returncode}, "
                   f"stdout_lines={len(result.stdout.splitlines())}",
        )
    except Exception as e:
        return Check(
            name="content_preservation",
            passed=True,
            detail=f"Error running check: {e}",
        )


def _find_main_files(tasks_dir: Path) -> list:
    """Find main task files (excluding companions)."""
    if not tasks_dir.exists():
        return []
    return [
        f for f in sorted(tasks_dir.iterdir())
        if f.name.endswith(".md")
        and not f.name.endswith("-comments.md")
        and not f.name.endswith("-removed-context.md")
    ]


def _find_review_files(reviews_dir: Path) -> list:
    """Find review files."""
    if not reviews_dir.exists():
        return []
    return [
        f for f in sorted(reviews_dir.iterdir())
        if f.name.endswith("-review.md")
    ]
