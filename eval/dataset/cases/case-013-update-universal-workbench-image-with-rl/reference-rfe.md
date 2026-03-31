---
rfe_id: RFE-001
title: Seamless RLVR Training Workflow Support in Workbenches
priority: Normal
status: Draft
size: M
parent_key: null
---
## Affected Customers

- RHOAI enterprise customers using Training Hub for fine-tuning and alignment workflows
- Internal AI/ML platform teams adopting RLVR for model alignment
- Partners integrating with OpenShift AI for LLM training pipelines

## Business Justification

Reinforcement Learning from Verifiable Rewards (RLVR) is a key emerging capability for LLM alignment, and Training Hub 0.5+ exposes it as a supported workflow. Without pre-packaged dependencies in the universal workbench image, adoption is hampered by setup friction. Example notebooks that fail out-of-the-box create a poor first impression and undermine confidence in the platform. Ensuring seamless RLVR support strengthens RHOAI's competitive positioning in the enterprise AI training market and accelerates customer time-to-value.

## User Problem

Users who want to develop and experiment with LoRA adapter-based RLVR training must manually install dependencies into their workbench environments. This causes:

1. **Setup friction and wasted time** — Users spend time debugging environment setup instead of training models
2. **Inconsistent dependency versions** — Different users and deployments end up with different library versions, leading to unreproducible results and hard-to-diagnose failures
3. **Poor discoverability** — RLVR capabilities are not surfaced through the workbench, so users may not realize the platform supports these workflows
4. **Broken example notebooks** — RLVR example notebooks fail to run without additional manual installation steps, creating a poor onboarding experience

## Scope

Update the RHOAI universal workbench image to bundle all RLVR dependencies that Training Hub exposes for RLVR workflows. This is a single focused need with the following key considerations:

- Ensure compatibility across CUDA, ROCm, and CPU backends
- Maintain compatibility with existing Training Hub 0.5+ and Kubeflow SDK dependencies
- Keep the image size increase reasonable and justified
- Publish all required RLVR dependencies to AIPCC indexes

### Out of Scope

- Changes to RLVR training logic or Training Hub APIs
- New notebook creation (existing example notebooks should work; new content is separate)
- Changes to workbench UI or launcher

## Success Criteria

1. Users can run RLVR training workflows immediately on a fresh workbench without any manual dependency installation
2. Example RLVR notebooks execute successfully out-of-the-box on a new workbench instance
3. Dependencies work correctly across CUDA, ROCm, and CPU backends
4. No dependency conflict reports from users after image update
5. All required RLVR dependencies are published to AIPCC indexes
6. Documentation is updated to reflect the included RLVR capabilities
