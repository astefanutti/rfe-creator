---
rfe_id: RFE-001
title: Day 0 Notebook Readiness for NVIDIA Vera Rubin NVL72
priority: Critical
status: Ready
size: M
parent_key: null
---
## Customer Problem

Data scientists and ML engineers using OpenShift AI notebooks on NVIDIA Vera Rubin NVL72 hardware cannot be confident that the notebook environment will work correctly without manual configuration. Today, the v2025.1 "Jupyter | PyTorch | CUDA | Python 3.12" notebook image ships with CUDA 13.0 and basic GPU detection works, but three gaps remain:

1. **No formal validation on Vera Rubin silicon** — The existing CUDA 13.0 notebook image has not been tested or certified against Vera Rubin GPUs. Data scientists cannot trust that PyTorch kernels, multi-GPU communication, and CUDA runtime behavior are correct on this architecture without explicit validation.

2. **No ARM (aarch64) notebook image for the Vera CPU** — The Vera Rubin platform uses an ARM-based CPU. Today, notebook images are x86-only. Data scientists on Vera Rubin NVL72 cannot launch notebooks natively on the Vera CPU without a multi-arch image variant.

3. **No guaranteed driver/toolkit alignment with NVIDIA's Vera Rubin software stack** — Without explicit alignment with NVIDIA's recommended driver versions, CUDA toolkit, and PyTorch builds for Vera Rubin, users risk driver mismatches, silent correctness errors, or degraded performance.

These gaps mean the OpenShift AI developer experience layer is incomplete at Vera Rubin launch, forcing data scientists to manually configure their environments or risk unreliable behavior — undermining the "Day 0 readiness" promise of the OpenShift for NVIDIA partnership.

## Affected Customers

- **Enterprise organizations** deploying OpenShift for NVIDIA infrastructure for AI/ML workloads
- **Neo-cloud providers** building GPU-as-a-service offerings on Vera Rubin hardware
- **Sovereign cloud operators** requiring validated, certified AI platforms on latest-generation hardware
- **Data science teams** using OpenShift AI notebooks as their primary development environment on NVIDIA GPUs
- **NVIDIA** as a strategic partner expecting Day 0 ecosystem readiness across the OpenShift for NVIDIA stack

## Business Justification

Day 0 GPU support in notebooks is table stakes for the OpenShift for NVIDIA partnership stack. Notebook images are the primary entry point for data scientists on OpenShift AI — they are where users first experience GPU-accelerated development. Without Vera Rubin readiness at launch, the entire developer experience layer of the stack is incomplete, creating a visible gap in the OpenShift for NVIDIA value proposition.

This is a strategic investment directly aligned with NVIDIA Vera Rubin milestones and the OpenShift for NVIDIA "fast lane" program. Failing to deliver validated notebook images at Vera Rubin launch would:

- Break the Day 0 readiness commitment to NVIDIA and joint customers
- Force data scientists into manual environment setup, degrading the managed notebook experience
- Create a gap in the OpenShift for NVIDIA stack visible to enterprise buyers evaluating the platform
- Risk losing early Vera Rubin adopters to competitors with validated notebook environments

## Desired Outcome

When Vera Rubin NVL72 hardware becomes available, data scientists should be able to launch an OpenShift AI notebook and immediately begin GPU-accelerated development — with no manual environment configuration, no driver troubleshooting, and no uncertainty about hardware compatibility. Specifically:

- **Notebooks launch and GPUs are detected automatically** — Data scientists open a PyTorch notebook on Vera Rubin NVL72 and GPUs are recognized and usable without any manual steps.
- **Training and inference workloads run correctly** — PyTorch workloads, including multi-GPU training, execute on Vera Rubin GPUs with correct results and expected performance, matching the experience on prior NVIDIA architectures.
- **Notebooks run natively on the Vera ARM CPU** — Data scientists on Vera Rubin NVL72 can launch notebooks that run natively on the ARM-based Vera CPU, without requiring x86 emulation or workarounds.
- **The software stack is aligned with NVIDIA's Vera Rubin releases** — Driver versions, CUDA toolkit, and framework builds are compatible with NVIDIA's Vera Rubin software stack, eliminating silent correctness errors or compatibility surprises.
- **Documentation guides users through the transition** — Users migrating from Grace Blackwell (prior architecture) have clear guidance on what has changed, including driver requirements and CUDA version updates.

## Scope

**This RFE covers:** Day 0 readiness of the PyTorch CUDA notebook image for the Vera Rubin NVL72 platform, including GPU validation, native ARM CPU support, and NVIDIA software stack alignment. This is the MVP notebook experience — the primary image that data scientists use on OpenShift AI.

**Non-MVP (stretch):** Additional notebook image variants (e.g., TensorFlow), additional acceleration libraries (TensorRT, cuDNN updates).

**Out of scope:** CUDA 14.x support, non-notebook components (inference server, llm-d), x86-only Rubin NVL8 configuration, custom user-built notebook images, non-OpenShift for NVIDIA platforms.

## Success Criteria

1. Data scientists can launch the PyTorch CUDA notebook on OpenShift for NVIDIA with Vera Rubin NVL72 hardware and begin GPU-accelerated development without manual environment configuration
2. Vera Rubin GPUs are automatically detected and usable for training and inference workloads from within notebooks
3. Multi-GPU workloads execute correctly across Vera Rubin GPUs
4. Notebooks run natively on the ARM-based Vera CPU without x86 emulation
5. The notebook software stack is aligned with NVIDIA's recommended driver and toolkit versions for Vera Rubin
6. The validated notebook image is available in the OpenShift AI image catalog at Vera Rubin launch milestones (Tech Preview June 2026, GA October 2026)
7. Documentation covers Vera Rubin support details, driver requirements, and migration guidance from Grace Blackwell to Vera Rubin

## Timeline Alignment

- **Tech Preview**: June 2026 (aligned with NVIDIA Vera Rubin Tech Preview)
- **GA**: October 2026 (aligned with NVIDIA Vera Rubin GA)
