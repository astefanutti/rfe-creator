"""Report generation -- CLI text and HTML reports."""

import difflib
import json
from pathlib import Path
from typing import Optional


def print_text_report(summary: dict, comparison: Optional[dict] = None):
    """Print a concise CLI text report."""
    meta = summary.get("metadata", {})
    print(f"\nRFE Creator Eval — {meta.get('model', '?')} "
          f"via {meta.get('runner', '?')}")
    print(f"Dataset: {meta.get('dataset', '?')} "
          f"({meta.get('cases_total', '?')} cases) | "
          f"Run: {meta.get('run_id', '?')}")
    print()

    # Deterministic
    det = summary.get("deterministic", {})
    det_pass = det.get("total_passed", 0)
    det_total = det.get("total_cases", 0)
    det_ok = det_pass == det_total
    _print_metric("DETERMINISTIC", f"{det_pass}/{det_total} pass", det_ok)

    # Reference
    ref = summary.get("reference", {})
    if ref.get("status") == "skip":
        _print_metric("REFERENCE", "skipped (no annotations)", None)
    else:
        _print_metric(
            "SCORE ACCURACY",
            f"mean deviation {ref.get('mean_score_deviation', '?')} "
            f"(threshold: {ref.get('max_score_deviation_threshold', '?')})",
            ref.get("status") != "fail",
        )
        _print_metric(
            "RECOMMENDATION MATCH",
            f"{_pct(ref.get('recommendation_match_rate'))} "
            f"(threshold: {_pct(ref.get('recommendation_match_threshold'))})",
            ref.get("recommendation_match_rate", 1) >=
            ref.get("recommendation_match_threshold", 0),
        )
        _print_metric(
            "FEASIBILITY MATCH",
            f"{_pct(ref.get('feasibility_match_rate'))} "
            f"(threshold: {_pct(ref.get('feasibility_match_threshold'))})",
            ref.get("feasibility_match_rate", 1) >=
            ref.get("feasibility_match_threshold", 0),
        )

    # LLM Judge
    judge = summary.get("llm_judge", {})
    if judge.get("status") == "skip":
        _print_metric("LLM JUDGE", "skipped", None)
    else:
        _print_metric(
            "JUDGE MEAN",
            f"{judge.get('mean_score', '?')} "
            f"(threshold: {judge.get('mean_score_threshold', '?')})",
            judge.get("status") != "fail",
        )
        _print_metric(
            "CALIBRATION",
            f"{judge.get('calibration_mean', '?')} "
            f"(threshold: {judge.get('calibration_threshold', '?')})",
            judge.get("calibration_mean", 0) >=
            judge.get("calibration_threshold", 0),
        )

    # Regressions
    regressions = summary.get("regressions", [])
    print()
    if regressions:
        print(f"REGRESSIONS: {len(regressions)} detected")
        for r in regressions:
            print(f"  - [{r.get('case_id')}] {r.get('metric')}: "
                  f"{r.get('baseline_value')} -> {r.get('current_value')}")
    else:
        baseline = summary.get("baseline_run")
        if baseline:
            print(f"REGRESSIONS vs {baseline}: 0")
        else:
            print("REGRESSIONS: no baseline to compare")

    # Pairwise comparison
    if comparison:
        print()
        a = comparison.get("run_a", "A")
        b = comparison.get("run_b", "B")
        print(f"Pairwise: {a} wins {comparison.get('wins_a', 0)}, "
              f"{b} wins {comparison.get('wins_b', 0)}, "
              f"tie {comparison.get('ties', 0)}")

    print()


def generate_html_report(summary: dict, output_path: Path,
                         comparison: Optional[dict] = None,
                         current_run_dir: Optional[Path] = None,
                         baseline_run_dir: Optional[Path] = None):
    """Generate an HTML report file."""
    meta = summary.get("metadata", {})
    det = summary.get("deterministic", {})
    ref = summary.get("reference", {})
    judge = summary.get("llm_judge", {})
    regressions = summary.get("regressions", [])

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>RFE Creator Eval — {meta.get('run_id', '?')}</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #1a1a1a; }}
h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.3em; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
.pass {{ color: #16a34a; font-weight: bold; }}
.fail {{ color: #dc2626; font-weight: bold; }}
.skip {{ color: #9ca3af; }}
.metric-row td:last-child {{ font-family: monospace; }}
.diff {{ font-family: monospace; font-size: 0.85em; white-space: pre-wrap; background: #f8f8f8; padding: 1em; border: 1px solid #ddd; border-radius: 4px; overflow-x: auto; }}
.diff .add {{ background: #d4edda; }}
.diff .del {{ background: #f8d7da; }}
.diff .hdr {{ color: #6c757d; font-weight: bold; }}
details {{ margin: 0.5em 0; }}
summary {{ cursor: pointer; font-weight: bold; padding: 0.3em 0; }}
</style>
</head>
<body>
<h1>RFE Creator Eval Report</h1>
<table>
<tr><th>Run ID</th><td>{meta.get('run_id', '?')}</td></tr>
<tr><th>Runner</th><td>{meta.get('runner', '?')}</td></tr>
<tr><th>Model</th><td>{meta.get('model', '?')}</td></tr>
<tr><th>Date</th><td>{meta.get('date', '?')}</td></tr>
<tr><th>Cases</th><td>{meta.get('cases_total', '?')}</td></tr>
</table>

<h2>Scoring Summary</h2>
<table>
<tr><th>Layer</th><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
<tr class="metric-row">
  <td>Deterministic</td><td>All pass</td>
  <td>{det.get('total_passed', 0)}/{det.get('total_cases', 0)}</td>
  <td>all</td>
  <td class="{'pass' if det.get('total_passed') == det.get('total_cases') else 'fail'}">
    {'PASS' if det.get('total_passed') == det.get('total_cases') else 'FAIL'}</td>
</tr>"""

    if ref.get("status") != "skip":
        ref_status = "pass" if ref.get("status") != "fail" else "fail"
        html += f"""
<tr class="metric-row">
  <td>Reference</td><td>Score deviation</td>
  <td>{ref.get('mean_score_deviation', '?')}</td>
  <td>&le; {ref.get('max_score_deviation_threshold', '?')}</td>
  <td class="{ref_status}">{'PASS' if ref_status == 'pass' else 'FAIL'}</td>
</tr>
<tr class="metric-row">
  <td></td><td>Recommendation match</td>
  <td>{_pct(ref.get('recommendation_match_rate'))}</td>
  <td>&ge; {_pct(ref.get('recommendation_match_threshold'))}</td>
  <td class="{ref_status}">{'PASS' if ref.get('recommendation_match_rate', 1) >= ref.get('recommendation_match_threshold', 0) else 'FAIL'}</td>
</tr>"""

    if judge.get("status") != "skip":
        j_status = "pass" if judge.get("status") != "fail" else "fail"
        html += f"""
<tr class="metric-row">
  <td>LLM Judge</td><td>Mean score</td>
  <td>{judge.get('mean_score', '?')}</td>
  <td>&ge; {judge.get('mean_score_threshold', '?')}</td>
  <td class="{j_status}">{'PASS' if j_status == 'pass' else 'FAIL'}</td>
</tr>
<tr class="metric-row">
  <td></td><td>Calibration</td>
  <td>{judge.get('calibration_mean', '?')}</td>
  <td>&ge; {judge.get('calibration_threshold', '?')}</td>
  <td class="{j_status}">{'PASS' if judge.get('calibration_mean', 0) >= judge.get('calibration_threshold', 0) else 'FAIL'}</td>
</tr>"""

    html += "\n</table>"

    if regressions:
        html += "\n<h2>Regressions</h2>\n<table>\n"
        html += "<tr><th>Case</th><th>Metric</th><th>Baseline</th><th>Current</th></tr>\n"
        for r in regressions:
            html += (f"<tr><td>{r.get('case_id')}</td><td>{r.get('metric')}</td>"
                     f"<td>{r.get('baseline_value')}</td>"
                     f"<td class='fail'>{r.get('current_value')}</td></tr>\n")
        html += "</table>"

    if comparison:
        html += f"""
<h2>Pairwise Comparison</h2>
<p><strong>{comparison.get('run_a')}</strong> vs <strong>{comparison.get('run_b')}</strong></p>
<table>
<tr><th>{comparison.get('run_a')}</th><th>{comparison.get('run_b')}</th><th>Tie</th></tr>
<tr><td>{comparison.get('wins_a', 0)}</td><td>{comparison.get('wins_b', 0)}</td><td>{comparison.get('ties', 0)}</td></tr>
</table>"""

    # Per-case artifact diffs (current vs baseline)
    if current_run_dir and baseline_run_dir:
        cases_dir = current_run_dir / "cases"
        baseline_cases = baseline_run_dir / "cases"
        if cases_dir.exists() and baseline_cases.exists():
            html += "\n<h2>Per-Case Artifact Diffs</h2>\n"
            html += (f"<p>Comparing <strong>{current_run_dir.name}</strong> "
                     f"vs <strong>{baseline_run_dir.name}</strong></p>\n")

            for case_dir in sorted(cases_dir.iterdir()):
                if not case_dir.is_dir():
                    continue
                baseline_case = baseline_cases / case_dir.name
                if not baseline_case.exists():
                    continue

                case_diffs = _generate_case_diffs(case_dir, baseline_case)
                if not case_diffs:
                    continue

                html += f"<details><summary>{case_dir.name}</summary>\n"
                for filename, diff_html in case_diffs:
                    html += (f"<details><summary>{filename}</summary>\n"
                             f"<div class='diff'>{diff_html}</div>\n"
                             f"</details>\n")
                html += "</details>\n"

    html += "\n</body>\n</html>\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)


def _print_metric(name: str, value: str, passed: Optional[bool]):
    if passed is None:
        status = " "
    elif passed:
        status = "v"
    else:
        status = "X"
    print(f"  [{status}] {name}: {value}")


def _pct(val) -> str:
    if val is None:
        return "?"
    return f"{val * 100:.0f}%" if isinstance(val, float) else str(val)


def _generate_case_diffs(current_case: Path, baseline_case: Path) -> list:
    """Generate diffs for all artifacts in a case. Returns [(filename, html)]."""
    diffs = []
    # Compare rfe-tasks and rfe-reviews subdirectories
    for subdir in ("rfe-tasks", "rfe-reviews"):
        curr_dir = current_case / subdir
        base_dir = baseline_case / subdir
        if not curr_dir.exists() or not base_dir.exists():
            continue

        # Match files by name
        curr_files = {f.name: f for f in curr_dir.iterdir()
                      if f.name.endswith(".md")}
        base_files = {f.name: f for f in base_dir.iterdir()
                      if f.name.endswith(".md")}

        all_names = sorted(set(curr_files) | set(base_files))
        for name in all_names:
            curr_text = curr_files[name].read_text() if name in curr_files else ""
            base_text = base_files[name].read_text() if name in base_files else ""

            if curr_text == base_text:
                continue

            diff_html = _unified_diff_html(
                base_text, curr_text,
                fromfile=f"baseline/{subdir}/{name}",
                tofile=f"current/{subdir}/{name}",
            )
            if diff_html:
                diffs.append((f"{subdir}/{name}", diff_html))

    return diffs


def _unified_diff_html(a: str, b: str, fromfile: str = "", tofile: str = "") -> str:
    """Generate HTML-formatted unified diff."""
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile,
                                lineterm="")
    lines = []
    for line in diff:
        line = line.rstrip("\n")
        escaped = (line.replace("&", "&amp;")
                       .replace("<", "&lt;")
                       .replace(">", "&gt;"))
        if line.startswith("+++") or line.startswith("---"):
            lines.append(f'<span class="hdr">{escaped}</span>')
        elif line.startswith("@@"):
            lines.append(f'<span class="hdr">{escaped}</span>')
        elif line.startswith("+"):
            lines.append(f'<span class="add">{escaped}</span>')
        elif line.startswith("-"):
            lines.append(f'<span class="del">{escaped}</span>')
        else:
            lines.append(escaped)

    return "\n".join(lines)
