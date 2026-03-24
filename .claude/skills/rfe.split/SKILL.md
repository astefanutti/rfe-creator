---
name: rfe.split
description: Split an oversized RFE into smaller, right-sized RFEs. Accepts a local artifact (e.g., /rfe.split RFE-001) or Jira key (e.g., /rfe.split RHAIRFE-1234). Walks through decomposition options, generates new RFEs, reviews them, and checks for scope coverage gaps.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill, mcp__atlassian__jira_get_issue
---

You are an RFE splitting assistant. Your job is to help decompose an oversized RFE into smaller, right-sized RFEs — each representing a coherent, independent business need.

## Step 1: Load the Source RFE

Check if `$ARGUMENTS` contains a Jira key (e.g., `RHAIRFE-1234`) or a local artifact reference (e.g., `RFE-001`).

**If a Jira key**: Fetch the RFE from Jira using `mcp__atlassian__jira_get_issue`. Write it to `artifacts/rfe-tasks/` as a local artifact using the RFE template format (read `${CLAUDE_SKILL_DIR}/../rfe.create/rfe-template.md` for the format). Record the Jira key in the artifact metadata.

**If a local artifact reference**: Find and read the matching file in `artifacts/rfe-tasks/`.

**If no argument provided**: List available RFEs in `artifacts/rfe-tasks/` and ask the user which one to split.

Also read `artifacts/rfe-review-report.md` if it exists — the right-sizing feedback explains why this RFE needs splitting.

## Step 2: Analyze and Propose Split Options

Read the RFE carefully. Identify the distinct business needs, capabilities, acceptance criteria, and user personas within it.

Propose 2-3 decomposition strategies, each with:
- How many RFEs it would produce
- What each RFE would cover
- Brief rationale for why this decomposition makes sense

Common decomposition axes:
- **By capability area** — e.g., monitoring vs alerting vs reporting
- **By user persona** — e.g., admin needs vs end user needs
- **By delivery phase** — e.g., core need that unblocks value vs enhancements
- **By scope boundary** — e.g., platform capability vs integration with external systems

Present the options and ask the user to pick one, adjust it, or propose their own.

## Step 3: Generate New RFEs

Once the user confirms a decomposition:

1. Generate new RFE artifacts using the template in `${CLAUDE_SKILL_DIR}/../rfe.create/rfe-template.md`
2. Each new RFE must be a **coherent, standalone business need** — not just a slice of acceptance criteria. It needs its own problem statement, justification, and success criteria.
3. Carry forward from the original:
   - Business justification (tailor to each child's specific scope)
   - Affected customers and segments
   - Priority (may differ per child — ask the user if unclear)
   - If the original came from Jira, note the source key (e.g., `**Split from**: RHAIRFE-1234`)
4. Number new RFEs sequentially after the highest existing RFE number in `artifacts/rfe-tasks/`
5. Write each to `artifacts/rfe-tasks/RFE-NNN-<slug>.md`
6. Archive the original by renaming it to `RFE-NNN-<slug>.md.split`
7. Update `artifacts/rfes.md` — remove the original entry, add the new RFEs

## Step 4: Review New RFEs

Run `/rfe.review` on the new artifacts. This runs rubric scoring, technical feasibility, and auto-revision.

## Step 5: Coverage Check

After the review completes, compare the **combined scope** of all new RFEs against the original:

1. List every acceptance criterion, capability, and scope item from the original RFE
2. For each item, identify which new RFE covers it
3. Flag any items from the original that are not covered by any new RFE

Present the coverage matrix to the user:

```
## Coverage Check

| Original Scope Item | Covered By |
|---------------------|------------|
| Users can view drift metrics | RFE-003 |
| Alerts fire on threshold breach | RFE-004 |
| Integration with external monitoring | NOT COVERED |
```

**If gaps exist**, ask the user:
- Add the missing scope to one of the new RFEs?
- Create an additional RFE for it?
- Intentionally drop it? (Record the decision)

If any changes are made, re-run `/rfe.review` on the affected RFEs.

## Step 6: Summary

Present the final state:

```
## Split Complete

Original: RFE-001 (archived as RFE-001-*.md.split)
New RFEs:
- RFE-003: <title> (Priority: Normal) — PASS
- RFE-004: <title> (Priority: Normal) — PASS

Coverage: All original scope items covered
Review: All new RFEs passed
```

Tell the user they can:
- Run `/rfe.submit` to create or update tickets in Jira
- Edit any new RFE in `artifacts/rfe-tasks/` and re-run `/rfe.review`

$ARGUMENTS
