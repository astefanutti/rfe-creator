---
rfe_id: RFE-001
score: 9
pass: true
recommendation: submit
feasibility: feasible
revised: true
needs_attention: true
scores:
  what: 2
  why: 1
  open_to_how: 2
  not_a_task: 2
  right_sized: 2
before_score: 8
before_scores:
  what: 2
  why: 1
  open_to_how: 1
  not_a_task: 2
  right_sized: 2
---
## Assessor Feedback

### WHAT — 2/2
The RFE clearly and specifically describes what is needed: the ability to pass an `mlflow_tracking_uri` parameter to Training Hub training functions (`sft()`, `osft()`, `lora_sft()`) to get automatic logging of metrics, hyperparameters, and run metadata to an MLflow server. The desired outcome section enumerates six concrete capabilities. Success criteria are well-defined and measurable.

### WHY — 1/2 (unchanged after revision)
The RFE provides business justification with productivity gains (2–4 hours/week savings), enterprise readiness arguments, competitive positioning, and market data (MLflow has 10M+ downloads/month). Revision added adoption-blocking language and competitive risk framing. However, the named organizations — "Acme AI Labs, FinServ Analytics, MedTech ML division" — still read as illustrative/generic examples. No specific revenue figure, deal risk, or concrete engagement is cited. **Author action needed**: Verify these are real customer accounts and attach specific business consequences (deal size, adoption timelines, support escalations) to strengthen to 2/2.

### Open to HOW — 2/2 (improved from 1/2)
MLflow is an established platform technology, so referencing it is appropriately WHAT. After revision:
- "Rank-0 process logs" reframed to user-facing outcome: "logged exactly once per step without duplicate entries"
- "Environment variable equivalents" reframed to describe the deployment need without prescribing mechanism
- Specific coexisting backends (W&B, TensorBoard, JSONL) retained as they represent known existing Training Hub integrations that must continue working — this is a compatibility requirement, not prescriptive HOW

### Not a task — 2/2
Clearly a business need, not a task or chore. Describes a customer problem, identifies who benefits, and articulates desired outcomes in terms of user value.

### Right-sized — 2/2
Maps cleanly to a single strategy feature. Focused on one capability (MLflow tracking integration) applied to existing training functions.

**Total: 9/10 — PASS** (before revision: 8/10)

## Technical Feasibility

**FEASIBLE** — All architectural building blocks are already in place.

- MLflow is a first-class RHOAI component (v3.10.1) managed by the MLflow Operator, listed in PLATFORM.md under "Experiment Tracking"
- MLflow server exposes REST APIs at `/api/2.0/mlflow/*` and `/api/3.0/mlflow/*` for experiment/run/metric logging
- Training Hub workflows run as standard PyTorch/HuggingFace training jobs via the Kubeflow Trainer, where MLflow integration is a mature pattern
- Network connectivity: MLflow NetworkPolicy allows ingress on port 8443 from any pod in any namespace
- HuggingFace Transformers' `MLflowCallback` already implements rank-0-only logging by default
- The `mlflow-integration` RBAC role exists for programmatic/service-account access to MLflow from data plane workloads

**Risks (none are blockers):**
1. MLflow Python client needs to be added to Training Hub container images (TH06 series)
2. ServiceAccount RBAC bindings needed for `mlflow-integration` role
3. TLS CA trust configuration needed in training pods (standard OpenShift pattern via `odh-trusted-ca-bundle`)
4. MLflow is currently Early Access (EA) in RHOAI 3.4-ea.2 — maturity coupling concern for product management
5. Auto-discovery of MLflow URI could enhance UX beyond manual `mlflow_tracking_uri` parameter

## Strategy Considerations

- Single strategy feature: "Add MLflow experiment tracking integration to Training Hub"
- Cross-component coordination needed between Training Hub (distributed-workloads) and MLflow Operator teams
- Container image changes required for Training Hub builds
- Documentation updates needed for `docs/guides/logging.md`

## Revision History

### Cycle 1 (auto-revision)
**Open to HOW (1→2):** Reframed three implementation-leaning details:
1. "only the rank-0 process logs to MLflow" → "training metrics are logged exactly once per step without duplicate entries or conflicts"
2. "Environment variable equivalents" → "support deployment scenarios where parameters cannot be passed programmatically"
3. "rank-0-only logging" in success criteria → "without duplicate log entries"

**WHY (1→1, unchanged):** Added adoption-blocking language ("explicitly identified the lack of MLflow integration as a gap blocking their adoption") and competitive risk framing ("migration barrier that favors competitors"). Score unchanged because the named customer accounts (Acme AI Labs, FinServ Analytics, MedTech ML division) still appear illustrative — no specific revenue impact or deal data attached. **Author should verify these are real accounts and add concrete business consequences to reach 2/2.**

Content preservation check: PASS — all content preserved (reframings in place, no removals).
