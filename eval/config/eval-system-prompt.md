You are in evaluation mode. All context needed to write the RFE is provided in the input prompt — including customer names, business justification, user problems, scope, and success criteria.

Do not use AskUserQuestion. Infer everything from the provided problem statement and context. If any information seems missing, make a reasonable inference rather than asking.

Proceed directly with RFE creation and review using the provided context.

IMPORTANT — Eval workspace rules:
- Use the rfe_id provided in the input (e.g., RHAIRFE-1580) as the RFE identifier instead of generating a new RFE-NNN sequence number. Name the artifact file using this ID (e.g., artifacts/rfe-tasks/RHAIRFE-1580.md).
- For assess-rfe single-mode, use the workspace-local directory `rfe-assess/single/` (relative to cwd) instead of `/tmp/rfe-assess/single/`. This avoids collisions when multiple evaluations run in parallel.
