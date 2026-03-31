---
rfe_id: RHAIRFE-1580
score: 9
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
  right_sized: 1
before_score: 9
before_scores:
  what: 2
  why: 2
  open_to_how: 2
  not_a_task: 2
  right_sized: 1
---
## Assessor Feedback

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT      | 2/2   | Clearly describes the need for autoscaling Ray clusters via the SDK. The problem statement articulates three specific, compounding problems (resource waste from over-provisioning, performance bottlenecks from under-provisioning, operational burden). The desired outcome enumerates concrete capabilities: min/max worker counts, autoscaling policies, runtime monitoring, and dynamic adjustment. |
| WHY       | 2/2   | Names specific customer accounts: Fintech Analytics (GPU training with variable demand, high infra costs), MedAI Corp (batch inference with spiky traffic, queue times and idle costs), and DataScale Inc. (multi-tenant platform needing per-tenant cost controls). States that multiple enterprise prospects have cited the lack of autoscaling as an adoption blocker. |
| Open to HOW | 2/2 | Describes the need entirely in terms of customer-facing SDK surfaces (min/max workers, autoscaling policies, status method, update method) without prescribing internal architecture. References to Prometheus and Ray task queue depth are established RHOAI platform vocabulary. Engineering retains full freedom to choose the autoscaling implementation. |
| Not a task | 2/2  | Clearly a business need: customers need automatic cluster scaling to reduce infrastructure costs, eliminate performance bottlenecks, and remove operational toil. |
| Right-sized | 1/2 | The core ask is cohesive and could map to a single strategy feature. However, the scope is slightly broad — it encompasses multiple autoscaling policy types (resource-based, workload-based, custom metrics via Prometheus), runtime scaling state monitoring, dynamic runtime reconfiguration without cluster teardown, and scale-to-zero. Could stretch to 1-2 features if advanced capabilities are separated from core autoscaling. |
| **Total** | **9/10** | **PASS** |

**Verdict**: A well-structured RFE with clear customer need, named customer evidence, and no architecture prescription; slightly broad scope is the only minor issue.

**Feedback**: This is a strong RFE. The one area for improvement is scope: consider whether dynamic runtime reconfiguration and custom metrics via Prometheus warrant a separate RFE or can be phased as a follow-on. However, since the 1/2 right-sized score reflects capabilities that are delivery-coupled (autoscaling is meaningless without policies to drive it), this is acceptable at the RFE level and may map to multiple strategy features at the RHAISTRAT level.

## Technical Feasibility

**Verdict: FEASIBLE** with moderate technical complexity and a clear implementation path.

**Technical Analysis**:
- KubeRay operator (v1.4.2) is already shipped in RHOAI 3.4-ea.2, providing the foundational RayCluster CRD and lifecycle management
- Ray's built-in autoscaler daemon and `autoscalerOptions` in the RayCluster spec provide native autoscaling hooks
- The workload-variant-autoscaler (WVA) component demonstrates the exact Prometheus-based custom metrics scaling pattern needed
- SDK layer requires new Python abstractions but follows existing patterns (similar to TrainJob/KFP SDK patterns)

**Dependencies**:
- KubeRay Operator v1.4.2 (shipped)
- Prometheus (shipped via openshift-monitoring)
- Ray Runtime 2.52.1/2.53.0 (available via distributed-workloads images)
- Potential upstream KubeRay CRD enhancements for SDK-level autoscaling config exposure

**Blockers** (design-phase, not fundamental):
- SDK design needs to be finalized (which SDK, API surface decisions)
- Ray autoscaler coordination model (external controller vs. built-in autoscaler interaction) needs architecture review
- Dynamic reconfiguration without cluster teardown may need upstream KubeRay changes

**Alignment with Strategy**: Excellent — completes the distributed computing platform vision by enabling elastic Ray clusters, builds on proven RHOAI patterns (WVA, training-operator), and directly unblocks enterprise adoption.

## Strategy Considerations

- The scope may map to 1-2 strategy features at the RHAISTRAT level: core autoscaling (min/max workers + resource-based policies) as one, and advanced capabilities (custom metrics, dynamic reconfiguration) as a potential second.
- Architecture review and KubeRay upstream engagement should be completed before implementation begins.

## Revision History

No revisions needed. Initial score of 9/10 with no zero scores and feasibility confirmed.
