# Eval Permissions Analysis

The eval harness runs skills in `--print` mode (non-interactive). Any tool call not in the `allow` list triggers a permission prompt that can't be answered, causing the pipeline to fail or skip steps. The eval `settings.json` must pre-approve everything the skills need.

## Skills in the Pipeline

`/rfe.speedrun` orchestrates the full pipeline and invokes sub-skills:

| Skill | Invoked by | Declared `allowed-tools` |
|-------|-----------|--------------------------|
| `/rfe.speedrun` | eval runner | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill |
| `/rfe.create` | rfe.speedrun | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion |
| `/rfe.review` | rfe.speedrun | Read, Write, Edit, Glob, Grep, Bash, Skill, AskUserQuestion |
| `/assess-rfe` | rfe.review (via Skill) | Read, Write, Edit, Glob, Grep, Bash, Agent, TaskGet |
| `/rfe-feasibility-review` | rfe.review (via Agent) | Read, Grep, Glob |
| `/export-rubric` | rfe.create, rfe.review | (not declared, uses Bash) |

## Tools Required

### Core tools (from skill declarations)
- **Read** — reading skill files, templates, architecture context, artifacts
- **Write** — creating RFE artifacts, review files, rubric export
- **Edit** — auto-revision of RFEs during review
- **Glob** — finding artifact files, architecture docs
- **Grep** — searching architecture context for component references
- **Bash** — running Python scripts (frontmatter.py, check_content_preservation.py, etc.)
- **Skill** — rfe.speedrun invokes /rfe.create, /rfe.review; rfe.review invokes /assess-rfe
- **Agent** — rfe.review spawns parallel feasibility review and rubric assessment agents
- **ToolSearch** — resolving deferred tool schemas at runtime

### Bash commands used by the pipeline
- `python3 scripts/frontmatter.py *` — read/write/validate YAML frontmatter
- `python3 scripts/check_content_preservation.py *` — detect removed content
- `python3 scripts/fetch_issue.py *` — Jira REST fallback (blocked in eval by missing env vars)
- `bash scripts/bootstrap-assess-rfe.sh` — clone assess-rfe plugin
- `bash scripts/fetch-architecture-context.sh` — sparse checkout architecture docs
- `python3 .context/assess-rfe/scripts/prep_single.py *` — prepare assessment data
- `python3 .context/assess-rfe/scripts/check_progress.py *` — check assessment progress
- `python3 .context/assess-rfe/scripts/parse_results.py *` — parse assessment results
- `python3 .context/assess-rfe/scripts/summarize_run.py *` — summarize assessment run
- General commands: `ls`, `mkdir`, `cp`, `cat`, `test`, `touch`, `find`, `head`, `tail`, `sed`, `grep`, `echo`, `env`

### Blocked tools
- `mcp__atlassian__*` — all Jira MCP tools (prevents accidental writes to real issues)

## Why Sonnet Fails Without Broad Permissions

In `--print` mode, there's no interactive user to approve permission prompts. When a tool call is denied:
- **Opus** adapts — finds workarounds (e.g., uses `frontmatter.py` via Bash instead of Write, outputs results as text)
- **Sonnet** treats denial as a blocker — stops the pipeline or skips phases

This means permission gaps cause different failure modes per model, which confuses eval results. The eval settings must be permissive enough that no model hits a permission wall — the eval should test skill quality, not permission negotiation.

## Maintaining This List

When adding new skills or modifying existing ones:
1. Check the skill's `allowed-tools` in its SKILL.md
2. Check what Bash commands the skill runs
3. Update `eval/config/settings.json` accordingly
4. Test with the weakest model you plan to eval (e.g., Haiku) — if it passes permissions, stronger models will too
