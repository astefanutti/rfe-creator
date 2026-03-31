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

**WHAT: 2/2** — Clear and specific. Four concrete visibility gaps are enumerated (request tracing, token usage monitoring, latency/error observability, usage attribution). Acceptance criteria are measurable and unambiguous.

**WHY: 2/2** — Four named enterprise customers (Amadeus, T-Mobile, Bank of America, Poste Italiane) with a direct quote from Amadeus ("OpenTelemetry is really important — to trace between agent and LLM"), quantified scope (500+ AI initiatives), and explicit production blockers tied to revenue risk and competitive positioning.

**Open to HOW: 2/2** — Describes customer-facing observability surfaces (telemetry attributes, tracing, dashboards, attribution) without mandating internal architecture. OpenTelemetry naming is WHAT per the rubric's technology exception — the customer need IS OpenTelemetry-based instrumentation, as stated directly by Amadeus. No internal architecture prescribed.

**Not a task: 2/2** — Framed as a business need (production readiness, cost accountability, SLA compliance, governance) rather than an engineering activity. No implementation tasks prescribed.

**Right-sized: 2/2** — Maps to a single strategy feature: GenAI observability instrumentation for the Responses API. The four acceptance criteria (telemetry emission, end-to-end tracing, dashboards, usage attribution) are facets of one cohesive observability capability, not separate features.

**Total: 10/10 — PASS**

No actionable suggestions. Minor note: if engineering finds dashboards are a distinct effort from instrumentation, consider a follow-on RFE, but as written the scope is appropriately cohesive.

## Technical Feasibility

**Feasibility: feasible_with_caveats**

The RHOAI 3.4 platform has significant existing observability infrastructure that supports this RFE:

- **Existing**: The rhods-operator Monitoring Controller already deploys MonitoringStack, Prometheus, Tempo (distributed tracing), and OpenTelemetry Collectors. The operator has RBAC for OTel CRDs. Perses dashboard integration exists in odh-dashboard.
- **Existing OTel integration**: fms-guardrails-orchestrator (full OTLP export), odh-model-controller gateway-discovery (optional OTLP traces), Llama Stack distribution (optional OTel instrumentation), KServe controller (creates OTel Collectors for InferenceServices).
- **Existing metrics**: vLLM exposes token counts on /metrics, ServiceMonitors/PodMonitors are dynamically created by odh-model-controller.

**Caveats**:

1. **GenAI Semantic Convention maturity**: OTel GenAI semantic conventions are still evolving. Building against an unstable spec risks rework, though strong customer demand (Amadeus) justifies early adoption.
2. **vLLM instrumentation gap**: vLLM currently exposes Prometheus metrics but not OTel spans with GenAI attributes. Requires either upstream contribution, downstream patch, or proxy-layer instrumentation.
3. **Trace context propagation**: End-to-end tracing through Gateway → Istio → KServe → vLLM requires W3C traceparent propagation at each hop. Istio handles this by default, but application-layer propagation in serving runtimes needs validation.
4. **Identity flow for attribution**: Per-user/team attribution depends on identity at the telemetry emission point. MaaS sets identity headers via Authorino; direct InferenceService access may lack identity context.
5. **"Responses API" terminology**: Clarification needed on whether this refers specifically to OpenAI's Responses API (newer than Chat Completions) or broadly to inference API response observability.
6. **Performance overhead**: Distributed tracing on the inference hot path requires careful benchmarking and sampling strategies.

## Strategy Considerations

- Consider phasing: Phase 1 = Prometheus GenAI metrics + Perses dashboards (leveraging existing vLLM /metrics); Phase 2 = OTel distributed tracing with GenAI semantic conventions; Phase 3 = per-user/team attribution and chargeback.
- Existing MaaS token rate limiting infrastructure (TokenRateLimitPolicy, Limitador) already tracks per-user token usage — could be extended for observability/chargeback, reducing duplication.
- Coordinate with upstream vLLM community on OTel instrumentation — Red Hat is a significant contributor.
- Determine whether to invest in Llama Stack's built-in OTel instrumentation or standardize platform-level instrumentation across all serving runtimes.
- Size may need re-evaluation to L if all acceptance criteria must be met in a single release.

## Revision History

No revisions needed — RFE scored 10/10 on first assessment.
