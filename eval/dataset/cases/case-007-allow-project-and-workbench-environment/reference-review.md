---
rfe_id: RFE-001
score: 10
pass: true
recommendation: submit
feasibility: feasible
revised: false
needs_attention: false
scores:
  what: 2
  why: 2
  open_to_how: 2
  not_a_task: 2
  right_sized: 2
before_score: 10
before_scores:
  what: 2
  why: 2
  open_to_how: 2
  not_a_task: 2
  right_sized: 2
---
## Assessor Feedback

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT      | 2/2   | Crystal clear need: the dashboard's workbench environment variables form only supports inline secret/config map creation; users need to select existing ones from the namespace. Problem statement details two concrete workarounds (manual duplication, direct YAML editing) and why both are painful. Acceptance criteria are specific and measurable. |
| WHY       | 2/2   | Names Airbus as a customer with a formal support case. References multiple active sales engagements where this is a blocker to RHOAI adoption, flagged by sales teams as deal friction. Named customer account with concrete evidence of impact. |
| Open to HOW | 2/2 | Describes desired user-facing behavior: selecting existing secrets/config maps from a list, displaying keys (not values), showing attached references when editing. References to RHOAI dashboard, Kubernetes Secrets, Config Maps, and Notebook CR are established platform vocabulary. No internal architecture mandated. |
| Not a task | 2/2  | Clear business need: organizations with centralized secret management workflows cannot reconcile their security practices with the dashboard's inline-only model. Capability gap blocking customer adoption, not a chore or tech debt item. |
| Right-sized | 2/2 | Maps to a single strategy feature: support selecting existing Secrets and Config Maps in the workbench environment variables UI. All acceptance criteria relate to the same coherent capability. |
| **Total** | **10/10** | **PASS** |

**Verdict**: Exemplary RFE. No changes needed.

## Technical Feasibility

**Feasible** — No blockers identified.

- The Kubeflow Notebook CRD spec already supports `envFrom` with `secretRef` and `configMapRef` as part of standard Kubernetes PodSpec
- The ODH Dashboard already has RBAC permissions for secrets and configmaps (create/delete/get/list/patch/update/watch) in namespaces
- The kubeflow notebook controller already handles `envFrom` references correctly — no controller changes needed
- Work is entirely in the dashboard UI and backend API layer

**Strategy-phase considerations**: Dashboard UI/UX complexity for resource selection, edit/update workflows for externally-attached secrets, security boundaries for externally-managed secrets, key preview performance in large namespaces.

## Strategy Considerations

None blocking. Standard dashboard UI feature work. Strategy phase should address UX patterns for namespace resource selection and performance considerations for large namespaces.

## Revision History

None — RFE scored 10/10 on first pass. No revisions needed.
