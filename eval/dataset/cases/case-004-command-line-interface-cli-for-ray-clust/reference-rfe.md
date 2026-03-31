---
rfe_id: RFE-001
title: Command Line Interface (CLI) for Ray Cluster and Job Management
priority: Normal
status: Ready
size: M
parent_key: null
---
## Problem Statement

Users of the Ray cluster SDK must currently write and execute Python scripts or use Jupyter notebooks for even the simplest operational tasks — listing clusters, checking status, scaling resources, or managing jobs. This creates significant barriers for three key user groups:

1. **Platform engineers and SREs** who manage ML infrastructure but are not Python-focused cannot effectively use the SDK. They are accustomed to CLI tools like `kubectl`, `aws`, `gcloud`, and `az` and expect similar tooling for Ray cluster management.

2. **DevOps engineers building CI/CD pipelines** for ML workloads cannot integrate Ray cluster management into standard automation workflows. Shell scripts, CI/CD pipelines, and GitOps processes all rely on CLI tools, not Python script execution.

3. **Data scientists and ML engineers** performing quick operational checks (e.g., "is my cluster running?", "what's the job status?") are forced to open a Python environment, import the SDK, authenticate, and write multi-line scripts for operations that should take a single command.

The Python-only approach means that a simple status check that should take seconds instead requires writing, saving, and executing a script — roughly a 5x overhead in time and effort.

## Business Justification

### Competitive Parity

Every major competitor in the ML platform space provides CLI tooling for infrastructure management:

- AWS provides `aws sagemaker` CLI commands
- Google Cloud provides `gcloud ai` CLI commands
- Azure provides `az ml` CLI commands
- Kubernetes ecosystem tools universally provide CLI interfaces

CLI tooling is table stakes for enterprise adoption. Organizations evaluating ML platforms will choose solutions that integrate with their existing DevOps practices and toolchain.

### Market Expansion

The current Python-only SDK limits the addressable user base to Python developers. Adding CLI support is expected to enable a **10x increase in non-data-scientist users** (SREs, platform engineers, DevOps engineers) who can adopt and manage Ray clusters through the SDK.

### Operational Efficiency

CI/CD pipeline integration currently requires wrapping Python scripts in shell commands, managing Python environments in CI runners, and handling SDK dependencies — an estimated **90% reduction in pipeline complexity** is achievable by providing native CLI commands that can be called directly from shell scripts and pipeline definitions.

### Affected Customers

- **Fidelity Investments** — Enterprise platform engineering teams managing ML infrastructure at scale
- **Bloomberg** — SRE teams requiring CLI-based operational tooling for Ray cluster management
- **Capital One** — DevOps engineers building CI/CD pipelines for ML workloads

## Expected Capabilities

Users should be able to perform the following operations from the command line without writing Python code:

### Cluster Management
- List all clusters with filtering and status information
- Get detailed information about a specific cluster
- Create new clusters (with support for presets/templates to simplify common configurations)
- Delete clusters
- Scale cluster resources (workers up/down)
- Check cluster status and health
- Access cluster dashboard URLs
- View cluster metrics

### Job Management
- Submit jobs to clusters
- Create job definitions
- List jobs with filtering
- Get detailed job information
- View job logs (including streaming/follow capability)
- Stop running jobs
- Wait for job completion (with timeout support)
- Delete job records

### General Capabilities
- Query available cluster capabilities and resource types
- Manage CLI configuration (authentication, defaults, output preferences)
- Multiple output formats (human-readable table, JSON, YAML) for both interactive use and scripting/automation
- Shell completion for bash, zsh, and fish
- Consistent error messages and exit codes suitable for scripting

## Success Criteria

1. Users can perform all major cluster and job management operations from the command line without writing Python code
2. Output is available in table, JSON, and YAML formats for easy scripting and automation
3. Shell completion works for bash, zsh, and fish shells
4. Quick status checks (e.g., cluster status, job status) are at least 5x faster than the current Python script approach
5. CI/CD pipelines can integrate cluster management using standard shell commands without requiring Python environment setup
6. Command structure follows CLI conventions familiar to users of kubectl, aws cli, and gcloud (command group + verb pattern)

## Out of Scope

- GUI or web-based management interfaces
- IDE plugins or extensions
- Programmatic SDK API changes — the CLI should consume the existing SDK, not replace it
- Infrastructure provisioning (e.g., creating the underlying Kubernetes cluster)
- Authentication provider implementation — the CLI should integrate with existing authentication mechanisms
