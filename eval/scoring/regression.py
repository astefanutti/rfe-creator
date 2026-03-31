"""Regression detection -- compare runs against thresholds and baselines.

Flags score drops, recommendation flips, and new failures when comparing
a current run to a baseline run or absolute thresholds.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Regression:
    """A single detected regression."""
    case_id: str
    metric: str
    baseline_value: str
    current_value: str
    detail: str = ""


def detect(
    current_summary: dict,
    baseline_summary: Optional[dict],
    thresholds_path: Path,
) -> list:
    """Detect regressions between current run and baseline.

    Args:
        current_summary: Summary dict from current run (summary.yaml).
        baseline_summary: Summary dict from baseline run (None = threshold-only).
        thresholds_path: Path to config/thresholds.yaml.

    Returns:
        List of Regression objects.
    """
    with open(thresholds_path) as f:
        thresholds = yaml.safe_load(f) or {}

    regressions = []

    # Threshold-based checks (absolute)
    regressions.extend(_check_deterministic(current_summary, thresholds))
    regressions.extend(_check_reference(current_summary, thresholds))
    regressions.extend(_check_judge(current_summary, thresholds))

    # Baseline-relative checks
    if baseline_summary:
        regressions.extend(_check_vs_baseline(current_summary, baseline_summary))

    return regressions


def _check_deterministic(summary: dict, thresholds: dict) -> list:
    regressions = []
    det = summary.get("deterministic", {})
    thresh = thresholds.get("deterministic", {})

    if thresh.get("all_pass", True):
        failed_cases = [c for c in det.get("cases", [])
                        if not c.get("all_pass", True)]
        if failed_cases:
            regressions.append(Regression(
                case_id="aggregate",
                metric="deterministic.all_pass",
                baseline_value="true",
                current_value=f"{len(failed_cases)} failures",
                detail=", ".join(c.get("case_id", "?") for c in failed_cases),
            ))

    return regressions


def _check_reference(summary: dict, thresholds: dict) -> list:
    regressions = []
    ref = summary.get("reference", {})
    thresh = thresholds.get("reference", {})

    if ref.get("status") == "skip":
        return regressions

    mean_dev = ref.get("mean_score_deviation", 0)
    max_dev = thresh.get("max_score_deviation", 2)
    if mean_dev > max_dev:
        regressions.append(Regression(
            case_id="aggregate",
            metric="reference.mean_score_deviation",
            baseline_value=f"<= {max_dev}",
            current_value=str(mean_dev),
        ))

    rec_rate = ref.get("recommendation_match_rate", 1.0)
    min_rec = thresh.get("min_recommendation_match_rate", 0.8)
    if rec_rate < min_rec:
        regressions.append(Regression(
            case_id="aggregate",
            metric="reference.recommendation_match_rate",
            baseline_value=f">= {min_rec}",
            current_value=str(rec_rate),
        ))

    feas_rate = ref.get("feasibility_match_rate", 1.0)
    min_feas = thresh.get("min_feasibility_match_rate", 0.9)
    if feas_rate < min_feas:
        regressions.append(Regression(
            case_id="aggregate",
            metric="reference.feasibility_match_rate",
            baseline_value=f">= {min_feas}",
            current_value=str(feas_rate),
        ))

    return regressions


def _check_judge(summary: dict, thresholds: dict) -> list:
    regressions = []
    judge = summary.get("llm_judge", {})
    thresh = thresholds.get("llm_judge", {})

    if judge.get("status") == "skip":
        return regressions

    mean = judge.get("mean_score", 0)
    min_mean = thresh.get("min_mean_score", 3.5)
    if mean < min_mean:
        regressions.append(Regression(
            case_id="aggregate",
            metric="llm_judge.mean_score",
            baseline_value=f">= {min_mean}",
            current_value=str(mean),
        ))

    cal = judge.get("calibration_mean", 0)
    min_cal = thresh.get("min_calibration_accuracy", 3.0)
    if cal < min_cal:
        regressions.append(Regression(
            case_id="aggregate",
            metric="llm_judge.calibration_accuracy",
            baseline_value=f">= {min_cal}",
            current_value=str(cal),
        ))

    return regressions


def _check_vs_baseline(current: dict, baseline: dict) -> list:
    """Compare per-case scores between runs to find regressions."""
    regressions = []

    current_cases = {c["case_id"]: c
                     for c in current.get("reference", {}).get("per_case", [])}
    baseline_cases = {c["case_id"]: c
                      for c in baseline.get("reference", {}).get("per_case", [])}

    for case_id, curr in current_cases.items():
        base = baseline_cases.get(case_id)
        if not base:
            continue

        # Score dropped significantly
        curr_dev_raw = curr.get("score_deviation")
        base_dev_raw = base.get("score_deviation")
        if curr_dev_raw is None or base_dev_raw is None:
            continue
        curr_dev = abs(curr_dev_raw)
        base_dev = abs(base_dev_raw)
        if curr_dev > base_dev + 2:
            regressions.append(Regression(
                case_id=case_id,
                metric="score_deviation",
                baseline_value=str(base_dev),
                current_value=str(curr_dev),
                detail="Score accuracy degraded vs baseline",
            ))

        # Recommendation flipped in wrong direction
        base_rec = base.get("recommendation_match")
        curr_rec = curr.get("recommendation_match")
        if base_rec is True and curr_rec is False:
            regressions.append(Regression(
                case_id=case_id,
                metric="recommendation_match",
                baseline_value="match",
                current_value="mismatch",
                detail="Recommendation flipped vs baseline",
            ))

    return regressions
