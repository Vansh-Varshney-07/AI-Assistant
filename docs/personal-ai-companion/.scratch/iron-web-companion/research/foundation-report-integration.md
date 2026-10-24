# Foundation research incorporated into Iron Web

Reviewed 24 October 2026. Source: **Personal AI Hackathon Foundation Research**, 30 pages, dated 23 October 2026. Found in this chat's outputs as `personal-ai-foundation-research-2026-10-23.pdf`; retain a source copy in `D:\Opencode_\memory_system\Personal AI Hackathon Foundation Research.pdf`.

This is a requirements/design update, not newly implemented integrations or executed application tests. The report itself marks its architecture, operational targets and tests as proposals. User choices remain controlling: Windows/local first, orchestrator-only memory, narrow recurring approvals, general fitness adapters, and no desktop capture.

[Source PDF](../../../sources/Personal-AI-Hackathon-Foundation-Research.pdf) · SHA-256: `4a6cd4922e49122e0e7229b4fa3a4065aedd3d07d4f99a139bbb85ee1d44c9d3`

## Additions and page traceability

| Report pages | Added to the design |
|---|---|
| 3–6, 23–24 | Focused demonstration: selected documents → cited brief → approved decision → fresh-session recall/correction → one controlled follow-up and actual draft/output. The broader connector roadmap remains. |
| 7–9, 15–16, 22–23 | Pin Hermes/sandbox dependencies; bounded NemoClaw/OpenShell compatibility trial with a simpler, correctly restricted Hermes fallback. Demonstrate actual allowed/denied operations. |
| 10–11 | Explicit, orchestrator-only memory operations before automatic provider hooks; one declared knowledge authority; source/authority/time/consent/revision distinctions and stale-context checks. |
| 11, 17, 20–21 | Deletion receipts and tombstones across active copies; database-safe backup and isolated restore; unavailable indexes cause typed degraded states, not false success. |
| 11 | Starter reviewed skills: review a paper, produce a source-linked project brief, check a chosen commitment. Version, test, review and retain rollback. |
| 12–14, 19, 26–27 | Separate Nebius Token Factory adapter: routine Lightning, bounded Ultra escalation, account-visible model discovery, real function-call/result replay, structured output, streaming/cancellation, per-route budgets and traces. |
| 9, 14–15 | Inference-disclosure gate showing provider/model, selected context, purpose and limits. Inspect auxiliary model routes too. Local memory does not imply local inference. |
| 16–17 | One scheduler owner per routine; durable occurrence IDs, leases, timezone, next/last run, missed-run policy, pause/cancel and meaningful-change notifications. Reboot and sleep limits must be visible. |
| 18–19 | Keep memory off disposable compute disks; optional finite cloud evaluation/indexing jobs; explicit token/tool/time/cost/concurrency limits. |
| 20–22 | Proposed 30-case synthetic evaluation: ten memory/correction, ten tool-use and ten research-synthesis cases. Compare both models on equal evidence/permissions; publish failures, p50/p95 latency and cost per successful task. |
| 4–5, 23–25, 28–30 | Submission checklist: clean licensed source, third-party notices, pre-existing-work disclosure, synthetic demo tenant, short public video, qualifying runtime trace and judge-access/recovery runbook. |

## Conflicts handled explicitly

- **Memory authority:** the PDF proposes a journal with graph/vector projections. Existing Iron Web uses its dual-store memory engine plus a separate receipt/work journal. Do not relabel SQLite as the factual authority or replace the stores without a versioned migration decision and tests.
- **Host choice:** preserve the Windows/local product. WSL2/Linux sandbox or synthetic judging host is conditional on a trial and approval; no silent move of personal data to cloud storage.
- **Provider hooks:** test explicit primary-only memory operations first; automatic prefetch/transcript mirroring stays optional and must respect retention consent.
- **Provider identity:** past NVIDIA-endpoint tests do not prove Nebius runtime use. Nebius credentials, exact provider model IDs and actual routing must be verified separately.
- **First slice:** propose research-and-follow-through for the hackathon while retaining Gmail, WhatsApp Business, notes/calendar, fitness and GitHub as later product increments. No open human design ticket is silently closed.

## Independent refresh of critical facts

Official rules require an NVIDIA open model and a runtime Token Factory call or a listed AI Cloud execution path. The displayed deadline is 30 October 2026 at 10:00 PDT, equivalent to 22:30 India time. Recheck the official rules for submission and personal eligibility. [Official rules](https://nebiusglobalaihackathon.devpost.com/rules)

Token Factory documents `https://api.tokenfactory.nebius.com/v1/` and `NEBIUS_API_KEY`. No account discovery, credential use or paid request was performed in this update. [Quickstart](https://docs.tokenfactory.nebius.com/quickstart)

NVIDIA describes NemoClaw as early-preview alpha with platform-specific support/caveats. Effective isolation and compatibility remain trial gates. [Platform support](https://docs.nvidia.com/nemoclaw/user-guide/hermes/reference/platform-support)

The report's exact model IDs/prices are provider candidates and dated estimates, not proof of present account access or measured spending. Existing installed stack, credits, host recovery and personal competition eligibility have not been newly validated.
