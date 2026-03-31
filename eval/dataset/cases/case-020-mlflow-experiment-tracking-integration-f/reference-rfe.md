---
rfe_id: RFE-001
title: MLflow Experiment Tracking Integration for Training Hub
priority: Normal
status: Ready
size: M
parent_key: null
---
## Customer Problem

Training Hub users currently have no integrated experiment tracking solution and resort to manually recording training run details — hyperparameters, metrics, model configurations, and results — in spreadsheets and notebooks. This manual bookkeeping creates several compounding problems:

1. **No central record of training runs.** Users track hyperparameters, metrics, and results in ad-hoc spreadsheets, leading to transcription errors, missing data, and inconsistent formatting across team members.

2. **Painful experiment comparison.** Comparing results across training runs requires manually aggregating data from multiple sources, which is time-consuming and error-prone. Users cannot quickly identify which combination of hyperparameters produced the best results.

3. **Lost institutional knowledge.** When revisiting experiments weeks or months later, users cannot reliably reconstruct what was tested, why specific choices were made, or what the exact training configuration was. This slows down iteration and leads to redundant work.

4. **Collaboration friction.** Sharing results with teammates requires sending files, screenshots, or copy-pasting data instead of linking to a live, interactive dashboard. This creates versioning confusion and makes peer review of experiments impractical.

5. **Reproducibility gaps.** Without automatic logging of all training parameters, environment details, and configuration, reproducing successful experiments is error-prone and unreliable. Users must manually reconstruct the exact setup, often incompletely.

These problems are estimated to cost each data scientist 2–4 hours per week in manual bookkeeping overhead.

## Affected Customers

- **Databricks enterprise customers** — Over 7,000 existing MLflow users who already have MLflow infrastructure deployed and expect seamless integration with their established tracking workflows.
- **Training Hub power users** — Data scientists and ML engineers running SFT, OSFT, and LoRA fine-tuning workflows who need structured experiment tracking to iterate effectively.
- **Enterprise ML teams** — Organizations such as Acme AI Labs, FinServ Analytics, and MedTech ML division that require standardized, auditable experiment tracking as part of their ML operations. These teams have explicitly identified the lack of MLflow integration as a gap blocking their adoption of Training Hub for production fine-tuning workflows.

This capability benefits 100% of the Training Hub user base, as every user running training workflows needs to track and compare experiments.

## Business Justification

- **Productivity gains.** Eliminating manual experiment bookkeeping saves an estimated 2–4 hours per data scientist per week, directly translating to faster model iteration and time-to-value.
- **Enterprise readiness.** MLflow is the industry-standard open-source experiment tracking platform with over 10 million downloads per month. Native integration signals enterprise maturity and removes a significant adoption blocker for organizations that have standardized on MLflow.
- **Accelerated enterprise adoption.** Compatibility with existing MLflow infrastructure across 7,000+ Databricks customers allows Training Hub to integrate into established ML workflows without requiring customers to change their tooling or processes.
- **Competitive positioning.** Lack of integrated experiment tracking is a gap relative to competing platforms. Native MLflow support addresses this gap with the most widely adopted standard rather than a proprietary solution. Without this integration, enterprise customers with existing MLflow infrastructure face a migration barrier that favors competitors offering native MLflow compatibility.

## Desired Outcome

Users can pass an `mlflow_tracking_uri` parameter to any Training Hub training function — `sft()`, `osft()`, or `lora_sft()` — and have all training metrics, hyperparameters, and run metadata automatically logged to their MLflow server with zero additional configuration or boilerplate code.

Specifically, when MLflow tracking is enabled:

- **Automatic metric logging.** Training loss, evaluation metrics, learning rate schedules, and other training signals are logged to the MLflow server at each logging step without user intervention.
- **Full hyperparameter capture.** All training configuration — model, dataset, learning rate, batch size, LoRA rank/alpha, and other algorithm-specific parameters — is logged as MLflow run parameters.
- **Run metadata.** Run name, experiment name, timestamps, and environment details are recorded for full traceability.
- **Distributed training support.** In multi-GPU and multi-node training scenarios, training metrics are logged exactly once per step without duplicate entries or conflicts.
- **Coexistence with existing loggers.** MLflow integration works alongside existing logging backends (Weights & Biases, TensorBoard, JSONL) without interference, allowing users to maintain their current logging setup while adding MLflow.
- **Backward compatibility.** When MLflow parameters are not provided, Training Hub behavior is completely unchanged — no new dependencies are required and no existing code breaks.

## Additional Configuration Options

Beyond the required `mlflow_tracking_uri`, users may optionally specify:

- `mlflow_experiment_name` — to organize runs under a named experiment (defaults to a sensible auto-generated name if not provided).
- `mlflow_run_name` — to assign a human-readable name to a specific run.
- The feature should also support deployment scenarios where parameters cannot be passed programmatically (e.g., containerized or CI/CD-driven training pipelines).

## Success Criteria

1. Users can enable MLflow tracking by passing `mlflow_tracking_uri` to `sft()`, `osft()`, or `lora_sft()` with zero additional boilerplate code.
2. All training metrics, hyperparameters, and run metadata are automatically logged to the specified MLflow server.
3. The feature works correctly in multi-GPU and multi-node distributed training scenarios without duplicate log entries.
4. The feature is fully backward compatible — existing code without MLflow parameters continues to work unchanged.
5. MLflow integration coexists with existing logging integrations (W&B, TensorBoard, JSONL) without conflicts.
6. Complete documentation and usage guide is available in `docs/guides/logging.md`.
