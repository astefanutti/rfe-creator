---
rfe_id: RFE-001
title: Native Experiment Tracking Integration for ML Workloads
priority: Normal
status: Ready
size: M
parent_key: null
---
## Problem Statement

Data scientists running distributed training jobs have no SDK-level integration with experiment tracking systems. Each team must independently configure tracking servers (MLflow, Weights & Biases, etc.), manually inject credentials into job environments, manage artifact storage, and wire up callbacks to training frameworks. There is no standardized approach through our SDK, resulting in:

- **Inconsistent setups across teams** — every team reinvents experiment tracking configuration, leading to fragile, non-reproducible configurations that break when jobs move between environments or scale up.
- **Broken tracking in production** — manual credential injection and environment variable management is error-prone, causing silent tracking failures that go undetected until experiments need to be reproduced.
- **Significant time wasted on boilerplate** — data scientists spend time debugging infrastructure plumbing instead of developing and iterating on models.

## Affected Customers

- **Databricks ML Platform team** — managing experiment tracking across large-scale distributed training workloads.
- **JPMorgan Chase AI Research group** — requires reliable, auditable experiment tracking for regulated AI/ML research.
- **Spotify ML Engineering** — running distributed training at scale with need for consistent tracking across teams.
- **Recursion Pharmaceuticals data science division** — needs standardized experiment tracking for drug discovery ML pipelines.

## Business Justification

- 95% of ML teams use experiment tracking, making the lack of native integration a top friction point during onboarding.
- Multiple enterprise prospects (estimated $3.5M pipeline) have flagged native experiment tracking integration as a requirement for adoption.
- Expected 60% reduction in experiment tracking setup time across teams.
- Expected shift from manual, ad-hoc tracking configuration to fully automated, cluster-level tracking — eliminating an entire category of setup toil.

## Desired Outcome

Users should be able to specify a tracking backend and its configuration at the platform or environment level, and all training jobs should automatically have access to the tracking backend without any manual per-job setup.

The integration should:

1. **Support common tracking backends** — at minimum MLflow, Weights & Biases, TensorBoard, and Ray's native tracking capabilities.
2. **Enable centralized configuration** — tracking backend selection and configuration should be specified once at the platform or environment level and automatically propagated to all jobs.
3. **Automate credential provisioning** — training jobs should have seamless access to the tracking backend's authentication and storage configuration without manual per-job setup by the user.
4. **Integrate with training frameworks** — experiment parameters, metrics, and artifacts should be tracked automatically during distributed training without requiring users to add tracking code to their training scripts.
5. **Support extensibility** — teams should be able to register custom tracking backends through a public API when the built-in backends do not meet their needs.

## Success Criteria

- A user can specify a tracking backend (e.g., MLflow, W&B) and its connection details at the platform or environment level, and all training jobs automatically have access to the tracking backend — zero manual per-job setup required.
- Custom tracking backends can be registered and used via a documented public API.
- Experiment parameters, metrics, and artifacts are tracked automatically during distributed training without requiring users to add tracking code to their training scripts.
- Setup time for experiment tracking is reduced by at least 60% compared to the current manual process.
