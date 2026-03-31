---
rfe_id: RFE-001
title: Full MLFlow Prompt Template Support in Gen AI Studio
priority: Major
status: Ready
size: M
parent_key: null
---
## Customer Statement / Problem

AI Engineers using RHOAI Gen AI Studio currently can only load and save simple system prompts through the MLFlow integration introduced in RHOAI 3.4. However, MLFlow's prompt registry supports richer template types that customers depend on: **parameterized text templates** with `{{variable}}` placeholders and **multi-role chat templates** with multiple turns (system, user, assistant). Without support for these template types, engineers must leave Gen AI Studio and work directly in the MLFlow UI or switch to competing tools like IBM wx.ai PromptLab, which already provides this end-to-end prompt management experience.

This gap forces AI Engineers to context-switch out of their primary RHOAI workspace, breaks their development workflow, and undermines Gen AI Studio's value proposition as a unified environment for building generative AI applications.

## Customer Names

- **Credit Mutual** — Named customer commitment. Credit Mutual has explicitly conditioned their migration to RHOAI on this capability being available. This is a direct retention and adoption risk.
- **Multiple existing prompt lab customers** — Waiting on RHOAI feature parity with prompt management capabilities before migrating to the platform.
- **AI Engineers building generative AI applications within RHOAI** — Broad user segment affected by the current limitation.

## Business Justification

1. **Named customer retention risk**: Credit Mutual has explicitly conditioned their RHOAI adoption on full prompt template support in Gen AI Studio. Failure to deliver this capability directly risks losing the customer.
2. **Competitive parity**: IBM wx.ai PromptLab currently offers end-to-end prompt template management (browsing, variable substitution, inference, saving). The lack of equivalent functionality in RHOAI is a documented reason customers evaluate and choose competing platforms.
3. **Migration enabler**: Multiple existing prompt lab customers are blocked from migrating to RHOAI until prompt template feature parity is achieved. This feature unblocks a cohort of migrations, not just a single customer.
4. **Strategic investment alignment**: Gen AI Studio is a strategic investment area for RHOAI. Full MLFlow prompt management is necessary for Gen AI Studio to be a credible alternative to competing offerings in the generative AI development space.

## User Persona

**AI Engineer** — Builds and iterates on generative AI applications using RHOAI. Works with prompt templates as a core part of their development workflow: authoring prompts with variable placeholders, testing them with different inputs against language models, and versioning them in the MLFlow prompt registry for production use.

## User Problem

AI Engineers cannot work with parameterized text prompt templates or multi-role chat prompt templates from Gen AI Studio. Specifically, they cannot:

- Browse or search the MLFlow prompt registry for text and chat template types (only system prompts are visible today)
- Load prompt templates that use `{{variable}}` placeholders
- View the variables defined in a template or fill in values for them
- Run inference using a prompt template with substituted variable values
- Create new text or chat prompt templates from within Gen AI Studio
- Save new or modified prompt templates as versioned entries back to the MLFlow registry

As a result, AI Engineers must switch to the MLFlow UI directly or use competing tools like wx.ai PromptLab, breaking their workflow within RHOAI and reducing the platform's value.

## Acceptance Criteria / Definition of Done

1. Users can browse and search the MLFlow prompt registry from Gen AI Studio and see all template types — both text templates and chat templates — not just system prompts.
2. Users can load a text prompt template with `{{variable}}` placeholders, view the list of variables, fill in values, and run inference with the substituted prompt.
3. Users can load a multi-role chat prompt template (with system, user, and assistant turns), view variables across all turns, fill in values, and run inference.
4. Users can create a new text prompt template with variable placeholders from within Gen AI Studio.
5. Users can create a new multi-role chat prompt template with multiple turns from within Gen AI Studio.
6. Users can save new or modified prompt templates as versioned entries in the MLFlow prompt registry.
7. Users can attach a registered MLFlow model to a prompt template session for inference.
8. Existing system prompt loading behavior from RHOAI 3.4 is preserved and unaffected.
9. Feature parity with wx.ai PromptLab prompt management capabilities (browse, load, variable substitution, inference, save) is achieved.

## Scope

**In scope:**
- Extending the existing MLFlow prompt integration in Gen AI Studio to support text and chat template types
- Browsing and searching the MLFlow prompt registry for all template types
- Loading, displaying, and editing text and chat prompt templates
- Variable detection, display, and value substitution for `{{variable}}` placeholders
- Running inference with substituted prompt templates
- Creating new text and chat prompt templates
- Saving prompt templates as versioned entries in the MLFlow registry
- Attaching registered MLFlow models to prompt template sessions

**Out of scope:**
- Changes to MLFlow internals or the MLFlow prompt registry API itself
- Prompt evaluation or batch testing pipelines
- Prompt optimization (e.g., DSPy-based automatic prompt tuning)
- Capabilities not supported by MLFlow's prompt registry
