---
rfe_id: RFE-001
score: 9
pass: true
recommendation: submit
feasibility: feasible
revised: false
needs_attention: false
before_score: 9
scores:
  what: 2
  why: 1
  open_to_how: 2
  not_a_task: 2
  right_sized: 2
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
| WHAT      | 2/2   | Clearly describes the need: users should be able to create, monitor, list, and delete RayJob resources directly through the CodeFlare SDK without manually managing Ray Cluster lifecycle. The problem (orphaned clusters, unnecessary complexity, inconsistent UX) and desired outcome (job-centric workflow with automatic cluster provisioning and teardown) are specific and well-articulated. |
| WHY       | 1/2   | References "strategic investment," competitive positioning against platforms with simpler job submission, and resource waste costing "thousands of dollars per day" for GPU workloads. Affected customers listed as generic segments ("RHOAI users," "Enterprise data science teams," "Partners"). No named customer accounts, specific deal values, or analyst ratings cited. The business case is plausible but lacks customer-level evidence. |
| Open to HOW | 2/2 | References only established RHOAI platform technologies (CodeFlare SDK, RayJob CRs, Kueue, KFTO, Ray Cluster) as platform vocabulary. Describes desired user-facing behavior without mandating internal architecture, code structure, or specific implementation approaches. |
| Not a task | 2/2  | Clearly a business need framed as a customer problem with success criteria, not an engineering task or tech debt item. |
| Right-sized | 2/2 | Maps cleanly to a single strategy feature: "RayJob support in the CodeFlare SDK." Sub-points are all facets of the same capability. |
| **Total** | **9/10** | **PASS** |

**Verdict**: A well-structured RFE that clearly articulates a real customer pain point with strong WHAT framing and appropriate scope, but lacking named customer evidence in the business justification.

**Actionable suggestion**: To reach 10/10, strengthen the WHY with named customer accounts or specific deal impact — e.g., cite enterprise customers who have reported orphaned cluster costs or flagged the multi-step workflow as a friction point in platform adoption.

## Technical Feasibility

**Feasibility: Feasible** — No blockers identified.

The platform architecture fully supports this capability. KubeRay operator v1.4.2 already includes a mature RayJob controller (v1 API, GA status) that provides the workflow described in the RFE:
- Automatic RayCluster provisioning from a cluster template embedded in the RayJob spec
- Job submission and monitoring via the Ray Dashboard API
- Automatic cluster cleanup after job completion (controlled by `shutdownAfterJobFinishes` field)
- Kueue integration for queuing and quota management (platform already has Kueue deployed)

The technical gap is in the CodeFlare SDK (client-side tooling), not the platform. Adding RayJob CRUD operations to the SDK is straightforward given the stable v1 CRD.

**Architectural notes for strategy phase**:
- CodeFlare SDK is client-side tooling; strategy needs to confirm ownership and whether this is upstream-first or RHOAI-internal
- RayJob spec includes full RayCluster template; SDK abstraction level needs design (full spec flexibility vs. opinionated simplified API)
- Resource waste mitigation depends on `shutdownAfterJobFinishes: true` and `ttlSecondsAfterFinished` defaults
- Dashboard visibility of SDK-created RayJobs may be a separate tracking requirement if dashboard changes are needed
- Backward compatibility with existing RayCluster-based SDK workflows should be considered

## Strategy Considerations

- SDK API design: abstraction level for RayJob spec needs strategy-phase design
- Ownership model: confirm whether CodeFlare SDK changes go upstream-first or RHOAI-internal
- Default image strategy: intersects with distributed-workloads image portfolio
- Dashboard integration: may need separate tracking if dashboard changes are required

## Revision History

No revisions applied. WHY scored 1/2 due to missing named customer accounts — this requires author input (specific customer names, deal values, or support ticket references) that cannot be inferred. The RFE passes at 9/10 with no zero scores.
