---
rfe_id: RFE-001
title: GenAI-Specific Observability for Responses API Workloads on RHOAI
priority: Major
size: M
status: Ready
parent_key: null
---
## Summary

Enterprise operations teams running Responses API workloads on RHOAI have no visibility into request behavior, token consumption, latency, or error rates. Without GenAI-specific observability, these teams cannot trace requests through their AI agent and LLM inferencing pipelines, debug production issues, optimize costs, or demonstrate SLA compliance. Multiple strategic enterprise customers are blocked from moving Responses API workloads to production until GenAI-aware telemetry is available.

## Problem Statement

Today, when an enterprise operations team deploys AI agents or LLM inferencing pipelines that use the Responses API on RHOAI, they have no way to:

- **Trace requests** end-to-end through their agent-to-LLM call chains — they cannot correlate a user-facing request with the underlying model invocations it triggers.
- **Monitor token usage** per request, per user, or per agent — making cost allocation, capacity planning, and chargeback impossible.
- **Observe latency and error rates** for Responses API calls — meaning production issues are discovered by end users, not by operations teams.
- **Attribute usage** to specific users, agents, or teams — preventing the cost accountability and governance required for enterprise AI deployments at scale.

These gaps make the Responses API unsuitable for production use in enterprise environments where operational visibility is a prerequisite for deployment approval.

## Affected Customers

- **Amadeus** — 500+ AI initiatives in progress; explicitly stated "OpenTelemetry is really important — to trace between agent and LLM." Production deployment of Responses API workloads is blocked without this capability.
- **T-Mobile** — Requires comprehensive observability for AI agents, including token usage tracking and performance metrics, to support production-scale agent deployments.
- **Bank of America** — Requires comprehensive observability and monitoring across the entire LLM inferencing pipeline to meet regulatory and operational requirements.
- **Poste Italiane** — Needs real-time model performance visibility across operations to manage AI workloads at enterprise scale.

## Business Justification

Four named enterprise customers with large-scale AI deployments have identified GenAI-specific observability for the Responses API as a requirement for production readiness. Amadeus alone has 500+ AI initiatives that depend on this capability. Without it, these strategic accounts cannot move Responses API workloads beyond proof-of-concept, blocking expansion revenue and putting competitive positioning at risk. These customers specifically require OpenTelemetry-based instrumentation with GenAI semantic conventions — the emerging industry standard for AI observability — to integrate RHOAI telemetry into their existing enterprise monitoring and tracing infrastructure. Production readiness and SLA compliance for AI workloads are gated on this capability.

## Acceptance Criteria

- [ ] Every Responses API call produces telemetry that includes GenAI-specific attributes (e.g., model identifier, input/output token counts, response status) following OpenTelemetry GenAI semantic conventions.
- [ ] Operations teams can trace a Responses API request end-to-end, correlating it with upstream agent calls and downstream model invocations, through OpenTelemetry integration.
- [ ] Real-time dashboards are available showing Responses API latency, token usage, error rates, and throughput — enabling operations teams to monitor production workloads without custom tooling.
- [ ] Token usage and request volume can be attributed to individual users, agents, or teams to support enterprise cost allocation and chargeback workflows.

## Success Criteria

- Operations teams can identify and diagnose Responses API issues in production using standard observability tooling (tracing, metrics, dashboards) without requiring application-level instrumentation by data scientists or developers.
- Enterprise customers can integrate Responses API telemetry into their existing OpenTelemetry-based monitoring infrastructure.
- Cost attribution for Responses API usage is available at the user, agent, or team level, enabling chargeback and capacity planning.
