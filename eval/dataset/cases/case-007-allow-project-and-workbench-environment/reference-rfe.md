---
rfe_id: RFE-001
title: Allow workbench environment variables to reference existing Kubernetes Secrets
  and Config Maps
priority: Normal
size: M
status: Ready
parent_key: null
---
## Summary

Data scientists using RHOAI workbenches cannot attach existing Kubernetes Secrets or Config Maps to their workbenches through the dashboard UI. Organizations that manage secrets centrally using external secret management solutions (e.g., External Secrets Operator with HashiCorp Vault) are forced to either duplicate secret values manually into the dashboard or edit the Notebook CR YAML directly, bypassing the dashboard entirely. The workbench environment variables UI needs to support selecting existing secrets and config maps from the project namespace, not just creating new ones inline.

## Problem Statement

The RHOAI dashboard's workbench environment variables form only supports creating new inline secrets and config maps. There is no option to reference secrets or config maps that already exist in the namespace. This creates two painful workarounds for users:

1. **Manual duplication**: Data scientists copy secret values from externally managed secrets into the dashboard's inline secret creation form. This breaks centralized secret management — values drift, rotation is missed, and raw secret values are exposed to users who should never see them.

2. **Direct YAML editing**: Platform engineers edit the Notebook CR directly to add `envFrom.secretRef` entries. These references are invisible in the dashboard UI, making it appear that no environment variables are configured. Other team members cannot see or manage these references through the dashboard.

Both workarounds defeat the purpose of centralized secret management and undermine the value proposition of the dashboard as the primary interface for workbench management. Additionally, secrets created inline for one workbench cannot be reused in another workbench within the same project without re-entering the values manually.

## Affected Customers

- **Airbus** — raised a formal support case specifically about this limitation
- **Multiple enterprise accounts** — flagged by sales teams as a friction point in deals; organizations using External Secrets Operator with HashiCorp Vault backends are particularly affected
- **Enterprise segment broadly** — organizations with mature secret management workflows (ESO, GitOps/ArgoCD, Vault) encounter this gap when adopting RHOAI workbenches

## Business Justification

Multiple active sales engagements have surfaced this limitation as a blocker to RHOAI adoption. Airbus has filed a formal support case, indicating this is not a theoretical gap but a concrete barrier for a named customer. Enterprises with established secret management practices cannot reconcile their security workflows with the RHOAI dashboard's inline-only secret creation model, creating friction that reduces platform credibility and slows deal progression. The inability to consume externally managed secrets through the dashboard forces organizations to choose between their security practices and using the RHOAI workbench UI.

## Acceptance Criteria

- [ ] Users can select existing Kubernetes Secrets from a namespace-scoped list when adding environment variables to a workbench
- [ ] Users can select existing Config Maps from a namespace-scoped list when adding environment variables to a workbench
- [ ] Secrets managed by external controllers (e.g., External Secrets Operator, ArgoCD) appear in the selection list without requiring special labels
- [ ] The UI displays secret keys (not secret values) so users understand which environment variables will be injected
- [ ] When editing a workbench, the UI shows which existing secrets and config maps are already attached
- [ ] Secrets and config maps created for one workbench can be reused in another workbench within the same project through the same selection mechanism

## Success Criteria

- Data scientists can consume externally managed secrets without ever seeing raw secret values, preserving centralized secret management workflows
- Platform teams can manage secrets through their existing tooling (ESO, Vault, ArgoCD) and have those secrets consumable in RHOAI workbenches through the dashboard
- The dashboard remains the single pane of glass for workbench configuration — no need to drop to YAML editing for secret attachment
