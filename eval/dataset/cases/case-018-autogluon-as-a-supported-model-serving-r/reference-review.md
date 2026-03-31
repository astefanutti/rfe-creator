---
rfe_id: RFE-001
score: 10
pass: true
recommendation: submit
feasibility: feasible
revised: true
needs_attention: false
scores:
  what: 2
  why: 2
  open_to_how: 2
  not_a_task: 2
  right_sized: 2
before_score: 9
before_scores:
  what: 2
  why: 2
  open_to_how: 1
  not_a_task: 2
  right_sized: 2
---

## Assessor Feedback

### Criterion Scores

| Criterion | Before | After | Notes |
|-----------|--------|-------|-------|
| WHAT | 2/2 | 2/2 | Clear and specific: adding AutoGluon as a supported serving runtime with dropdown deployment |
| WHY | 2/2 | 2/2 | Strong evidence: $14.5B AutoML market, 70%+ tabular data, 2-4hr deployment friction, named verticals |
| Open to HOW | 1/2 | 2/2 | Revised: removed "via KServe" and "container image" prescriptive references |
| Not a task | 2/2 | 2/2 | Clearly a feature request for a new platform capability |
| Right-sized | 2/2 | 2/2 | Well-scoped single need with explicit scope boundaries and deferred enhancements |

**Total: 10/10 (before: 9/10)**

### Verdict: PASS — Ready for submission

The RFE clearly articulates a business need (streamlined, supported AutoGluon deployment) with strong evidence-based justification. It names specific customer segments and use cases, quantifies the deployment friction, and defines clear success criteria without prescribing implementation.

### Actionable Notes
- No remaining issues requiring author attention.

## Technical Feasibility

**Verdict: Feasible**

The RHOAI platform has a well-established, extensible pattern for adding new serving runtimes. The architecture context (rhoai-3.4-ea.2) confirms:

- `odh-model-controller` ships templates for serving runtimes (vLLM, OVMS, MLServer, etc.)
- `odh-dashboard` reads ServingRuntime resources and presents them in the dropdown
- `rhods-operator` deploys component manifests via kustomize with SHA256-pinned images
- The existing pattern (especially MLServer for traditional ML) provides a clear integration model

**Key considerations for strategy phase:**
- AutoGluon does not currently ship a production-grade KServe-compatible inference server — Red Hat would need to build/maintain one or contribute an MLServer plugin
- AutoGluon's large dependency tree (PyTorch, LightGBM, XGBoost, CatBoost, scikit-learn) complicates container image builds, especially for multi-architecture support (ppc64le, s390x)
- The RFE's CSV input/JSON output format is non-standard for KServe (which uses V2 Inference Protocol); this will need design attention
- AutoGluon is AWS-maintained (Apache 2.0) — dependency on an AWS-controlled project for a supported runtime carries governance considerations
- MLServer plugin approach (similar to existing sklearn/xgboost plugins) may be the lowest-risk implementation path

**No hard technical blockers** prevent this from being feasible. Implementation approach decisions (standalone server vs. MLServer plugin, phased rollout) are appropriately left to the strategy phase.

## Strategy Considerations

- Consider phased approach: community-supported template first, then promoted to fully supported runtime if adoption warrants
- MLServer plugin path reuses existing infrastructure and is architecturally lower risk than a standalone serving container
- Multi-architecture support (especially ppc64le, s390x) for AutoGluon's ML dependencies may constrain initial platform support
- Container image size and CVE patching surface area are ongoing maintenance considerations
- Support scope definition (which model types, prediction modes, data formats) needed during strategy refinement

## Revision History

**Cycle 1 (auto-revision):**
- Reframed "Single-model serving via KServe" → "Single-model deployment per endpoint" in Scope Notes (removed prescriptive architecture reference)
- Reframed "A Red Hat-verified container image for the AutoGluon serving runtime is published and maintained" → "A Red Hat-supported AutoGluon serving runtime artifact is published and maintained" in Success Criteria (removed prescriptive delivery mechanism)
- Content preservation check: PASS — all content preserved, no blocks removed
- Score improved: 9/10 → 10/10 (Open to HOW: 1 → 2)
