---
rfe_id: RFE-001
title: Reliable Multi-Turn Stateful Tool Calling Through Llama Stack
priority: Major
size: M
status: Ready
parent_key: null
---
## Summary

Multi-turn tool calling through Llama Stack's Responses API degrades progressively as conversations advance, preventing customers from building reliable agentic workflows on RHOAI. Two compounding issues drive the degradation: reasoning context produced by the model is lost between turns (because the Responses API is built on chat completions that strip reasoning text), and tool call parsing quality varies significantly across models in vLLM. As a result, tool calls that succeed in early turns begin failing in later turns, making multi-step agent workflows — the primary use case for the Responses API — unreliable.

## Problem Statement

Customers building agentic AI workflows on RHOAI need tool-calling agents that can reliably execute multi-step tasks: call a tool, receive a result, reason about it, and call another tool. Today, this works inconsistently through Llama Stack. After a few turns of tool use, the model loses access to its prior reasoning because the Responses API strips reasoning text when converting between its internal representation and chat completions. Simultaneously, vLLM's tool call parsers behave inconsistently across supported models — small parsing errors that are tolerable in single-turn interactions compound over multiple turns and further degrade reliability.

The current workaround is to bypass Llama Stack entirely and call vLLM directly via Chat Completions, but this forces customers to reimplement conversation state management, tool orchestration, and error handling — capabilities the Responses API is designed to provide. Customers in regulated industries cannot easily adopt hosted alternatives due to data residency and compliance requirements, so they need the self-hosted agentic platform to work reliably.

## Affected Customers

- **BBVA** — Multi-million dollar account building internal AI tooling on RHOAI. Their agentic workflows require multi-turn tool calling for automated financial analysis and internal process automation. As a regulated financial institution, they require self-hosted infrastructure and cannot use hosted API alternatives.
- **Citi** — Multi-million dollar account running agentic workflows in regulated financial services on RHOAI. Their use cases involve multi-step reasoning and tool use for compliance and operational workflows. Regulatory requirements mandate self-hosted deployment.

Both accounts are actively developing on the Responses API and have reported progressive tool calling degradation.

## Business Justification

BBVA and Citi represent multi-million dollar accounts whose agentic AI initiatives depend on reliable multi-turn tool calling. Deal expansion is at risk if the core agentic capability — multi-turn tool use — remains unreliable. Hosted API providers (e.g., OpenAI with integrated, tested tool calling) become the path of least resistance if RHOAI cannot deliver comparable reliability, despite these customers' strong preference for self-hosted deployment.

Llama Stack's Responses API is RHOAI's strategic answer to hosted agentic APIs. If multi-turn tool calling through this API does not work reliably, the entire agentic platform positioning stalls — not just for these two accounts, but for the broader market of enterprises building agentic workflows that require self-hosted infrastructure.

## Acceptance Criteria

- [ ] A multi-turn tool calling scenario (model calls a tool, receives a result, reasons about it, and calls another tool) completes successfully through Llama Stack's Responses API without degradation across turns
- [ ] Reasoning text produced by the model is preserved across turns so that subsequent tool calls benefit from prior reasoning context
- [ ] Tool call parsing quality through Llama Stack matches the quality observed when calling vLLM directly via Chat Completions for the same model and prompt
- [ ] End-to-end test coverage validates multi-turn tool calling scenarios both directly against vLLM and through Llama Stack across multiple supported models
- [ ] Customers can build multi-turn agent workflows using the Responses API without needing to fall back to direct vLLM Chat Completions access

## Success Criteria

The problem is solved when multi-turn tool calling through Llama Stack is as reliable as single-turn tool calling, and as reliable as equivalent tool calling through direct vLLM access. Specifically:

- Tool call success rate does not degrade as conversation turn count increases
- BBVA and Citi can run their agentic workflows end-to-end on the Responses API without workarounds
- No parity gap exists between tool calling through Llama Stack and tool calling directly against vLLM for supported models
