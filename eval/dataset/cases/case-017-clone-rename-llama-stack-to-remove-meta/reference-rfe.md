---
rfe_id: RFE-001
title: Rename Llama Stack to a community-owned name before RHOAI 3.5 GA
priority: Critical
status: Ready
size: L
parent_key: null
---
## Problem Statement

RHOAI enterprise customers, partners, and the open-source community need to adopt and build on RHOAI's agentic AI framework under a stable, community-owned project identity that reflects Red Hat's independent stewardship — not Meta's trademark. The current name "Llama Stack" ties the project to a company that has pulled back its investment, creating confusion about ownership, long-term governance, and whether the project has an independent future.

At GA, the project name will become embedded across the entire customer-facing surface — Kubernetes CRDs, container image names in registry.redhat.io, Python import paths, CLI commands, API endpoint paths, Helm charts, Quick Start templates, partner integrations, and operational runbooks. Once GA ships, a rename becomes a breaking change affecting every customer, partner, and community user, requiring deprecation cycles, migration tooling, and extensive documentation rewrites. Establishing a community-owned identity before GA avoids this cost entirely and gives customers a stable foundation to build on from day one.

## Affected Customers

- **RHOAI enterprise customers** adopting agentic AI workloads who will build automation, integrations, and operational procedures around the project name at GA
- **Partners** integrating with the Responses API and OpenAI-compatible APIs whose tooling and documentation will reference the project name
- **Upstream open-source community** contributors and users building on the project who need clarity on project identity and governance

## Business Justification

1. **Brand independence**: Removing dependency on Meta's Llama trademark protects Red Hat's independent brand identity and avoids long-term legal and marketing risk tied to another company's trademark decisions.
2. **Pre-GA cost advantage**: Renaming before GA is dramatically cheaper than after. Post-GA rename costs include deprecation cycles (minimum one release), customer migration guides, breaking changes across integrations, extensive documentation rewrites, and partner notification campaigns. Pre-GA, there is no installed base to migrate.
3. **Ownership clarity**: Red Hat is the primary driver of the codebase and community. The project identity should reflect that ownership, not create confusion about Meta's involvement or control.
4. **Legal risk mitigation**: Shipping a GA product under another company's trademark creates ongoing legal exposure around trademark usage rights, licensing terms, and brand association that Red Hat does not control.

## Scope

A coordinated rename initiative spanning all upstream and downstream surfaces before RHOAI 3.5 GA:

- **Upstream**: Repository names, package names, Python import paths, CLI command names, API endpoint paths, MCP server tool names
- **Downstream RHOAI operator**: CRD names and API group names, Kubernetes namespace names, container image names in registry.redhat.io, Helm chart names and values
- **Documentation**: All GA documentation, Quick Start templates, API references, tutorials
- **CI/CD**: Pipeline configurations, integration test suites, build scripts
- **Community**: Blog post or announcement explaining the rename and migration path, updated community communications and governance docs
- **Backward compatibility**: Old names aliased for at least one release cycle to support early adopters and community users during transition

The new name must be selected via an open community process and cleared by Red Hat legal for trademark availability.

## Success Criteria

1. New name selected via open community process and cleared by Red Hat legal for trademark availability, giving the project a stable, community-owned identity
2. Customers and partners can adopt RHOAI's agentic AI framework at GA without exposure to future breaking name changes — zero instances of "llama" or "llamastack" in the Kubernetes API surface, container image names, or customer-facing documentation (except explicit migration/context notes)
3. Early adopters and community users experience a smooth transition — old names aliased for one release cycle with deprecation warnings pointing to the new identity
4. Community and partner confidence in Red Hat's stewardship is reinforced through a published announcement explaining the rename rationale and migration path
5. The renamed project is fully functional and validated — all CI/CD pipelines and integration test suites pass under the new name
6. No customer-facing material ships at GA with the old name as the primary reference
