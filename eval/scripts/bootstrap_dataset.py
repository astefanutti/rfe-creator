#!/usr/bin/env python3
"""Bootstrap an evaluation dataset from existing RHAIRFE Jira issues.

Fetches issues by explicit keys or JQL discovery, converts them into
eval case directories with input.yaml and skeleton annotations.

Usage:
    # Fetch specific issues
    python3 eval/scripts/bootstrap_dataset.py --keys RHAIRFE-1109 RHAIRFE-1234

    # Discover recent issues via JQL
    python3 eval/scripts/bootstrap_dataset.py --jql "project = RHAIRFE ORDER BY created DESC" --limit 30

    # Both: discover then interactively select
    python3 eval/scripts/bootstrap_dataset.py --jql "project = RHAIRFE ORDER BY created DESC" --limit 30 --interactive

Environment variables:
    JIRA_SERVER  Jira server URL
    JIRA_USER    Jira username/email
    JIRA_TOKEN   Jira API token
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

# Add project scripts to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


def _load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

from jira_utils import (
    require_env, api_call_with_retry, get_issue, get_comments,
    adf_to_markdown,
)


DATASET_DIR = PROJECT_ROOT / "eval" / "dataset"
CASES_DIR = DATASET_DIR / "cases"


def search_jql(server, user, token, jql, max_results=50):
    """Search Jira issues by JQL query, using cursor-based pagination."""
    import urllib.parse
    issues = []
    page_size = min(max_results, 100)
    next_page_token = None

    while len(issues) < max_results:
        params = {
            "jql": jql,
            "maxResults": page_size,
            "fields": "summary,priority,status,labels,description",
        }
        if next_page_token:
            params["nextPageToken"] = next_page_token

        path = f"/search/jql?{urllib.parse.urlencode(params)}"
        result = api_call_with_retry(server, path, user, token)
        batch = result.get("issues", [])
        issues.extend(batch)
        print(f"  Fetched {len(issues)}...", flush=True)

        next_page_token = result.get("nextPageToken")
        is_last = result.get("isLast", True)
        if not batch or is_last or not next_page_token:
            break

    return issues[:max_results]


def fetch_case_data(server, user, token, issue_key):
    """Fetch all data needed for an eval case from a Jira issue."""
    issue = get_issue(server, user, token, issue_key,
                      fields=["summary", "description", "priority",
                              "labels", "status"])
    fields = issue.get("fields", {})

    # Convert description
    description = fields.get("description")
    if isinstance(description, dict):
        description_md = adf_to_markdown(description).strip()
    elif isinstance(description, str):
        description_md = description.strip()
    else:
        description_md = ""

    # Fetch comments
    comments_raw = get_comments(server, user, token, issue_key)
    comments_md = ""
    if comments_raw:
        lines = [f"# Comments: {issue_key}", ""]
        for c in comments_raw:
            author = c.get("author", {}).get("displayName", "Unknown")
            created = c.get("created", "")[:10]
            body = c.get("body", {})
            if isinstance(body, dict):
                body = adf_to_markdown(body).strip()
            lines.append(f"## {author} \u2014 {created}")
            lines.append(body)
            lines.append("")
        comments_md = "\n".join(lines)

    # Determine priority
    priority_obj = fields.get("priority")
    priority = "Normal"
    if isinstance(priority_obj, dict):
        priority = priority_obj.get("name", "Normal")

    # Estimate size from description length
    desc_len = len(description_md)
    if desc_len < 500:
        size = "S"
    elif desc_len < 1500:
        size = "M"
    elif desc_len < 3000:
        size = "L"
    else:
        size = "XL"

    return {
        "key": issue_key,
        "title": fields.get("summary", "Untitled"),
        "priority": priority,
        "size": size,
        "description_md": description_md,
        "comments_md": comments_md,
        "labels": fields.get("labels", []),
        "status": fields.get("status", {}).get("name", "Unknown"),
    }


def slugify(text, max_len=40):
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text[:max_len].rstrip('-')


def create_case(case_num, data):
    """Create an eval case directory from fetched Jira data."""
    slug = slugify(data["title"])
    case_id = f"case-{case_num:03d}-{slug}"
    case_dir = CASES_DIR / case_id

    case_dir.mkdir(parents=True, exist_ok=True)

    # Write input.yaml
    input_data = {
        "pipeline": "rfe.review",
        "input_type": "jira_snapshot",
        "rfe_id": data["key"],
        "title": data["title"],
        "priority": data["priority"],
        "size": data["size"],
        "status": "Ready",
        "source_jira_status": data["status"],
        "source_labels": data["labels"],
        "rfe_content": data["description_md"],
    }
    if data["comments_md"]:
        input_data["comments"] = data["comments_md"]

    input_path = case_dir / "input.yaml"
    with open(input_path, "w") as f:
        yaml.dump(input_data, f, default_flow_style=False, allow_unicode=True,
                  width=120, sort_keys=False)

    # Write skeleton annotations
    annotations = {
        "expected_scores": {
            "what": None,
            "why": None,
            "open_to_how": None,
            "not_a_task": None,
            "right_sized": None,
        },
        "expected_total": None,
        "expected_pass": None,
        "expected_recommendation": None,
        "expected_feasibility": None,
        "known_issues": [],
        "score_tolerance": 1,
        "tags": [],
        "difficulty": None,
    }
    annotations_path = case_dir / "annotations.yaml"
    with open(annotations_path, "w") as f:
        yaml.dump(annotations, f, default_flow_style=False, sort_keys=False)

    return case_id


def update_manifest(case_entries):
    """Update the dataset manifest with new cases."""
    manifest_path = DATASET_DIR / "manifest.yaml"

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f) or {}
    else:
        manifest = {"version": 1, "description": "RFE Creator evaluation dataset"}

    existing_ids = {c["id"] for c in manifest.get("cases", [])}
    existing_sources = {c.get("source") for c in manifest.get("cases", [])}
    manifest.setdefault("cases", [])

    for entry in case_entries:
        if entry["id"] not in existing_ids and \
                entry.get("source") not in existing_sources:
            manifest["cases"].append(entry)

    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True)


def interactive_select(issues, page_size=20):
    """Present discovered issues for interactive selection with paging."""
    print(f"\nFound {len(issues)} issues:\n")

    selected = set()  # Track selected indices (1-based)
    page = 0
    total_pages = (len(issues) + page_size - 1) // page_size

    while True:
        start = page * page_size
        end = min(start + page_size, len(issues))
        page_issues = issues[start:end]

        # Get terminal width for title truncation
        try:
            import shutil
            term_width = shutil.get_terminal_size().columns
        except Exception:
            term_width = 120
        title_width = max(30, term_width - 40)

        print(f"{'#':>3}  {'':>3} {'Key':<16} {'Priority':<10} {'Title'}")
        print("-" * min(term_width, 40 + title_width))
        for i, issue in enumerate(page_issues, start + 1):
            fields = issue.get("fields", {})
            key = issue.get("key", "?")
            priority = "?"
            p = fields.get("priority")
            if isinstance(p, dict):
                priority = p.get("name", "?")
            title = fields.get("summary", "?")[:title_width]
            mark = "[x]" if i in selected else "[ ]"
            print(f"{i:>3}  {mark} {key:<16} {priority:<10} {title}")

        print(f"\nPage {page + 1}/{total_pages} "
              f"(showing {start + 1}-{end} of {len(issues)}) | "
              f"{len(selected)} selected")
        prompt_parts = ["Select: numbers (e.g. 1,3,5-10), 'all'"]
        if page + 1 < total_pages:
            prompt_parts.append("'n'=next")
        if page > 0:
            prompt_parts.append("'p'=prev")
        prompt_parts.append("'done'=finish")
        print(" | ".join(prompt_parts))

        selection = input("> ").strip().lower()

        if selection == "all":
            return [i["key"] for i in issues]
        elif selection == "n" and page + 1 < total_pages:
            page += 1
        elif selection == "p" and page > 0:
            page -= 1
        elif selection == "done" or selection == "":
            if selected or selection == "done":
                break
        else:
            # Parse number selections — toggle on/off
            for part in selection.split(","):
                part = part.strip()
                try:
                    if "-" in part:
                        s, e = part.split("-", 1)
                        for n in range(int(s), int(e) + 1):
                            if 1 <= n <= len(issues):
                                selected.symmetric_difference_update({n})
                    else:
                        n = int(part)
                        if 1 <= n <= len(issues):
                            selected.symmetric_difference_update({n})
                except ValueError:
                    print(f"  Skipping invalid input: {part}")

    # Return keys in issue order
    return [issues[n - 1]["key"] for n in sorted(selected)]


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keys", nargs="*", default=[],
                        help="Specific RHAIRFE keys to fetch")
    parser.add_argument("--jql", default=None,
                        help="JQL query for discovery")
    parser.add_argument("--limit", type=int, default=30,
                        help="Max results for JQL discovery (default: 30)")
    parser.add_argument("--interactive", action="store_true",
                        help="Interactively select from JQL results")
    args = parser.parse_args()

    if not args.keys and not args.jql:
        parser.error("Provide --keys and/or --jql")

    server, user, token = require_env()
    if not all([server, user, token]):
        print("Error: JIRA_SERVER, JIRA_USER, JIRA_TOKEN required.",
              file=sys.stderr)
        sys.exit(1)

    keys = list(args.keys)

    # JQL discovery
    if args.jql:
        print(f"Searching: {args.jql}")
        issues = search_jql(server, user, token, args.jql, args.limit)

        if args.interactive:
            discovered_keys = interactive_select(issues)
        else:
            discovered_keys = [i["key"] for i in issues]

        # Merge with explicit keys (explicit keys first, no duplicates)
        seen = set(keys)
        for k in discovered_keys:
            if k not in seen:
                keys.append(k)
                seen.add(k)

    if not keys:
        print("No issues selected.", file=sys.stderr)
        sys.exit(1)

    # Fetch and create cases
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    case_entries = []

    # Auto-detect next case number from existing directories
    existing_nums = []
    if CASES_DIR.exists():
        for d in CASES_DIR.iterdir():
            if d.is_dir() and d.name.startswith("case-"):
                try:
                    num = int(d.name.split("-")[1])
                    existing_nums.append(num)
                except (IndexError, ValueError):
                    pass
    case_num = (max(existing_nums) + 1) if existing_nums else 1

    # Check which Jira keys already exist in the dataset
    existing_sources = set()
    if CASES_DIR.exists():
        for d in CASES_DIR.iterdir():
            if d.is_dir() and (d / "input.yaml").exists():
                try:
                    with open(d / "input.yaml") as f:
                        existing_input = yaml.safe_load(f)
                    if existing_input and existing_input.get("rfe_id"):
                        existing_sources.add(existing_input["rfe_id"])
                except Exception:
                    pass

    for key in keys:
        if key in existing_sources:
            print(f"Skipping {key}: already in dataset")
            continue
        print(f"Fetching {key}...", end=" ", flush=True)
        try:
            data = fetch_case_data(server, user, token, key)
            case_id = create_case(case_num, data)
            case_entries.append({
                "id": case_id,
                "source": key,
                "pipeline": "rfe.review",
                "difficulty": None,
                "tags": [],
            })
            print(f"-> {case_id}")
            case_num += 1
        except Exception as e:
            print(f"FAILED: {e}", file=sys.stderr)

    # Update manifest
    update_manifest(case_entries)
    print(f"\nCreated {len(case_entries)} cases in {CASES_DIR}")
    print(f"Next steps:")
    print(f"  1. Derive problem statements:  python3 eval/scripts/derive_inputs.py")
    print(f"  2. Review cases and tag difficulty in annotations.yaml")
    print(f"  3. Run eval:  python3 eval/scripts/run_eval.py run --model opus --score")


if __name__ == "__main__":
    main()
