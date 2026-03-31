---
rfe_id: RFE-001
score: 9
pass: true
recommendation: submit
feasibility: feasible
revised: false
needs_attention: false
scores:
  what: 2
  why: 2
  open_to_how: 2
  not_a_task: 2
  right_sized: 1
before_score: 9
before_scores:
  what: 2
  why: 2
  open_to_how: 2
  not_a_task: 2
  right_sized: 1
---
## Assessor Feedback

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT | 2/2 | Clearly describes the capability gap: Gen AI Studio only supports simple system prompts via MLflow, but customers need parameterized text templates with `{{variable}}` placeholders and multi-role chat templates. The problem is precisely scoped, current limitation explained, and desired outcome articulated in concrete terms. |
| WHY | 2/2 | Strong named-customer evidence. Credit Mutual has explicitly conditioned their RHOAI migration on this capability — a direct retention/adoption risk tied to a specific account. Competitive pressure from wx.ai PromptLab cited as documented reason customers choose competing platforms. Multiple existing prompt lab customers blocked on migration. |
| Open to HOW | 2/2 | Describes what users need to do (browse, load, edit, create, save, run inference) without prescribing internal architecture. MLflow and Gen AI Studio are named as the established platform technologies the customer need is tied to — this is WHAT, not HOW. Acceptance criteria describe user-facing behaviors using common UI vocabulary. |
| Not a task | 2/2 | Clearly a business need, not a development task. Frames the problem from the AI Engineer persona's perspective, articulates why the gap matters to the business, and describes what users cannot do today. |
| Right-sized | 1/2 | The RFE covers a coherent capability area but spans both "read" workflows (browse, load, inference) and "write" workflows (create, save) across two template types. The 9 acceptance criteria are broad enough that this could map to 1-2 strategy features. However, the business case ("end-to-end parity with wx.ai PromptLab") supports treating this as a single need. This is an acceptable score — the RFE may map to multiple strategy features at the RHAISTRAT level without needing to be split as an RFE. |

**Verdict: PASS (9/10) — Recommendation: Submit**

**Strengths:**
- Excellent named-customer evidence with Credit Mutual's conditional commitment
- Precise problem statement identifying the gap between current system-prompt-only support and richer template types
- Clean separation of WHAT from HOW — acceptance criteria describe user-facing behaviors
- Well-defined user persona with clear connection to disrupted workflow

**Minor note (Right-sized, 1/2):**
- The scope spans read and write workflows across two template types. If desired, this could be split into consuming existing templates vs. authoring new templates. However, the unified "end-to-end parity" framing is defensible and does not require splitting.

## Technical Feasibility

**Verdict: Feasible**

All backend APIs and infrastructure required to deliver this capability already exist in RHOAI 3.4:

- **MLflow already supports prompt management.** The MLflow component (v3.10.1+rhaiv.1) explicitly lists "prompt management" as a core capability. The upstream APIs for text and chat prompt templates are available.
- **Module Federation integration already exists.** The MLflow component exports a `MlflowPromptsWrapper` federated module. RHOAI 3.4-ea.2 changes explicitly include "Add module federation support for prompt management."
- **Proxy routes established.** The odh-dashboard backend proxies MLflow API requests, and the data-science-gateway provides additional routing.
- **No new components or services required.** This extends existing UI components consuming existing APIs — lowest-risk type of architecture change.

**Dependencies:** gen-ai-ui (major — bulk of new UI code), mlflow-ui federated module (moderate), odh-dashboard and MLflow server (minimal).

**Risks:** Low to medium — UI complexity for multi-role chat template editor is the main work; no architectural blockers. MLflow EA status means this is the right time to enrich capabilities before GA.

**Architecture alignment:** Strong — follows established Module Federation pattern, extends existing MLflow prompt management investment.

## Strategy Considerations

- At RHAISTRAT level, this may decompose into 1-2 features (e.g., template consumption vs. template authoring), but this is a strategy-level decision, not an RFE-level concern.
- MLflow's EA status in RHOAI 3.4 makes this a natural candidate for the next release cycle.
- RBAC granularity for prompts vs. models may be a follow-up need if customers require separate permissions.

## Revision History

None — RFE passed on first assessment with no auto-revision needed.
