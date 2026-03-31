---
rfe_id: RFE-001
title: Rename Red Hat OpenShift AI Operator to Red Hat AI Operator to reflect broader
  portfolio scope
priority: Normal
status: Ready
size: M
parent_key: null
---
## Customer Problem

Platform Operators deploying Red Hat AI portfolio products encounter an operator named "Red Hat OpenShift AI" that implies it is specific to OpenShift. As the Red Hat AI portfolio expands to include products like Red Hat AI Inference Server (RHAIIS) with distributed inference across both xKS and OpenShift, this naming creates confusion about the operator's scope and purpose. The current name blocks natural reuse of the existing operator for new AI products without creating a misleading product identity, and forces a false choice between maintaining a confusingly named operator or building and maintaining an entirely separate operator for each new product.

## Affected Customers

- **Platform Operators** deploying Red Hat AI portfolio products on OpenShift who need a single, coherent operator experience across the expanding AI product line
- **Enterprises running RHOAI on OpenShift** looking to adopt RHAIIS and future AI products without confusion about operator scope or product relationships
- **Red Hat partners** integrating with the AI operator ecosystem who need consistent, portfolio-aligned naming to build and market their integrations

## Business Justification

A portfolio-aligned operator name reduces onboarding friction for Platform Operators deploying new products and supports a coherent product identity as the Red Hat AI portfolio grows beyond OpenShift-specific tooling. Without this rename, Red Hat faces two costly alternatives: (1) maintain a confusingly named operator that undermines product messaging, or (2) create and maintain a separate operator for RHAIIS on OpenShift, increasing net new development work and ongoing support burden. This rename enables the existing operator to serve as the foundation for the broader AI portfolio, aligning operator identity with product strategy.

## Desired Outcome

Platform Operators experience a consistent "Red Hat AI" identity across all operator touchpoints — installation, configuration, monitoring, and documentation — with no evidence of legacy "Red Hat OpenShift AI" naming. Existing RHOAI installations upgrade seamlessly to RHAI without redeploying managed workloads or requiring manual Custom Resource migration. Platform Operators can confirm rename completion and operator health through their existing monitoring and observability tooling.

## Success Criteria

1. Platform Operators encounter no legacy RHOAI naming across any customer-facing operator interactions, including installation, configuration, CLI usage, monitoring, and documentation
2. Existing RHOAI installations can upgrade to RHAI without redeploying managed workloads
3. Existing Custom Resources created under RHOAI continue to reconcile after upgrade without manual migration
4. Metrics, distributed traces, and telemetry reflect the new naming convention
5. Platform Operators can confirm rename completion and operator health from existing monitoring
6. Installation guide, upgrade guide, and CRD reference documentation updated to reflect the new name with explicit transition steps
