---
rfe_id: RFE-001
title: AutoGluon as a supported model serving runtime in OpenShift AI
priority: Normal
status: Ready
size: M
parent_key: null
---
## Problem Statement

Enterprise users who train AutoML models with AutoGluon face a deployment experience that contradicts the framework's core promise of simplicity. While AutoGluon makes model training accessible to citizen data scientists and data analysts without deep ML expertise, deploying those models on Red Hat OpenShift AI requires Kubernetes-level skills: manually obtaining a KServe-compatible container image, navigating to Settings > Serving runtimes, and authoring complex ServingRuntime YAML that demands knowledge of KServe specifications, API protocols, and resource configuration. The resulting custom runtime is explicitly marked as "unsupported" by Red Hat, which is an enterprise adoption blocker for organizations that require vendor-backed support for production workloads.

This stands in stark contrast to the deployment experience for vLLM, OpenVINO, and Triton, which are pre-configured, officially supported runtimes available via a simple dropdown selection in the OpenShift AI dashboard.

## Business Justification

The AutoML market is projected to reach $14.5B by 2030, and tabular data represents over 70% of enterprise ML use cases — the exact domain where AutoGluon excels. Enterprise customers in financial services (fraud detection, credit scoring), healthcare (patient outcome prediction), retail (demand forecasting, churn prediction), and manufacturing (predictive maintenance) are choosing AutoGluon for its ability to democratize ML model training for non-ML-expert users.

However, the deployment gap undermines the value proposition:

- **Deployment friction**: Each AutoGluon model deployment requires 2-4 hours of manual configuration involving Kubernetes and KServe expertise — skills that citizen data scientists and data analysts typically do not have.
- **Unsupported status**: Enterprise customers with strict compliance and support requirements cannot adopt custom runtimes that are explicitly marked as unsupported by Red Hat. This blocks production deployment entirely for these organizations.
- **Competitive gap**: Competing ML platforms offer streamlined deployment for AutoML frameworks. The lack of native AutoGluon support in OpenShift AI creates a gap that drives ease-of-use-focused users to alternative platforms.
- **Partner and ISV friction**: ISVs and partners building AutoML solutions on OpenShift AI face the same deployment barriers, limiting the ecosystem growth potential.

Natively supporting AutoGluon eliminates these barriers, increases platform adoption among ease-of-use-focused users, and positions OpenShift AI as the enterprise platform for the full ML lifecycle — from training through production serving.

## Affected Customers

- Data analysts and citizen data scientists at enterprise organizations in financial services, healthcare, retail, and manufacturing who use AutoGluon for tabular prediction tasks
- ISVs and partners building AutoML-powered solutions on OpenShift AI
- ML platform teams at enterprises who currently spend engineering effort creating and maintaining unsupported custom serving runtimes for AutoGluon

## Desired Outcome

Users can deploy AutoGluon models on OpenShift AI with the same streamlined, fully supported experience available today for vLLM, OpenVINO, and Triton — selecting a runtime from a dropdown, specifying a model location, and clicking Deploy — with no YAML authoring, no Kubernetes expertise, and full Red Hat support coverage.

## Success Criteria

- AutoGluon appears as a selectable serving runtime in the OpenShift AI dashboard runtime selection dropdown, alongside existing supported runtimes (vLLM, OpenVINO, Triton)
- Users can deploy an AutoGluon TabularPredictor model by selecting the AutoGluon runtime, pointing to a model storage location, and clicking Deploy — no manual YAML authoring required
- A Red Hat-supported AutoGluon serving runtime artifact is published and maintained with ongoing updates
- The AutoGluon runtime is listed in the Red Hat OpenShift AI Supported Configurations document and included in Red Hat support scope
- Official documentation is available, including a deployment guide, worked examples, API reference, and troubleshooting guidance
- Existing custom AutoGluon serving runtimes continue to function (backward compatibility is preserved)

## Scope Notes

This request focuses on a single need: adding AutoGluon as a pre-configured, officially supported serving runtime. Initial GA scope covers:

- **Model types**: Tabular models — regression, binary classification, multiclass classification, and time series forecasting
- **I/O format**: CSV input / JSON output
- **Serving pattern**: Single-model deployment per endpoint
- **API protocol**: REST

Areas explicitly outside initial scope (potential future enhancements): multi-model serving, GPU acceleration, gRPC protocol, multimodal AutoGluon models, and model monitoring/drift detection integration.
