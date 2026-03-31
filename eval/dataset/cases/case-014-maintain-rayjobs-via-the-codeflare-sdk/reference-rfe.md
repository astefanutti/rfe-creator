---
rfe_id: RFE-001
title: Maintain RayJobs via the CodeFlare SDK
priority: Normal
status: Ready
size: M
parent_key: null
---
## Customer Problem

Data scientists using the CodeFlare SDK on Red Hat OpenShift AI (RHOAI) must currently follow a multi-step, error-prone workflow to run distributed Ray jobs: create a Ray Cluster, submit a job, monitor the job, and then manually tear down the cluster after completion. This process has several problems:

1. **Resource waste from orphaned clusters**: Users frequently forget to tear down Ray Clusters after their jobs complete, leaving idle clusters consuming expensive compute resources (GPUs, CPUs, memory) indefinitely.

2. **Unnecessary complexity**: The cluster-then-job workflow forces data scientists to manage infrastructure concerns (cluster provisioning, scaling, teardown) rather than focusing on their core work of developing and running training jobs.

3. **Inconsistent user experience**: The Kubeflow Training Operator (KFTO) already offers a simplified job-centric paradigm where users submit a job and the infrastructure lifecycle is handled automatically. The CodeFlare SDK's Ray workflow lags behind this experience, creating an inconsistent and confusing developer experience within the same platform.

## Affected Customers

- **Red Hat OpenShift AI (RHOAI) users** running distributed Ray workloads
- **Enterprise data science teams** using the CodeFlare stack for distributed training and inference
- **Partners** building distributed AI/ML solutions on OpenShift who leverage the CodeFlare SDK

## Business Justification

This is a strategic investment to improve the CodeFlare SDK user experience and reduce cloud resource waste from orphaned Ray Clusters. The current multi-step workflow is a friction point in enterprise AI/ML platform deals where competing platforms offer simpler job submission experiences. Aligning RHOAI's distributed compute story with the simplified job-centric paradigm already adopted by KFTO strengthens competitive positioning and delivers a consistent user experience across all distributed compute mechanisms in the platform.

The resource waste problem is particularly impactful for enterprise customers running GPU workloads, where forgotten clusters can cost thousands of dollars per day in cloud environments.

## What We Need

Users need the ability to create and manage RayJob custom resources directly through the CodeFlare SDK, enabling a simplified workflow where they submit a job and the cluster lifecycle is handled automatically. Specifically:

1. **Direct RayJob support in the SDK**: Users should be able to define and submit RayJobs through the CodeFlare SDK without needing to first create and manage a separate Ray Cluster. The SDK should support creation, status monitoring, listing, and deletion of RayJob resources.

2. **Automatic cluster lifecycle management**: When a user submits a RayJob, the underlying Ray Cluster should be provisioned automatically and cleaned up after job completion, eliminating the risk of orphaned clusters wasting resources.

3. **Integration with existing platform capabilities**: RayJobs created through the SDK should work with existing Kueue integration for queuing and quota management, and integrate with the broader RHOAI platform (dashboard visibility, authentication, etc.).

4. **Sensible defaults for common use cases**: Users who want to run standard training jobs should not need to build custom Ray images or write extensive boilerplate configuration. The SDK should provide defaults that cover the most common distributed training scenarios.

## Success Criteria

- Users can create and manage RayJobs directly through the CodeFlare SDK without manually provisioning Ray Clusters
- The job lifecycle follows a simple pattern: Job created -> Running -> Completed/Failed
- Ray Clusters are automatically cleaned up after job completion, eliminating resource waste from orphaned clusters
- RayJobs created through the SDK integrate with Kueue for queuing and quota management
- The workflow is consistent with the job-centric experience provided by KFTO
