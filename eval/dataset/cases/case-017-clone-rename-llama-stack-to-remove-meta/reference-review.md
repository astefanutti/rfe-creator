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
  open_to_how: 2
  not_a_task: 1
  right_sized: 2
---
## Assessor Feedback

### WHAT (2/2)
The RFE clearly and specifically describes what is needed: rename the project from "Llama Stack" to a community-owned name across all customer-facing surfaces before RHOAI 3.5 GA. The problem statement articulates the timing constraint well — pre-GA rename is far cheaper than post-GA — and the scope section enumerates every surface that needs updating (CRDs, container images, Python imports, CLI commands, API paths, Helm charts, documentation). No ambiguity about what is being requested.

### WHY (1/2)
The business justification provides four plausible arguments (brand independence, pre-GA cost advantage, ownership clarity, legal risk mitigation), but all are internally-focused strategic reasoning without customer-level evidence. There are no named customer accounts, no revenue or deal impact figures, no analyst data, and no reference to a specific strategic investment with a causal chain. The affected customers section names only generic segments ("RHOAI enterprise customers," "Partners," "Upstream open-source community"). Per rubric calibration, generic segments with clear need but no named accounts scores a 1.

**Actionable suggestion**: Add evidence of customer or partner feedback about brand confusion, or explicitly tie the rename to a named strategic investment (e.g., "open-source community leadership is a 2026 strategic investment"). Even one named partner or customer account expressing concern about Meta branding would lift this to a 2.

### Open to HOW (2/2)
The RFE enumerates customer-facing surfaces that need renaming (CRDs, API groups, container images, CLI commands, import paths) — these are WHAT per the rubric, not architecture prescription. The backward compatibility aliasing requirement is a customer-facing migration policy, not internal architecture. Engineering retains full discretion over implementation approach.

### Not a task (2/2) — revised up from 1/2
After revision, the problem statement now leads with the customer need: "RHOAI enterprise customers, partners, and the open-source community need to adopt and build on RHOAI's agentic AI framework under a stable, community-owned project identity." Success criteria are reframed around business outcomes (customer adoption confidence, smooth early-adopter transition, partner confidence in stewardship) rather than task completion milestones. The RFE now reads as a business need for stable project identity, not a housekeeping rename task.

### Right-sized (2/2)
Despite touching many components (upstream repos, downstream operator, documentation, CI/CD, community), a rename is inherently a single coordinated activity that doesn't decompose into independent strategy features. You either rename everything or nothing — partial rename would be worse. This maps to one strategy feature with broad implementation scope, appropriately sized at L.

## Technical Feasibility

**Feasible.** All Llama Stack APIs are at v1alpha1 maturity and EA (Early Access) status in RHOAI 3.4, with no GA backward compatibility contract. This significantly reduces the rename burden.

Key architecture findings:
- **CRD API Group**: `llamastack.io` with kind `LlamaStackDistribution` (v1alpha1, Namespaced). CRD renames require creating new CRDs + migration, but alpha status means small user base.
- **Platform integration**: The rhods-operator defines `LlamaStackOperator` component CRD at `components.platform.opendatahub.io/v1alpha1` with corresponding controller and RBAC.
- **Container images**: Operator uses `RELATED_IMAGE_ODH_LLAMASTACK_OPERATOR` env vars in OLM CSV (92 images pinned by SHA256).
- **Four repositories**: llama-stack-distribution, llama-stack-k8s-operator, llama-stack-provider-ragas, llama-stack-provider-trustyai-garak.
- **Python packages**: `llama_stack_provider_ragas`, `llama_stack_provider_trustyai_garak` import paths.

**Key risks**:
- Upstream community decision: rename requires either upstream agreement or permanent hard fork
- CRD migration: existing LlamaStackDistribution instances need migration tooling
- Cross-component coordination: 4+ repos plus rhods-operator plus OLM bundle must update atomically
- NetworkPolicy breakage: `app=llama-stack` label selectors must transition carefully
- Python import path changes affect all downstream consumers and KFP pipeline components

**Blockers**: None (upstream governance is a risk, not a hard technical blocker).

## Strategy Considerations

- The upstream community governance decision (rename vs. hard fork) will significantly impact ongoing maintenance burden and should be resolved early in the strategy phase.
- Consider whether backward compatibility aliases need automated migration tooling or just documentation.

## Revision History

### Revision 1 (auto)
- **Not a task (1→2)**: Reframed problem statement to lead with customer need for stable, community-owned project identity rather than describing a rename activity. Reframed success criteria around business outcomes (customer adoption confidence, smooth early-adopter transition, partner confidence) rather than task completion milestones.
- **WHY (1/2, unchanged)**: Cannot auto-resolve — the business justification is strong but lacks named customer accounts or revenue data. The author should add specific customer or partner feedback about Meta branding concerns, or tie the rename to a named strategic investment, to lift this to 2/2.
