# W01–W47 catalogue audit — 26 October 2026

This compares the user's supplied 47-role catalogue with both available local development branches. It counts logical roles, including suitable deterministic services; it does not require 47 separate model agents or permanent processes.

**Not all 47 are complete.** There are project artifacts associated with **37 roles**, at different stages. **Ten roles need an explicit role definition or documented reuse mapping.** Five additional roles have registry descriptions only; partial integrations and profile-to-runtime integration still require work. A registry entry is not evidence of working execution.

## Sources inspected

- Active checkout: `D:\Opencode_\AI assistant`, branch `codex/platform-integration`, HEAD `4913ee9`. Existing local platform/desktop code is uncommitted and was included in this audit.
- Other checkout: `C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant`, branch `codex/ui-backend-integration`, HEAD `7b59c06`. Its 16 dedicated worker-definition directories and contract tests are committed. This work is **not merged into the active branch**.
- Atlas registry: 29 entries, including general combined workers and entries outside the W01–W47 catalogue. Therefore neither `29` nor `47 - 29` measures completed or missing catalogue workers.
- Explicit desktop routing, platform services, action gates, source adapters and test reports in the active checkout.

The two implementations both own files under `wayfinder/workers/`; integration must preserve the desktop runtime files/role exports while adding the other branch's schemas and definitions. This audit did not merge, switch branches, edit the other checkout or start any worker/desktop action.

## Counts by evidence stage

| Stage | Count | Meaning |
|---|---:|---|
| Dedicated definitions with offline contract tests | 16 | Other branch has definition YAML and task-level fixture/schema tests. Live Hermes execution and integration into this platform are not established by these tests. |
| Implemented and tested desktop roles | 4 | W33–W36 have the existing scoped implementation and test evidence. W34 is deterministic discovery; the other three use Hermes on demand. |
| Deterministic platform services, implemented or partial | 9 | Shared services cover these responsibilities; they are not nine separate agents. Generality and qualification vary below. |
| Partial execution/data integrations | 3 | Supporting code exists, but the complete role is not qualified. |
| Registry descriptions only | 5 | Named role metadata exists, without a dedicated definition/test/runtime binding verified here. |
| No explicit role definition or reuse mapping found | 10 | General Hermes/tools or related roles may be reusable; new agent implementations are not automatically necessary. |
| **Total** | **47** | **37 have some artifact; this is not 37 completed workers.** |

## Role-by-role status

`Profile` means a dedicated definition and offline contract suite on the other branch. `Service` means the existing deterministic integration covers some or all of the responsibility. `Metadata` means the registry description alone. `Missing` means no explicit role definition/reuse mapping was found in the inspected code.

| ID | Worker | Evidence and remaining work |
|---|---|---|
| W01 | Intent Analyst | **Profile.** Dedicated schema/fixtures and definition; runtime integration pending. |
| W02 | Context Retriever | **Service.** Scoped orchestrator-only ContextGateway over Iron Web, tested through the read-only workflow. |
| W03 | Task Planner | **Profile.** Plan contract/fixtures; general plan execution integration pending. |
| W04 | Capability Scout | **Service.** Atlas candidate retrieval with installed-runtime qualification for the existing W35 binding. Additional handlers require qualification. |
| W05 | Workflow Coordinator | **Service, partial.** Fixed read-only recipe, two-active-workflow limit, deadlines/cancellation/result validation. General multi-worker dependencies/parallel execution remain unqualified. |
| W06 | Result Validator | **Profile.** Other branch's output contract; current controller also validates its own bounded outputs. Shared integration pending. |
| W07 | Synthesis Worker | **Profile.** Other branch's output contract; the current read-only workflow returns validated W35 text with provenance. General multi-worker synthesis pending. |
| W08 | Web Researcher | **Profile.** Offline source/output/capability tests; no live search or Hermes worker run proved by this audit. |
| W09 | Source Verifier | **Profile.** Offline verification contract; live source-comparison execution unqualified here. |
| W10 | Document Analyst | **Profile.** Offline contract; overlaps the existing W35 implementation, which should be reused explicitly during integration. |
| W11 | Data Analyst | **Profile.** Offline data-analysis contract/helper checks; integrated execution unqualified here. |
| W12 | Knowledge Synthesizer | **Profile.** Offline contract; integrated execution pending. |
| W13 | Calendar Analyst | **Profile.** Read adapter prepared with fixture tests. Google client/consent and real-account qualification pending; scheduling analysis is not proved by reading events. |
| W14 | Task Manager | **Profile.** Read adapter prepared with fixture tests. Account qualification and controlled task writes pending. |
| W15 | Schedule Optimizer | **Profile.** Offline scheduling contract/helpers; connected end-to-end planning and approved changes pending. |
| W16 | Commitment Tracker | **Profile.** Offline extraction/proposal contract; authorized live message ingestion pending. |
| W17 | Reminder Manager | **Missing.** Hermes cron capability exists, but no explicit reminder-role definition/binding was verified. Reuse the existing scheduler. |
| W18 | Meeting Preparation Worker | **Profile.** Offline briefing contract; connected calendar/document/context workflow pending. |
| W19 | Repository Analyst | **Profile.** Offline analysis contract; hosted GitHub execution qualification pending. |
| W20 | Code Researcher | **Missing.** Can potentially reuse W08/W09 with an explicit coding-research task binding. |
| W21 | Implementation Planner | **Missing.** Can potentially specialize/reuse W03; no explicit binding/test found. |
| W22 | Code Worker | **Missing.** A bounded workspace execution binding remains necessary. |
| W23 | Test Analyst | **Missing.** Project test runners exist, but no explicit restricted test-worker definition/binding was verified. |
| W24 | Code Reviewer | **Profile.** Offline review contract; integrated bounded review execution pending. |
| W25 | Git Workflow Worker | **Partial integration.** Real controlled local branch creation is qualified. Full worker definition, commits/PRs and hosted GitHub actions are not qualified. |
| W26 | Activity Analyst | **Partial integration.** Scoped canonical CSV records/summaries are tested. Named fitness-provider access and reasoning-role binding are not qualified; fitness is deferred by the user. |
| W27 | Progress Analyst | **Missing.** Explicit role/reuse mapping and historical trend tests not found; fitness deferred. |
| W28 | Routine Planner | **Missing.** Explicit role/reuse mapping not found; fitness deferred. |
| W29 | Message Analyst | **Metadata.** Registry role exists; dedicated profile/contract and integrated authorized-message analysis were not found. |
| W30 | Response Drafter | **Metadata.** Registry role exists; dedicated profile/contract and integrated draft execution were not found. |
| W31 | Communication Reviewer | **Metadata.** Registry role exists; dedicated profile/contract and integrated draft review were not found. |
| W32 | Message Action Worker | **Metadata.** Registry role exists. Current Gmail adapter has no send operation; a qualified approval-controlled send integration is still required. |
| W33 | Desktop Context Analyst | **Implemented/tested.** Explicitly shared images only. No desktop monitoring; native UI testing remains disabled. |
| W34 | File Discovery Worker | **Implemented/tested.** Deterministic scoped FileBroker discovery, not a separate reasoning agent. |
| W35 | Local File Analyst | **Implemented/tested.** Existing isolated Hermes file analysis, including synthetic live-provider evidence. |
| W36 | Desktop Action Planner | **Implemented/tested.** Reviewable schema-validated plans; no execution authority. |
| W37 | Desktop Action Worker | **Partial integration.** Approval gate and fixture adapter exist; successful native completion remains unverified. Default driver is disconnected and native testing stays disabled. |
| W38 | Memory Query Worker | **Service.** Reuses the same scoped ContextGateway/Iron Web APIs as W02. These are two logical responsibilities, not duplicated memory engines. |
| W39 | Preference Interpreter | **Missing.** Existing memory stores preferences, but explicit conversion-to-planning-constraints worker/reuse mapping not found. |
| W40 | Memory Update Proposer | **Missing.** Existing services validate and apply proposals, but do not constitute a worker that identifies facts worth saving. |
| W41 | Memory Conflict Analyst | **Service, partial.** Existing Iron Web recall exposes conflicts, uncertainty and freshness; dedicated advisory analysis integration remains partial. |
| W42 | Memory Maintenance Worker | **Service, partial.** Scoped previews and approved correction/retraction events exist. General deduplication, expiry and cleanup recommendation workflows are not exposed/qualified for this role. |
| W43 | Error Investigator | **Metadata.** Registry description exists; dedicated definition/contract and runtime investigation binding were not found. |
| W44 | Workflow Recovery Worker | **Service, partial.** Explicit one-retry read path, interruption handling and read-only Git/memory reconciliation. Broader workflow/provider recovery remains incomplete. |
| W45 | Security Reviewer | **Missing.** Permission enforcement exists, but it is different from a worker providing advisory security findings. |
| W46 | Action Auditor | **Service.** Scoped persistent approval/execution/outcome audits for the implemented Git/memory/desktop paths. Additional connector types require their own qualification. |
| W47 | Workflow Evaluator | **Service, partial.** Historical artifact checks and latency/failure/dispatch metrics. Semantic quality, full tool-selection evaluation and provider token/cost evidence remain incomplete. |

## Verification for this audit

Ran the other checkout's dedicated worker contract tests read-only using Python `-B` and pytest with its cache disabled. **98 tests passed** in 1.12 seconds across the **16 definition suites**. Report written only in the active workspace: `.local/verification/catalogue-peer-contracts.xml`.

These are offline contract/fixture tests. They do not invoke Hermes, browse sources, read accounts, send messages, run code changes or exercise desktop input. Existing platform and desktop test reports are separate and must not be counted as tests of all 47 roles.

## Remaining definition/reuse work

The ten IDs are **W17, W20, W21, W22, W23, W27, W28, W39, W40, W45**. The five registry-only IDs are **W29, W30, W31, W32, W43**. Completing those definitions will still leave integration/qualification work, especially provider consent, hosted GitHub, controlled writes, multi-worker coordination and W37.

The next integration should bring the other branch's worker-owned schemas/definitions into the platform through explicit adapters, preserving the existing desktop handlers and permission boundaries. No new framework, scheduler or memory system is needed, and several missing logical roles can reuse existing workers or services.
