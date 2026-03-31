"""Prepare an isolated workspace for a single eval case.

Creates a temporary directory with pre-staged artifacts and symlinks to
project scripts/skills, so any agent runner can execute skills against it.

Usage:
    python3 eval/scripts/prepare_workspace.py \\
        --case eval/dataset/cases/case-001-slug \\
        --run-id 2026-03-30-opus \\
        --project-root /path/to/rfe-creator
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def prepare(case_dir: Path, run_id: str, project_root: Path,
            output_dir: Path = None) -> Path:
    """Set up an isolated workspace for one eval case.

    Supports two pipeline modes:
    - rfe.review: pre-stages artifacts from rfe_content (existing behavior)
    - rfe.speedrun: empty workspace — skill creates everything from scratch;
      rfe_content saved as ground_truth.md in the output dir for comparison.

    Args:
        case_dir: Path to eval/dataset/cases/case-NNN-slug/
        run_id: Unique identifier for this eval run
        project_root: Path to rfe-creator project root
        output_dir: Where to save ground truth (for rfe.speedrun mode)

    Returns:
        Path to the prepared workspace directory.
    """
    input_path = case_dir / "input.yaml"
    if not input_path.exists():
        raise FileNotFoundError(f"No input.yaml in {case_dir}")

    with open(input_path) as f:
        input_data = yaml.safe_load(f)

    rfe_id = input_data["rfe_id"]
    case_id = case_dir.name
    pipeline = input_data.get("pipeline", "rfe.review")

    # Create workspace
    workspace = Path(f"/tmp/rfe-eval/{run_id}/{case_id}")
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)

    # Create artifact directories
    (workspace / "artifacts" / "rfe-tasks").mkdir(parents=True)
    (workspace / "artifacts" / "rfe-reviews").mkdir(parents=True)

    # Create workspace-local rfe-assess directory to avoid /tmp/rfe-assess collisions
    (workspace / "rfe-assess" / "single").mkdir(parents=True)

    if pipeline == "rfe.review":
        # Pre-stage artifacts for review-only mode
        (workspace / "artifacts" / "rfe-originals").mkdir(parents=True)

        if rfe_id.startswith("RHAIRFE-"):
            task_filename = f"{rfe_id}.md"
        else:
            slug = input_data.get("slug", "eval")
            task_filename = f"{rfe_id}-{slug}.md"

        task_path = workspace / "artifacts" / "rfe-tasks" / task_filename
        _write_task_file(task_path, input_data, project_root)

        original_path = workspace / "artifacts" / "rfe-originals" / task_filename
        _write_original_file(original_path, input_data)

        comments = input_data.get("comments")
        if comments:
            comment_stem = task_filename.replace(".md", "")
            comment_path = (workspace / "artifacts" / "rfe-tasks" /
                            f"{comment_stem}-comments.md")
            comment_path.write_text(comments, encoding="utf-8")

    elif pipeline == "rfe.speedrun":
        # Empty workspace — skill creates everything from scratch
        # Save ground truth for later comparison
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            gt_path = output_dir / "ground_truth.md"
            rfe_content = input_data.get("rfe_content", "")
            gt_path.write_text(rfe_content, encoding="utf-8")

    # Symlink project resources into workspace
    _create_symlinks(workspace, project_root)

    return workspace


def _write_task_file(path: Path, input_data: dict, project_root: Path):
    """Write the pre-staged RFE task file using frontmatter.py for validation."""
    rfe_content = input_data.get("rfe_content", "")

    # Write body first
    path.write_text(rfe_content, encoding="utf-8")

    # Use frontmatter.py to set validated frontmatter
    frontmatter_script = project_root / "scripts" / "frontmatter.py"
    fields = [
        f"rfe_id={input_data['rfe_id']}",
        f"title={input_data['title']}",
        f"priority={input_data.get('priority', 'Normal')}",
        f"status={input_data.get('status', 'Ready')}",
    ]
    if input_data.get("size"):
        fields.append(f"size={input_data['size']}")

    result = subprocess.run(
        ["python3", str(frontmatter_script), "set", str(path)] + fields,
        capture_output=True, text=True,
        cwd=str(project_root),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"frontmatter.py set failed: {result.stderr}")


def _write_original_file(path: Path, input_data: dict):
    """Write the raw RFE content as the original snapshot (no frontmatter)."""
    rfe_content = input_data.get("rfe_content", "")
    path.write_text(rfe_content, encoding="utf-8")


def _create_symlinks(workspace: Path, project_root: Path):
    """Symlink project resources into the workspace."""
    symlinks = {
        "scripts": project_root / "scripts",
        ".claude": project_root / ".claude",
        "CLAUDE.md": project_root / "CLAUDE.md",
    }

    # Also symlink .context if it exists (architecture context, assess-rfe)
    context_dir = project_root / ".context"
    if context_dir.exists():
        symlinks[".context"] = context_dir

    for name, target in symlinks.items():
        link = workspace / name
        if target.exists():
            link.symlink_to(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", required=True,
                        help="Path to case directory")
    parser.add_argument("--run-id", required=True,
                        help="Unique run identifier")
    parser.add_argument("--project-root", default=None,
                        help="Project root (default: auto-detect)")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else \
        Path(__file__).resolve().parent.parent.parent

    workspace = prepare(
        case_dir=Path(args.case),
        run_id=args.run_id,
        project_root=project_root,
    )
    print(workspace)


if __name__ == "__main__":
    main()
