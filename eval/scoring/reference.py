"""Layer 2: Reference-based scoring -- compare against human annotations.

Compares pipeline output scores against expected values from annotations.yaml.
Pure Python, no LLM calls.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


CRITERIA = ("what", "why", "open_to_how", "not_a_task", "right_sized")


@dataclass
class ReferenceResult:
    """Reference comparison result for one eval case."""
    case_id: str
    has_annotations: bool = False
    score_deviation: Optional[int] = None
    criterion_deviations: dict = field(default_factory=dict)
    recommendation_match: Optional[bool] = None
    feasibility_match: Optional[bool] = None
    within_tolerance: bool = True
    detail: str = ""

    @property
    def summary(self) -> dict:
        return {
            "case_id": self.case_id,
            "has_annotations": self.has_annotations,
            "score_deviation": self.score_deviation,
            "criterion_deviations": self.criterion_deviations,
            "recommendation_match": self.recommendation_match,
            "feasibility_match": self.feasibility_match,
            "within_tolerance": self.within_tolerance,
            "detail": self.detail,
        }


def score(
    case_output_dir: Path,
    case_dataset_dir: Path,
    project_root: Path,
) -> ReferenceResult:
    """Compare pipeline output against human annotations.

    Args:
        case_output_dir: eval/runs/{run_id}/cases/{case_id}/ with collected artifacts.
        case_dataset_dir: eval/dataset/cases/{case_id}/ with annotations.yaml.
        project_root: For importing artifact_utils.

    Returns:
        ReferenceResult with deviation metrics.
    """
    case_id = case_output_dir.name
    result = ReferenceResult(case_id=case_id)

    # Load annotations
    annotations_path = case_dataset_dir / "annotations.yaml"
    if not annotations_path.exists():
        result.detail = "No annotations.yaml found"
        return result

    with open(annotations_path) as f:
        annotations = yaml.safe_load(f) or {}

    expected_total = annotations.get("expected_total")
    if expected_total is None:
        result.detail = "Annotations not yet filled (expected_total is null)"
        return result

    result.has_annotations = True
    tolerance = annotations.get("score_tolerance", 1)

    # Import artifact_utils
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from artifact_utils import read_frontmatter_validated

    # Find and parse review file
    reviews_dir = case_output_dir / "rfe-reviews"
    review_data = _load_review(reviews_dir, project_root)
    if review_data is None:
        result.detail = "No valid review file found"
        result.within_tolerance = False
        return result

    # Score deviation
    actual_total = review_data.get("score", 0)
    result.score_deviation = actual_total - expected_total

    # Per-criterion deviations
    expected_scores = annotations.get("expected_scores", {})
    actual_scores = review_data.get("scores", {})
    for criterion in CRITERIA:
        expected = expected_scores.get(criterion)
        actual = actual_scores.get(criterion)
        if expected is not None and actual is not None:
            result.criterion_deviations[criterion] = actual - expected

    # Recommendation match
    expected_rec = annotations.get("expected_recommendation")
    if expected_rec:
        actual_rec = review_data.get("recommendation")
        result.recommendation_match = actual_rec == expected_rec

    # Feasibility match
    expected_feas = annotations.get("expected_feasibility")
    if expected_feas:
        actual_feas = review_data.get("feasibility")
        result.feasibility_match = actual_feas == expected_feas

    # Check tolerance
    if abs(result.score_deviation) > tolerance:
        result.within_tolerance = False
        result.detail = (f"Score deviation {result.score_deviation} "
                         f"exceeds tolerance {tolerance}")
    else:
        result.detail = f"Within tolerance (deviation={result.score_deviation})"

    # Check per-criterion tolerance
    for criterion, dev in result.criterion_deviations.items():
        if abs(dev) > tolerance:
            result.within_tolerance = False

    return result


def aggregate(results: list, thresholds: dict) -> dict:
    """Aggregate reference results across all cases.

    Args:
        results: List of ReferenceResult objects.
        thresholds: From config/thresholds.yaml reference section.

    Returns:
        Aggregate summary with pass/fail status.
    """
    annotated = [r for r in results if r.has_annotations]
    if not annotated:
        return {
            "status": "skip",
            "reason": "No annotated cases",
            "cases": len(results),
            "annotated": 0,
        }

    deviations = [abs(r.score_deviation) for r in annotated
                  if r.score_deviation is not None]
    mean_deviation = sum(deviations) / len(deviations) if deviations else 0

    rec_matches = [r.recommendation_match for r in annotated
                   if r.recommendation_match is not None]
    rec_rate = sum(rec_matches) / len(rec_matches) if rec_matches else 1.0

    feas_matches = [r.feasibility_match for r in annotated
                    if r.feasibility_match is not None]
    feas_rate = sum(feas_matches) / len(feas_matches) if feas_matches else 1.0

    max_dev = thresholds.get("max_score_deviation", 2)
    min_rec = thresholds.get("min_recommendation_match_rate", 0.8)
    min_feas = thresholds.get("min_feasibility_match_rate", 0.9)

    passed = (
        mean_deviation <= max_dev
        and rec_rate >= min_rec
        and feas_rate >= min_feas
    )

    return {
        "status": "pass" if passed else "fail",
        "cases": len(results),
        "annotated": len(annotated),
        "mean_score_deviation": round(mean_deviation, 2),
        "max_score_deviation_threshold": max_dev,
        "recommendation_match_rate": round(rec_rate, 3),
        "recommendation_match_threshold": min_rec,
        "feasibility_match_rate": round(feas_rate, 3),
        "feasibility_match_threshold": min_feas,
        "cases_within_tolerance": sum(1 for r in annotated if r.within_tolerance),
    }


def _load_review(reviews_dir: Path, project_root: Path) -> Optional[dict]:
    """Load the first valid review file from the reviews directory."""
    if not reviews_dir.exists():
        return None

    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from artifact_utils import read_frontmatter_validated

    for f in sorted(reviews_dir.iterdir()):
        if f.name.endswith("-review.md"):
            try:
                data, _ = read_frontmatter_validated(str(f), "rfe-review")
                return data
            except Exception:
                continue
    return None
