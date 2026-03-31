---
rfe_id: RFE-001
title: Unified MLflow and Infrastructure Observability for RHOAI
priority: Normal
size: M
status: Ready
parent_key: null
---
## Summary

Enterprise RHOAI customers running multi-tenant MLflow need a unified observability experience where MLflow experiment metrics and infrastructure metrics are viewable together. Today, data scientists and platform administrators must context-switch between disconnected tools to understand training performance and infrastructure health, creating friction that blocks production ML adoption at scale.

## Problem Statement

Data scientists cannot see MLflow training metrics (loss, accuracy, custom metrics) alongside infrastructure metrics (GPU utilization, memory pressure) in a single correlated timeline. When a training run underperforms, they cannot determine whether the root cause is a code issue or resource contention without manually cross-referencing the MLflow UI with separate infrastructure dashboards. This constant context-switching slows experimentation velocity and makes troubleshooting unreliable.

Platform administrators have no visibility into MLflow server health, storage consumption, or per-tenant usage from the centralized monitoring stack. On shared multi-tenant clusters, this means capacity planning and troubleshooting of the MLflow infrastructure itself is guesswork — administrators cannot proactively identify tenants consuming disproportionate resources, detect degraded MLflow server performance, or forecast storage growth.

## Affected Customers

Enterprise RHOAI customers running shared multi-tenant clusters, including:

- **NatWest Group** ML Platform team — flagged inability to correlate training and infrastructure metrics as friction during expansion discussions
- **Siemens AI Factory** — production ML platform requiring unified monitoring as a baseline expectation
- **Deutsche Telekom** data science division — raised observability gaps during POC evaluations

Multiple large accounts have identified this as a friction point during POCs and expansion deals. Unified monitoring is a table-stakes expectation for production ML platforms in the enterprise segment.

## Business Justification

This is a core platform observability gap blocking enterprise RHOAI adoption at scale:

- **Revenue impact**: Multiple large accounts (NatWest Group, Siemens, Deutsche Telekom) have flagged this gap as friction during POCs and expansion deals. Removing this friction directly supports deal progression and platform stickiness.
- **Competitive positioning**: Production ML platforms from competing vendors offer integrated experiment-to-infrastructure observability. The absence of this capability positions RHOAI as incomplete for enterprise production workloads.
- **Operational cost**: Without unified monitoring, platform teams at customer sites build ad-hoc workarounds to correlate metrics manually, increasing support burden and reducing confidence in the platform.

## Acceptance Criteria

- [ ] Data scientists can view MLflow training metrics (loss, accuracy, custom metrics) alongside infrastructure metrics (GPU utilization, memory) on a single correlated timeline, linked by run ID and timestamp
- [ ] MLflow server operational health is observable from the platform's centralized monitoring, including request latency, active experiments, and storage usage per tenant
- [ ] Platform administrators can identify per-tenant MLflow resource consumption from the centralized monitoring view
- [ ] Documentation covers how data scientists and platform administrators access unified MLflow and infrastructure observability

## Success Criteria

- Data scientists can view training metric trends and infrastructure metric trends on a single correlated timeline for any given MLflow run, eliminating the need to cross-reference separate tools
- Platform administrators can monitor MLflow server health and per-tenant resource consumption from the centralized monitoring stack, enabling proactive capacity management
- Time to diagnose training performance issues is measurably reduced by eliminating the context-switching overhead between MLflow UI and infrastructure dashboards

## Scope

### In Scope

- Making MLflow experiment and run training metrics available in the platform's centralized monitoring alongside infrastructure metrics
- Making MLflow server operational health and per-tenant usage observable from centralized monitoring
- Correlation of training metrics with infrastructure metrics by run ID and timestamp
- Documentation for unified MLflow observability setup

### Out of Scope

- Metrics collection infrastructure deployment and configuration (separate RFE)
- Tenant-scoped metric access control and query isolation (separate RFE)
- ML model drift and bias monitoring (separate RFE)
