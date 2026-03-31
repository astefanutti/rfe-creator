---
rfe_id: RFE-001
title: LlamaStack compatibility for Claude Code Agent SDK workloads on OpenShift AI
priority: Major
size: M
status: Ready
parent_key: null
---
## Summary

Customers building AI agents with the Claude Code Agent SDK need the ability to deploy and operate those agents through LlamaStack on OpenShift AI. LlamaStack currently lacks the API capabilities required to support the Claude SDK's orchestration model — specifically real-time streaming, stateful multi-turn conversation management, and tool-definition interoperability — blocking customers from centralizing their agentic AI workloads on the platform.

## Problem Statement

Customers who have adopted the Claude Code Agent SDK for building AI agents cannot deploy those agents through LlamaStack on OpenShift AI. The Claude SDK's orchestration logic requires capabilities that LlamaStack does not currently expose:

- **No real-time streaming**: Agent responses require incremental token delivery via server-sent events. Without this, users experience unacceptable latency waiting for full response completion before seeing any output.
- **No stateful session management**: The Claude SDK conducts multi-turn conversations involving complex tool-calling workflows. Without server-side state management, the SDK must re-transmit the full conversation history with every request, creating overhead that degrades performance and reliability.
- **No tool-definition interoperability**: The Claude SDK defines tools (such as computer, text_editor, and bash) using its own schema format. LlamaStack cannot interpret these definitions, preventing agents from executing tool calls through the platform.

As a result, customers are forced to either bypass LlamaStack entirely — losing the benefits of unified audit trails, security filtering, and cost optimization — or abandon the Claude Code Agent SDK in favor of less capable alternatives.

## Affected Customers

- **Verizon Networks** — 5th largest OpenShift customer. Verizon is actively building AI agents using the Claude Code Agent SDK and requires LlamaStack deployment on OpenShift AI to meet their enterprise infrastructure and compliance requirements.

## Business Justification

- **Revenue at risk**: Verizon's agentic AI workloads represent business worth millions in OpenShift consumption. Without LlamaStack support for the Claude SDK, these workloads may move to competing platforms.
- **Strategic priority**: Keeping Verizon on OpenShift and driving OpenShift AI adoption is a key business objective. Supporting their chosen agent framework through LlamaStack directly advances this goal.
- **Platform value proposition**: Centralizing agentic traffic through LlamaStack enables unified audit trails, security filtering, and cost savings over third-party hosted models — but only if the customer's agent framework is supported.

## Acceptance Criteria

- [ ] Agents built with the Claude Code Agent SDK can be deployed and operated through LlamaStack on OpenShift AI
- [ ] Real-time token streaming delivers incremental agent responses to users without requiring full response completion
- [ ] Multi-turn agent conversations maintain context server-side, allowing the Claude SDK to conduct tool-calling workflows without re-transmitting full conversation history each request
- [ ] Claude SDK tool definitions (including computer, text_editor, and bash tools) are interoperable with LlamaStack's tool-calling capabilities
- [ ] Agent sessions can be resumed after a network interruption using a persistent session identifier

## Success Criteria

- Context persistence verified via successful 5+ turn conversations where LlamaStack retains state across turns without SDK-side overhead
- Tool-call interoperability verified for Claude SDK's computer, text_editor, and bash tool definitions
- Streaming Time to First Token under 200ms
- Ability to resume a session via session_id after a network disconnect
