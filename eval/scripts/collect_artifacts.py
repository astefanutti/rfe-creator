"""Collect artifacts from a workspace after a skill run.

Agent-agnostic: reads whatever artifacts the runner produced, parses
frontmatter, and copies results to the eval run directory.

Usage:
    python3 eval/scripts/collect_artifacts.py \\
        --workspace /tmp/rfe-eval/run-id/case-001 \\
        --output eval/runs/run-id/cases/case-001
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def collect(workspace: Path, output_dir: Path, project_root: Path) -> dict:
    """Harvest artifacts from workspace and store in output directory.

    Args:
        workspace: The workspace directory where the skill ran.
        output_dir: Where to store collected artifacts.
        project_root: Project root for importing artifact_utils.

    Returns:
        dict with collected artifact metadata.
    """
    # Add project scripts to path for artifact_utils import
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from artifact_utils import (
        read_frontmatter, read_frontmatter_validated,
        scan_task_files, scan_review_files,
    )

    artifacts_dir = workspace / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "tasks": [],
        "reviews": [],
        "removed_context": [],
        "files_copied": [],
    }

    # Copy artifact subdirectories
    for subdir in ("rfe-tasks", "rfe-originals", "rfe-reviews"):
        src = artifacts_dir / subdir
        dst = output_dir / subdir
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            result["files_copied"].extend(
                str(p.relative_to(output_dir))
                for p in dst.rglob("*") if p.is_file()
            )

    # Parse task frontmatter
    if (output_dir / "rfe-tasks").exists():
        for filename in sorted((output_dir / "rfe-tasks").iterdir()):
            if not filename.name.endswith(".md"):
                continue
            if _is_companion(filename.name):
                continue
            try:
                data, body = read_frontmatter_validated(
                    str(filename), "rfe-task")
                result["tasks"].append({
                    "file": filename.name,
                    "frontmatter": data,
                })
            except Exception as e:
                result["tasks"].append({
                    "file": filename.name,
                    "error": str(e),
                })

    # Parse review frontmatter
    if (output_dir / "rfe-reviews").exists():
        for filename in sorted((output_dir / "rfe-reviews").iterdir()):
            if not filename.name.endswith("-review.md"):
                continue
            try:
                data, body = read_frontmatter_validated(
                    str(filename), "rfe-review")
                result["reviews"].append({
                    "file": filename.name,
                    "frontmatter": data,
                })
            except Exception as e:
                result["reviews"].append({
                    "file": filename.name,
                    "error": str(e),
                })

    # Collect removed-context files
    if (output_dir / "rfe-tasks").exists():
        for filename in sorted((output_dir / "rfe-tasks").iterdir()):
            if filename.name.endswith("-removed-context.yaml"):
                import yaml
                try:
                    with open(filename) as f:
                        ctx = yaml.safe_load(f)
                    result["removed_context"].append({
                        "file": filename.name,
                        "data": ctx,
                    })
                except Exception as e:
                    result["removed_context"].append({
                        "file": filename.name,
                        "error": str(e),
                    })

    # Write collection summary
    summary_path = output_dir / "collected.json"
    with open(summary_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    return result


def _is_companion(filename: str) -> bool:
    return (filename.endswith("-comments.md") or
            filename.endswith("-removed-context.md") or
            filename.endswith("-removed-context.yaml"))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", required=True,
                        help="Workspace directory")
    parser.add_argument("--output", required=True,
                        help="Output directory for collected artifacts")
    parser.add_argument("--project-root", default=None,
                        help="Project root (default: auto-detect)")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else \
        Path(__file__).resolve().parent.parent.parent

    result = collect(
        workspace=Path(args.workspace),
        output_dir=Path(args.output),
        project_root=project_root,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
