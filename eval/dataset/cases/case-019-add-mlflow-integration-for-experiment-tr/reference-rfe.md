---
rfe_id: RFE-001
title: Add Centralized Experiment Tracking to AI Training Pipeline
priority: Normal
status: Ready
size: M
parent_key: null
---
## Customer Problem

Internal ML engineering teams and enterprise customers using the AI training platform (including FinServe AI division, MedTech Labs data science group, and AutoDrive ML team) lack centralized experiment tracking across their training runs. The platform supports multiple training strategies (LoRA, SFT, OSFT) and integrates with Eval Hub for evaluation, but there is no unified system to capture, compare, or audit experiment data.

Users cannot:

- **Compare experiment runs** across training strategies to determine which approach yields the best results for a given dataset or task.
- **Track hyperparameter impact** on model performance — changes to learning rates, batch sizes, LoRA rank, or other strategy-specific parameters are not systematically recorded alongside outcomes.
- **Inspect metrics and artifacts** in a centralized location — training loss curves, evaluation scores from Eval Hub, model checkpoints, and logs are scattered across different systems and must be manually correlated.
- **Reproduce prior results** — without a record of exact parameters, dataset versions, and environment configurations, teams cannot reliably recreate a previous training run.

Teams currently resort to ad-hoc spreadsheets and custom scripts to track experiments, leading to lost context, unreproducible results, and significant manual overhead during model development and optimization cycles. Engineers report spending substantial time on manual tracking rather than on model improvement work.

## Business Justification

- **Revenue risk**: At least 4 enterprise accounts have flagged experiment observability as a gap during renewal discussions, representing approximately $3.5M in annual recurring revenue at risk.
- **Auditability and governance**: Enterprise customers in regulated industries (financial services, healthcare) require traceable experiment lineage to meet compliance and governance requirements. Without it, the platform cannot serve these customers' audit needs.
- **Competitive parity**: Competing ML platforms offer built-in experiment tracking as a standard capability. The absence of this feature is a differentiator working against us in competitive evaluations.
- **Developer productivity**: Manual experiment tracking slows iteration cycles, increases context-switching overhead, and introduces errors — directly impacting time-to-value for all users of the training pipeline.

## Affected Customers

- Internal ML engineering teams building and iterating on models using the AI training pipeline
- FinServe AI division — enterprise customer requiring auditability of model training experiments for regulatory compliance
- MedTech Labs data science group — enterprise customer needing reproducible experiment tracking across training strategies
- AutoDrive ML team — enterprise customer comparing training approaches (LoRA vs. SFT vs. OSFT) at scale

## Proposed Enhancement

The AI training pipeline needs centralized experiment tracking so that every training run automatically captures parameters, metrics, artifacts, and lineage in a single, queryable system. This capability should integrate as a cross-cutting concern across the existing pipeline without changing the pipeline's modular structure or Eval Hub integration.

### Required Capabilities

1. **Automatic parameter capture** — Each training run must record the training strategy used, all strategy-specific hyperparameters, and dataset metadata (name, version, schema) without requiring manual user action.

2. **Metric logging** — Training metrics (loss, accuracy, learning rate) and Eval Hub evaluation results must be captured and associated with the run that produced them, enabling time-series analysis of training progress and final evaluation outcomes.

3. **Artifact association** — Model artifacts, training logs, and evaluation reports produced during a run must be linked to the experiment record, so users can retrieve and inspect them from a single location.

4. **Experiment lineage** — Each experiment record must be linked to the pipeline run that executed it, the dataset version used, and the resulting model version in the Model Registry. Users must be able to trace from a registered model back to the exact experiment, parameters, and data that produced it.

5. **Cross-run comparison** — Users must be able to compare multiple experiment runs side-by-side — filtering by training strategy, sorting by metrics, and viewing parameter differences — to identify which configurations produce the best results.

### Scope Boundaries

- Training modularity is preserved — LoRA, SFT, and OSFT remain independent strategy implementations.
- Eval Hub integration is unchanged — evaluation continues through the existing Eval Hub interface; experiment tracking receives forwarded results.
- Pipeline structure is unchanged — no changes to pipeline orchestration, step ordering, or execution model.

> **Implementation note**: MLflow is the leading candidate for this capability given its maturity, broad adoption in ML workflows, and native support for parameter/metric/artifact logging with a comparison UI. Final technology selection is deferred to the strategy/design phase.

## Success Criteria

1. **End-to-end experiment capture**: A complete pipeline run using any training strategy produces an experiment record containing:
   - **Parameters**: Training strategy, all hyperparameters, dataset version
   - **Metrics**: Training loss/accuracy at each logging interval, Eval Hub evaluation results
   - **Artifacts**: Model artifacts, training logs, Eval Hub evaluation reports
   - **Lineage**: Pipeline run ID, model version (from Model Registry), dataset reference

2. **Cross-run comparison**: Users can compare multiple experiment runs side-by-side, filtering by training strategy, sorting by metrics, and viewing parameter differences — without relying on external tools or manual data collection. Time to retrieve a comparison of any two runs should be under 30 seconds.

3. **Lineage traceability**: Users can trace from a registered model back to the exact experiment, parameters, dataset, and evaluation results that produced it — in no more than 3 navigation steps from the Model Registry entry.

4. **No regression**: Existing pipeline functionality (training, evaluation, model registration) continues to work correctly with experiment tracking enabled. Experiment tracking adds no more than 5% overhead to total pipeline execution time and does not introduce pipeline failures if the tracking system is temporarily unavailable.
