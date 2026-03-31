---
rfe_id: RHAIRFE-1580
title: Autoscaling Support for Elastic Ray Clusters via SDK
priority: Normal
status: Ready
size: M
parent_key: null
---
## Problem Statement

Users managing Ray clusters through the SDK can only configure static cluster sizes, requiring manual intervention to resize clusters as workload demands change. This creates three compounding problems:

1. **Resource waste from over-provisioning**: During low-demand periods, clusters run at full size with idle workers consuming expensive GPU and CPU resources. There is no ability to scale down or scale to zero when clusters are idle.

2. **Performance bottlenecks from under-provisioning**: During peak loads, statically-sized clusters cannot absorb demand spikes, leading to long job queue times and degraded throughput.

3. **Operational burden**: Platform teams must manually monitor utilization and resize clusters, which is error-prone, slow to react, and unsustainable for organizations running multiple Ray clusters across teams.

80% of Ray workloads have variable resource needs but are currently running on static clusters.

## Affected Customers

- **Fintech Analytics** — runs large GPU training jobs with highly variable demand; currently over-provisions to avoid disruption, driving up infrastructure costs.
- **MedAI Corp** — operates batch inference workloads with spiky traffic patterns; experiences long queue times during peaks and pays for idle resources between bursts.
- **DataScale Inc.** — runs a multi-tenant Ray platform and needs per-tenant cost controls; static clusters make cost attribution and optimization impossible at scale.
- **Internal platform engineering teams** — manage shared Ray infrastructure and bear the operational burden of manual cluster sizing across multiple environments.

Multiple enterprise prospects have cited the lack of autoscaling as a blocker for adoption.

## Business Justification

- **60% reduction in infrastructure costs** via scale-to-zero and right-sizing during low-demand periods.
- **90% reduction in job queue time** during peak loads through automatic scale-up.
- **Zero manual intervention** for cluster sizing, eliminating operational toil for platform teams.
- Removes a key adoption blocker for enterprise customers evaluating the platform.

## Desired Outcome

Users should be able to configure Ray clusters through the SDK that automatically scale up and down based on actual workload demand, including the ability to scale to zero when idle. Specifically:

- Users can define minimum and maximum worker counts for a cluster, including setting `min_workers=0` to enable scale-to-zero.
- Users can specify autoscaling policies based on resource utilization (CPU, memory, GPU), workload signals (Ray task queue depth), or custom metrics sourced from Prometheus.
- Users can monitor the current scaling state of their cluster at runtime.
- Users can dynamically adjust autoscaling configuration on a running cluster without needing to tear down and recreate it.
- Clusters automatically scale up and down based on the configured policies without manual intervention.

## Success Criteria

1. Users can configure `min_workers` and `max_workers` parameters when creating a cluster through the SDK, including `min_workers=0` for scale-to-zero.
2. An autoscaling configuration model is available that supports resource-based scaling policies (CPU/memory/GPU utilization thresholds), workload-based scaling policies (Ray task queue depth), and custom metrics policies via Prometheus.
3. Users can call a status method to monitor current scaling state (current worker count, scaling decisions, policy evaluations).
4. Users can call an update method to dynamically adjust autoscaling configuration at runtime on a running cluster.
5. Clusters automatically scale up and down based on configured policies without requiring manual intervention.
