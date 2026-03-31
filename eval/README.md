# RFE Creator Eval Harness

Evaluation harness for the RFE Creator pipeline. Tests whether `/rfe.speedrun` (create + review) produces quality RFEs across different models and skill changes.

## Architecture

```
eval/
  config/
    settings.json             # Permissions for headless skill execution
    thresholds.yaml           # Regression thresholds
    eval-system-prompt.md     # Injected system prompt for eval mode
    judge-prompt.md           # LLM judge prompt (review-only cases)
    judge-prompt-full-pipeline.md  # LLM judge prompt (full-pipeline cases)
  dataset/
    manifest.yaml             # Case list with metadata
    cases/
      case-NNN-slug/
        input.yaml            # Derived prompt + original RFE content
        annotations.yaml      # Optional: human-expected scores
        reference-rfe.md      # Gold standard RFE (from Opus baseline)
        reference-review.md   # Gold standard review
  runners/
    base.py                   # Abstract runner interface
    claude_code.py            # Claude Code runner (claude --print)
  scripts/
    eval.py                   # Main CLI
    bootstrap_dataset.py      # Fetch Jira issues -> eval cases
    derive_inputs.py          # Reverse-engineer prompts from RFE descriptions
    prepare_workspace.py      # Isolated workspace per case
    collect_artifacts.py      # Harvest artifacts post-run
    anthropic_client.py       # Shared client factory (Vertex AI / direct API)
  scoring/
    deterministic.py          # Layer 1: schema/consistency checks
    reference.py              # Layer 2: compare against annotations
    llm_judge.py              # Layer 3: LLM-as-judge meta-evaluation
    regression.py             # Threshold + baseline regression detection
    comparison.py             # Pairwise A/B model comparison
  reporting/
    report.py                 # CLI text + HTML reports with diffs
  runs/                       # Output directory (gitignored)
```

## Quick Start

### 1. Bootstrap the dataset

Fetch existing RFEs from Jira and create eval cases:

```bash
python3 eval/scripts/bootstrap_dataset.py \
  --jql "project = RHAIRFE ORDER BY created DESC" \
  --limit 30 --interactive
```

Interactively select cases from the paginated list. The script auto-detects existing cases and skips duplicates.

### 2. Derive input prompts

Reverse-engineer problem statements from the fetched RFE descriptions:

```bash
python3 eval/scripts/derive_inputs.py
```

This uses Opus (via Vertex AI or direct API) to create a `prompt` + `clarifying_context` for each case, simulating what a PM would type to start the RFE pipeline.

### 3. Generate the gold standard

Run the full pipeline with Opus and save outputs as reference:

```bash
python3 eval/scripts/eval.py gold --model opus
```

This runs `/rfe.speedrun` on all cases, then copies successful outputs to `reference-rfe.md` and `reference-review.md` in each case's dataset directory.

### 4. Run with a different model

```bash
python3 eval/scripts/eval.py run --model sonnet --run-id test-sonnet
```

### 5. Score and compare

```bash
# Score with LLM judge + regression detection against gold baseline
python3 eval/scripts/eval.py score --run-id test-sonnet --baseline gold-2026-03-31

# Or do it all in one shot
python3 eval/scripts/eval.py run --model sonnet --run-id test-sonnet \
  --score --baseline gold-2026-03-31
```

### 6. Pairwise comparison

Compare two runs head-to-head using a position-swapped LLM judge:

```bash
python3 eval/scripts/eval.py compare --run-a gold-2026-03-31 --run-b test-sonnet
```

## Scoring Layers

### Layer 1: Deterministic (free, fast)

Code-based checks on output artifacts:

| Check | What it verifies |
|-------|-----------------|
| file_completeness | Task + review files exist |
| task_schema | Valid rfe-task frontmatter |
| review_schema | Valid rfe-review frontmatter |
| score_bounds | Scores in range, criteria sum = total |
| pass_score_consistency | `pass` matches score >= 7 with no zeros |
| recommendation_consistency | submit only when pass=true |
| revision_tracking | before_score exists when revised=true |
| content_preservation | No untracked content loss |

### Layer 2: Reference (free, needs annotations)

Compares pipeline scores against human-expected values in `annotations.yaml`. Skipped if annotations aren't filled in. Optional — useful for hard numeric regression gates.

### Layer 3: LLM Judge (API cost per case)

An independent Opus judge evaluates output quality:

**Full-pipeline cases** (comparing against gold standard):
- **Coverage**: Does the generated RFE capture the same business needs?
- **Quality**: Is the RFE well-formed (WHAT/WHY, no HOW, right-sized)?
- **Calibration**: Do the pipeline's own rubric scores match reality?

**Review-only cases** (comparing original vs revised):
- **Revision quality**: Did the revision genuinely improve the RFE?
- **Content fidelity**: Was business content preserved?
- **Calibration**: Are the pipeline's scores accurate?
- **Reframing quality**: Were HOW violations properly reframed?

## Regression Detection

### Threshold-based (always runs)

Configured in `config/thresholds.yaml`:

```yaml
deterministic:
  all_pass: true
reference:
  max_score_deviation: 2
  min_recommendation_match_rate: 0.8
  min_feasibility_match_rate: 0.9
llm_judge:
  min_mean_score: 3.5
  min_calibration_accuracy: 3.0
```

### Baseline comparison (with `--baseline`)

Compares per-case metrics between runs. Flags score accuracy drops and recommendation flips.

## Reports

The HTML report (`eval/runs/{run-id}/report.html`) includes:
- Scoring summary with pass/fail per layer
- Regression flags
- Per-case artifact diffs when scored with `--baseline` (collapsible, unified diff format)

## CLI Reference

```bash
# Bootstrap dataset from Jira
python3 eval/scripts/bootstrap_dataset.py --jql "..." --limit 30 --interactive

# Derive prompts from fetched RFEs
python3 eval/scripts/derive_inputs.py
python3 eval/scripts/derive_inputs.py --case case-001  # single case
python3 eval/scripts/derive_inputs.py --force           # re-derive all

# Generate gold standard
python3 eval/scripts/eval.py gold --model opus

# Save references from an existing run (without re-running)
python3 eval/scripts/eval.py save-gold --run-id gold-2026-03-31

# Run eval
python3 eval/scripts/eval.py run --model sonnet --run-id test-sonnet
python3 eval/scripts/eval.py run --model sonnet --run-id test-sonnet --score --baseline gold-2026-03-31
python3 eval/scripts/eval.py run --model haiku --run-id test-haiku --parallel 4

# Score an existing run
python3 eval/scripts/eval.py score --run-id test-sonnet
python3 eval/scripts/eval.py score --run-id test-sonnet --baseline gold-2026-03-31
python3 eval/scripts/eval.py score --run-id test-sonnet --no-judge  # skip LLM judge

# Pairwise comparison
python3 eval/scripts/eval.py compare --run-a gold-2026-03-31 --run-b test-sonnet

# Run specific cases
python3 eval/scripts/eval.py run --model opus --run-id rerun --case case-013 case-019
```

## Runner Abstraction

The harness is agent-agnostic. The `runners/base.py` interface can be implemented for any agent platform:

- `runners/claude_code.py` — Claude Code via `claude --print`
- `runners/agent_sdk.py` — Anthropic Agent SDK (future)
- Any agent compatible with the Agent Skills spec

The scoring, reporting, and comparison layers only examine output artifacts — they don't know which runner produced them.

## Environment

### Jira access (for bootstrap only)

Set in `.env` at the project root:

```
JIRA_SERVER=https://your-site.atlassian.net
JIRA_USER=your-email@example.com
JIRA_TOKEN=your-api-token
```

### Anthropic API (for LLM judge and derive_inputs)

The scripts auto-detect Vertex AI or direct API:
- **Vertex AI**: Set `ANTHROPIC_VERTEX_PROJECT_ID` and `CLOUD_ML_REGION`
- **Direct API**: Set `ANTHROPIC_API_KEY`

### Permissions

See `PERMISSIONS.md` for the full analysis of which tools and permissions the pipeline needs in headless mode.
