---
rfe_id: RFE-001
title: Responses API OpenAI Field/Parameter Parity for GA Readiness
priority: Major
size: L
status: Ready
parent_key: null
---
## Summary

Customers cannot migrate production workloads from OpenAI to Red Hat AI because the current Tech Preview Responses API implementation silently drops fields, is missing parameters, and has undocumented behavioral differences compared to the OpenAI Responses API. This forces customers to maintain dual codepaths or accept unexpected failures when switching providers. Full field-level and parameter-level parity with the OpenAI Responses API is needed to move the Responses API from Tech Preview to GA, enabling customers to adopt Red Hat AI as a drop-in replacement for OpenAI in agentic use cases (tool use, multi-turn reasoning, structured outputs).

## Problem Statement

The Responses API is the primary interface for agentic AI capabilities — tool use, multi-turn reasoning, and structured outputs. The current Tech Preview implementation was shipped with intentionally incomplete OpenAI API coverage to move fast, but the gaps now block customer adoption:

- **Silent field drops**: Fields sent by customer applications are silently ignored rather than processed or rejected with a clear error. This causes subtle, hard-to-debug behavioral differences between OpenAI and Red Hat AI.
- **Missing parameters**: Parameters supported by the OpenAI Responses API are absent, forcing customers to remove functionality or maintain separate codepaths.
- **Undocumented behavioral differences**: Streaming (SSE) event format, error responses, and edge-case behaviors differ from OpenAI without documentation, making it impossible for customers to assess compatibility before migrating.
- **No compatibility matrix**: Customers have no way to determine which fields and parameters are supported, partially supported, or unsupported without trial-and-error testing.

The result is that 20+ validated customers across financial services, public sector, telecom, and manufacturing cannot convert from Tech Preview to GA production deployments.

## Affected Customers

- **Italian Public Sector** (7 accounts: ANAC, AGEA, INPS, Poste Italiane, FIT, ENEL, SNAM) — positioning Red Hat AI as "Private OpenAI"; API parity is the entire value proposition for these accounts
- **Bank of America** — requires OpenAI-compatible endpoints for Model-as-a-Service deployment
- **Infineon** — explicitly requires the ability to "interface via OpenAI API standard to easily switch models" for provider portability
- **Citi** — Backstage plugin integration depends on endpoint parity with the OpenAI API
- **Turkcell** — building pluggable RAG and agent stack requiring OpenAI-compatible Responses API
- **Isbank** — requires OpenAI-compatible standard interface for agent workloads
- **SVA** — migrating from Watsonx specifically because of OpenAI-style API limitations; incomplete parity undermines the migration rationale
- **20+ additional validated customers** across financial services, public sector, telecom, and manufacturing sectors

## Business Justification

- **Top adoption driver**: OpenAI API compatibility is the #1 adoption driver validated across customer discovery efforts. Incomplete API parity directly blocks the largest revenue opportunity in the pipeline.
- **Italian public sector opportunity**: 7 accounts position Red Hat AI as "Private OpenAI" — API parity is the entire value proposition. These accounts cannot proceed without it.
- **Enterprise financial services**: Bank of America and Citi both require OpenAI-compatible endpoints as a prerequisite for their deployment models (MaaS and Backstage integration respectively).
- **Provider portability**: Infineon and SVA are choosing Red Hat AI specifically for OpenAI compatibility — gaps undermine the competitive differentiator against alternatives like Watsonx.
- **TP-to-GA conversion**: This is the single highest-leverage action to convert Tech Preview users into GA production customers. Every day of delay extends the gap between TP adoption and revenue recognition.

## User Scenarios

1. **As an enterprise developer migrating from OpenAI**, I need to point my existing OpenAI Python SDK application at Red Hat AI's Responses API endpoint and have it work with zero code changes, so that I can adopt Red Hat AI without rewriting my application.
2. **As a platform engineer evaluating Red Hat AI for production**, I need a published compatibility matrix showing per-field, per-parameter coverage compared to the OpenAI Responses API, so that I can assess migration risk and plan my adoption timeline.
3. **As an application developer using agentic capabilities**, I need streaming (SSE) event format parity with OpenAI's Responses API for tool use, multi-turn reasoning, and structured output responses, so that my real-time agent UIs and orchestration pipelines work without modification.

## Acceptance Criteria

- [ ] A customer application written against the OpenAI Responses API (Python SDK) works against Red Hat AI's Responses API with zero code changes, or all differences are documented in a published compatibility matrix
- [ ] No silent field drops — every unsupported field returns a clear error or is documented as unsupported in the compatibility matrix
- [ ] Streaming behavior matches OpenAI SSE event format for all supported response types
- [ ] Compatibility matrix published documenting per-field, per-parameter coverage compared to OpenAI Responses API
- [ ] Conversations API integration works with the Responses API for multi-turn interactions
- [ ] Performance benchmarks published for representative workloads (latency p50/p95/p99, throughput, resource consumption) with sizing guidance

## Success Criteria

- Customer applications targeting the OpenAI Responses API can run against Red Hat AI with zero code changes for all documented-as-supported capabilities
- Tech Preview customers (especially Italian public sector accounts and financial services) can begin GA production deployments
- Published compatibility matrix enables customers to self-assess migration readiness without trial-and-error testing

## Scope

### In Scope
- Full field-level and parameter-level parity with the OpenAI Responses API
- SSE streaming parity for all supported response types
- Conversations API integration with the Responses API
- Per-field, per-parameter compatibility matrix documentation
- Performance benchmarks and sizing guidance for representative workloads
- Clear error responses for any unsupported fields or parameters

### Out of Scope
- Response storage and persistence infrastructure (see separate RFE)
- Multi-provider backend validation matrix (see separate RFE)
- Observability integration with GenAI semantic conventions (see separate RFE)
- TP-to-GA upgrade tooling and migration path documentation (see separate RFE)
