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
before_score: 9
before_scores:
  what: 2
  why: 1
  open_to_how: 2
  not_a_task: 2
  right_sized: 2
---
## Assessor Feedback

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT | 2/2 | The RFE clearly describes the customer need: platform admins need the ability to register, view, edit, and delete external MaaS model endpoint registrations directly from the RHOAI dashboard. The "What Needs to Happen" section specifies the registration form fields (provider selection, endpoint URL, model name/identifier, credential reference), MVP provider scope (OpenAI, Anthropic, Bedrock) vs. stretch (Azure OpenAI, Vertex AI), and explicitly states CLI must continue working. The need is specific and unambiguous. |
| WHY | 1/2 | The Business Justification positions this as a "MaaS GA completeness requirement" and describes it as closing an admin experience gap that "undermines MaaS adoption." The Affected Customers section names generic enterprise segments: "large financial services, healthcare, and technology companies" and gives examples like "major banks using Azure OpenAI" and "Fortune 500 companies" -- but these are generic segments, not named customer accounts. There is no specific revenue impact, deal at risk, or named account. Per calibration: generic segments with clear need = 1. |
| Open to HOW | 2/2 | The RFE describes WHAT the UI should capture (provider selection, endpoint URL, model name, credential reference) and where it should live (Model Deployments page), which are user-facing surfaces -- WHAT, not HOW. It references MaaSModelRef CRDs as existing platform vocabulary describing the current state, not architecture prescription. Engineering is free to propose how to implement the dashboard UI. |
| Not a task | 2/2 | This is clearly a business need: enterprise platform admins lack a dashboard UI for managing external MaaS model registrations, creating barriers to adoption and productivity gaps. The problem statement centers on customer pain (no discoverability, no lifecycle management, confusion for AI engineers, barrier to adoption). |
| Right-sized | 2/2 | This maps cleanly to a single strategy feature: "Add dashboard UI for external MaaS model registration CRUD." While it covers CRUD operations plus provider support, these are all part of a single cohesive UI feature. The MVP/stretch split for providers keeps it focused. |

**Total: 9/10 — PASS**

**Suggestion to reach full marks (WHY):** Replace the generic customer segment references ("major banks," "Fortune 500 companies") with named customer accounts and specific business impact. For example: "Customer X is blocked from scaling MaaS adoption because their platform admin team refuses CLI-only workflows, putting $Y in expansion revenue at risk." Alternatively, articulate specific deals at risk or pre-sales feedback.

## Technical Feasibility

**Verdict: Feasible**

All foundational building blocks exist in the current RHOAI 3.4 architecture:

1. **MaaSModelRef CRD already supports ExternalModel references** — the `maas-controller` defines `MaaSModelRef` (`maas.opendatahub.io/v1alpha1`) with ExternalModel reference capability. The `providers_external.go` stub exists in the controller.

2. **MaaS UI plugin already exists** — the ODH Dashboard deploys a `maas-ui` federated plugin container on port 8243, with API requests proxied via `/maas/api/*`. This is the natural place to build the registration UI.

3. **Dashboard Kubernetes API proxy supports CRD CRUD** — the dashboard backend provides a generic `/api/k8s` pass-through endpoint with user impersonation, enabling direct MaaSModelRef CRUD without new backend endpoints.

4. **RBAC is already partially configured** — the `maas-api` ClusterRole has read permissions on `maasmodelrefs`. Write permissions may need to be extended for platform admin use.

5. **CLI compatibility is architecturally guaranteed** — both CLI and UI write to the same Kubernetes CRD, so models registered via either path are inherently visible to both.

**Risks:**
- **Medium: RHAISTRAT-1295 dependency** — External Model Egress via IGW backend must land first. The ExternalModel provider is currently a stub. UI should not ship before backend is functional.
- **Low: CRD schema completeness** — the MaaSModelRef spec for ExternalModel may need extension as part of RHAISTRAT-1295.
- **Low: Provider-specific credential handling** — different providers use different auth mechanisms, requiring UX design consideration per provider.
- **Low: MaaS is currently EA** — `v1alpha1` CRD API may change during EA-to-GA transition.

## Strategy Considerations

- Maps to a single strategy feature in the MaaS/Dashboard area
- RHAISTRAT-1295 is a hard dependency — strategy should sequence accordingly
- UX design review should be scheduled early to unblock implementation

## Revision History

### Cycle 1
- **WHY (1/2 → 1/2)**: Strengthened Business Justification with more concrete GA-blocker framing, added organizational security policy angle (platform admins often lack kubectl access in enterprise environments), and clarified the fragmented management experience impact. Score remains 1/2 because the rubric requires named customer accounts or specific revenue impact data to reach 2/2, which are not available from the input. A note was added to the RFE flagging this gap for the product team.
- **Action needed from product team**: Add named customer accounts and specific business impact data (deals at risk, revenue, pre-sales feedback) to the Business Justification and Affected Customers sections to reach WHY 2/2.
