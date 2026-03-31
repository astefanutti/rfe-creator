---
rfe_id: RFE-001
title: Model Signature Verification at Serving Time
priority: Normal
size: M
status: Ready
parent_key: null
---
## Summary

Users who sign AI models during storage using Red Hat Trusted Artifact Signer and AI Hub have no assurance that the models actually being served match what was signed. Signature verification must be enforced at model serving time to complete the model supply chain trust chain — closing the gap between "sign on store" (delivered via RHAISTRAT-513) and "verify on serve." This RFE addresses the need for signature verification when models are deployed for inference through KServe and llm-d, covering both S3/HuggingFace-stored models with OpenSSF Model Signature (model.sig) files and OCI ModelCar images with Cosign signatures.

## Problem Statement

Today, RHOAI provides the ability to sign AI models at storage time through integration with Red Hat Trusted Artifact Signer. However, signatures are completely ignored at serving time. This means:

- Users who carefully sign their models have zero runtime assurance that the model being served is the same model they signed. The signing workflow is incomplete without verification.
- Platform administrators have no mechanism to enforce signature verification policies for deployed inference workloads. There is no guidance on how to configure Red Hat Trusted Artifact Signer with OpenShift AI to verify model signatures before serving.
- The existing "sign on store" investment (RHAISTRAT-513) does not deliver its intended runtime integrity value without a corresponding "verify on serve" capability.
- For models stored as OCI ModelCar images, both the container image signature (Cosign) and any embedded OpenSSF Model Signatures should be verifiable, but neither is checked today.

## Affected Customers

- **Financial services institutions (FSI segment)**: Require verifiable model provenance for regulatory compliance and governance. Model integrity verification is a prerequisite for audit trails in regulated AI deployments.
- **Government agencies**: Require end-to-end verifiable supply chain integrity for AI models deployed in sensitive environments, aligning with software supply chain security mandates.
- **Regulated industry customers**: Organizations in healthcare, energy, and other regulated sectors that need to demonstrate model provenance and integrity as part of their compliance and risk management frameworks.

## Business Justification

- **Strategic investment completion**: The "sign on store" capability was delivered via RHAISTRAT-513. Without "verify on serve," that investment does not deliver its intended runtime integrity value. This RFE completes the end-to-end model supply chain security story.
- **Customer demand**: Customers in regulated industries are actively requesting end-to-end verifiable model provenance. The ability to verify model signatures at serving time is a key requirement for production AI deployments in these segments.
- **Competitive differentiation**: Model supply chain security is an emerging differentiator in the enterprise AI platform market. Providing a complete sign-and-verify workflow positions RHOAI ahead of competitors that lack runtime integrity verification.
- **Ecosystem alignment**: Upstream Sigstore ecosystem projects — including the ImagePolicy controller and Model Validation operator — provide building blocks that can accelerate delivery.

## Acceptance Criteria

- [ ] Administrators can configure signature verification policies that apply when models are deployed for inference
- [ ] Models sourced from S3 or HuggingFace with an associated model.sig file (OpenSSF Model Signature) are verified before serving begins
- [ ] OCI ModelCar images are verified (container image signature via Cosign and/or embedded OpenSSF Model Signature) before serving begins
- [ ] Clear pass/fail feedback is provided to both administrators and users when signature verification fails, with actionable information about the failure
- [ ] Policy-driven enforcement allows administrators to choose between blocking deployment (hard-stop) or issuing warnings when verification fails

## Success Criteria

- The end-to-end story — sign on store, verify on serve — provides a complete, verifiable trust chain for AI model provenance in RHOAI.
- Administrators in regulated environments can demonstrate to auditors that only signed and verified models are served in production.
- Users receive clear, actionable feedback when a model fails signature verification, enabling them to resolve the issue without escalation.
