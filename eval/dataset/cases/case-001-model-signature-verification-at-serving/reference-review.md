---
rfe_id: RFE-001
score: 9
pass: true
recommendation: submit
feasibility: feasible
revised: false
needs_attention: false
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

TITLE: Model Signature Verification at Serving Time

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT      | 2/2   | Clear, specific need for model signature verification at serving time. Well-defined acceptance criteria covering both S3/HuggingFace and OCI ModelCar sources, policy-driven enforcement, and pass/fail feedback. |
| WHY       | 1/2   | Generic customer segments (FSI, government, regulated industries) with strategic investment completion argument (RHAISTRAT-513). No named customer accounts or specific revenue/deal impact. The strategic investment causal chain is present but could be strengthened. |
| Open to HOW | 2/2 | Uses platform vocabulary (KServe, llm-d, Cosign, ModelCar, OpenSSF Model Signature) without prescribing internal architecture. Describes what needs to be verified, not how to implement verification. Policy enforcement modes described as user-facing outcomes. |
| Not a task | 2/2  | Clear business need framed around customer outcomes (admins can configure, users get feedback) rather than engineering activity. |
| Right-sized | 2/2 | Focused on a single capability — signature verification at serving time. Maps to approximately one strategy feature. |
| **Total** | **9/10** | **PASS** |

### Verdict
Strong RFE that clearly describes a business need for completing the model supply chain trust chain. The only gap is named customer evidence in the business justification.

### Feedback
Minor improvement: strengthen WHY by adding named customer accounts or specific deal/revenue impact if available. The strategic investment argument (completing RHAISTRAT-513) provides a clear causal chain but the assessor looks for customer-level evidence for a full 2/2.

## Technical Feasibility

**Feasibility**: feasible

The platform can support this capability. KServe's storage initializer architecture provides a natural enforcement point for signature verification before model serving begins. The need is clear and architecturally compatible with the platform.

**Strategy considerations for /strat.refine**:
- Cross-component coordination: changes may span KServe storage initializer, odh-model-controller, and dashboard/CLI tooling
- Two distinct verification paths needed: OpenSSF Model Signatures (model.sig for S3/HuggingFace) vs Cosign signatures (for OCI ModelCar images) — these have different trust models
- Policy configuration API surface needs design: how admins specify verification requirements per namespace/runtime
- Trust root distribution: mechanism needed to propagate public keys from Trusted Artifact Signer to serving pods
- OCI ModelCar Cosign verification may overlap with cluster-level image admission control — engineering should determine whether to handle at KServe level or defer to cluster policy
- Multi-node inference (LeaderWorkerSet) coordination for verification across pods
- Upstream KServe contribution may be needed for storage initializer extension points
- HuggingFace multi-file model signature coverage (sharded models)

**Blockers**: none — all concerns are strategy-phase architecture decisions, not fundamental platform incompatibilities.

**Scope assessment**: appropriate — this is a single business need (verify signatures at serving time) even though implementation may involve multiple work streams.

## Strategy Considerations

Items flagged for /strat.refine:
- Determine enforcement architecture (storage initializer vs admission webhook vs both)
- Design policy CRD or configuration mechanism for admin-facing verification policy
- Define trust root distribution approach
- Clarify OCI image signature verification responsibility (KServe vs cluster admission control)
- Plan upstream KServe contribution strategy
- Address multi-node inference verification coordination

## Revision History

No revisions applied. RFE passes rubric (9/10) with no zeros and is technically feasible. WHY scored 1/2 due to generic customer segments — this is noted for the author but does not require auto-revision as the RFE passes.
