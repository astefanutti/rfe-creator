---
name: strat.review
description: Adversarial review of refined strategies. Runs independent forked reviewers for feasibility, testability, scope, and architecture.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Skill
---

You are a strategy review orchestrator. Your job is to run independent adversarial reviews of the strategies in `artifacts/strat-tasks/` and combine the results into a single review report.

## Step 1: Verify Artifacts Exist

Read files in `artifacts/strat-tasks/`. If no strategy artifacts exist or they haven't been refined yet (no "Strategy" section), tell the user to run `/strat.refine` first and stop.

Check if a prior review report exists at `artifacts/strat-review-report.md`. If it does, read it — this is a re-review after revisions.

## Step 2: Fetch Architecture Context

```bash
bash scripts/fetch-architecture-context.sh
```

## Step 3: Run Reviews

Invoke these forked reviewer skills in parallel. Each runs in its own isolated context — no reviewer sees another's output.

- **`feasibility-review`**: Can we build this with the proposed approach? Are effort estimates credible?
- **`testability-review`**: Are acceptance criteria testable? What edge cases are missing?
- **`scope-review`**: Is each strategy right-sized? Does the effort match the scope?
- **`architecture-review`** (if architecture context available): Are dependencies correctly identified? Are integration patterns correct?

Each reviewer receives:
- The strategy artifacts (`artifacts/strat-tasks/`)
- The source RFEs (`artifacts/rfes.md`, `artifacts/rfe-tasks/`)
- The prior review report (if this is a re-review)

## Step 4: Combine Results

Write `artifacts/strat-review-report.md`:

```markdown
# Strategy Review Report

**Date**: <date>
**Strategies reviewed**: <count>
**Architecture context**: <version or "not available">

## Summary
<Overall assessment: are these strategies ready for prioritization?>

## Per-Strategy Results

### STRAT-001: <title>

**Feasibility**: <assessment>
**Testability**: <assessment>
**Scope**: <assessment>
**Architecture**: <assessment or "skipped — no context">

**Consensus recommendation**: <approve / revise / split / reject>
**Key concerns**:
- <concern from reviewer>
- <concern from reviewer>

**Agreements across reviewers**: <where reviewers aligned>
**Disagreements**: <where reviewers diverged — preserve both views>

### STRAT-002: <title>
...

## Revision History
<If re-review: what changed, what's resolved, what's new>
```

Important: **Preserve disagreements.** If the feasibility reviewer says "this is fine" but the scope reviewer says "this is too big," report both views. Do not average or harmonize.

## Step 5: Advise the User

Based on the results:
- **All approved**: Tell the user strategies are ready for `/strat.prioritize`.
- **Some need revision**: List specific issues. Tell the user to edit the strategy files and re-run `/strat.review`.
- **Fundamental problems**: Recommend revisiting the RFE or re-running `/strat.refine` with different constraints.

$ARGUMENTS
