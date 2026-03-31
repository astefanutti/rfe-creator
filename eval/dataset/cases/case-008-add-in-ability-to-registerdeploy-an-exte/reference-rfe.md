---
rfe_id: RFE-001
title: Dashboard UI for registering and managing external MaaS model endpoints
priority: Normal
status: Ready
size: M
parent_key: null
---
## Affected Customers

Enterprise platform admin teams adopting RHOAI MaaS for governed AI model access — large financial services, healthcare, and technology companies running OpenShift AI at scale. Examples include major banks using Azure OpenAI through MaaS governance and Fortune 500 companies standardizing on RHOAI for multi-provider LLM access.

## User Problem

Platform administrators who need to register external model endpoints (such as OpenAI, Anthropic, Azure OpenAI, Bedrock, and Vertex AI) as MaaS-governed models must currently use kubectl and manually create MaaSModelRef CRDs via the CLI. There is no dashboard support for this workflow.

This creates several problems:

- **No discoverability**: There is no way for admins to see from the dashboard which external providers are currently configured, making it difficult to audit or manage the registered model landscape.
- **No UI-based lifecycle management**: Admins cannot update or remove external model registrations from the dashboard — every change requires CLI access and Kubernetes knowledge.
- **Confusion for AI engineers**: AI engineers using Application AI Engineering (AAE) cannot easily distinguish configured external MaaS models from other endpoint types (such as Custom Endpoints), making it harder to find and consume the right governed models.
- **Barrier to MaaS adoption**: CLI-only registration is a significant barrier to platform admin productivity and reduces the discoverability of MaaS capabilities, undermining enterprise adoption of governed model access.

This need is fundamentally different from the existing Custom Endpoints feature. Custom Endpoints are unmanaged, ad-hoc connections without subscription binding or admin governance. MaaS external model registration requires admin ownership, MaaS subscription inclusion, and credential management at the MaaSModelRef level — capabilities that currently have no UI representation.

## Business Justification

This is a MaaS GA blocker. External model registration is a core MaaS admin workflow — without dashboard support, MaaS cannot be considered GA-complete because a fundamental management capability is only accessible via CLI. RHOAI 3.4 already supports external model registration via CLI and surfaces registered models in AAE, but the absence of dashboard UI creates an admin experience gap that directly undermines MaaS adoption in enterprise accounts.

Enterprise platform admin teams evaluating RHOAI for governed multi-provider LLM access — particularly in regulated industries such as financial services and healthcare — expect full dashboard management for governed model endpoints. CLI-only registration is a barrier in these environments because platform admins managing OpenShift AI at scale often lack direct kubectl access due to organizational security policies, and requiring CLI for a routine admin operation fragments the management experience across two surfaces. This friction delays MaaS onboarding and reduces the discoverability of MaaS external model capabilities for both admins and the AI engineers who consume them.

*Note: Specific named customer accounts and revenue impact data should be added by the product team to strengthen this justification.*

## What Needs to Happen

Platform admins need the ability to register, view, edit, and delete external MaaS model endpoint registrations directly from the Model Deployments page in the RHOAI dashboard.

The registration form needs to capture:
- Provider selection (e.g., OpenAI, Anthropic, Azure OpenAI, Bedrock, Vertex AI)
- Endpoint URL
- Model name/identifier
- Credential reference

MVP provider support should include OpenAI, Anthropic, and Bedrock, with remaining supported providers (Azure OpenAI, Vertex AI) as a stretch goal.

The existing CLI registration path must continue to work — this is additive UI, not a replacement. Models registered via CLI should appear in the dashboard, and vice versa.

## Dependencies and Constraints

- Depends on RHAISTRAT-1295 (External Model Egress via IGW) backend landing first — the UI cannot function without the underlying backend support for external model egress.
- UX design review and approval is required before implementation begins.
- Must not break or replace the existing CLI-based MaaSModelRef registration workflow.

## Success Criteria

- A platform admin can create a new external MaaS model registration from the dashboard, selecting provider, endpoint URL, model identifier, and credential reference.
- Registered external models appear in AAE for AI engineers with correct MaaS subscription access.
- A platform admin can view, edit, and delete existing external MaaS model registrations from the dashboard.
- UX is reviewed and approved by the design team before implementation.
