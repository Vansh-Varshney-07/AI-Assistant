# Agent and worker readiness for the Wayfinder rebuild plan

Audit date: 27 October 2026. Checkout: `main`, baseline commit `47f0dca`. This is a read-only source/planning audit; no model, account, native UI or new execution tests were invoked.

## What the current source actually supports

The old `WORKER-CATALOGUE-AUDIT.md` still says the 16 worker definitions are on another, unmerged branch. That statement is historical: **all 16 definition directories and their offline contract suites are now present in this checkout**. It does not follow that those workers are connected to Hermes at runtime.

`WorkerHub.start` admits W33, W35 and W36, plus a separate canonical CHAT route. `hermes_runner.py` agrees with that allowlist. W34 is the deterministic FileBroker; W37 has a separate action gate and no qualified native driver. The 16 YAML definitions and dataclass contracts are not loaded by a general production role dispatcher.

`TaskProfiles` explicitly binds only A01/A05/A06 to `existing.W35`, for one selected UTF-8 file. A07 links the existing Memory view. Other profiles have no qualified execution adapter, and all six app presets return unavailable. The profile catalogue cannot activate a provider merely by listing its name.

`CapabilityCatalog` qualifies only `wayfinder.files.analyze` through the existing W35 binding. Search candidates always report `executable=False`; discovering metadata does not authorize an operation.

The chat service is operational as bounded conversation bookkeeping over isolated Hermes jobs. It has canonical history, request IDs, lookup/cancel/delete and restart interruption handling. It does **not** currently dispatch tools, read accounts or automatically publish Iron Web memory. The manifest's “no qualified general chat service” wording is stale; agentic tool use remains a separate missing integration.

Google Workspace, Tavily and Notion have manual, scoped read handlers and 0.4.1 verification evidence. Those are real integration improvements over the older audit. They do not establish connected profile execution, full Gmail bodies, Docs/Sheets content, sends or account writes. Existing reports must be kept separate from any tests executed during the forthcoming rebuild.

## Counts: logical responsibilities, not permanent agents

| Evidence category | Count | Interpretation |
| --- | ---: | --- |
| Dedicated YAML definitions plus offline contracts | 16 | Present locally; no general production dispatcher for these roles. |
| Existing desktop/file implementations W33–W36 | 4 | W35 is exposed in the desktop app; W34 is a broker; W33/W36 client surfaces remain excluded. |
| Deterministic platform responsibilities | 9 | Implemented or partial services; not nine new model processes. |
| Partial execution/data integrations | 3 | W25, W26 and W37 need distinct qualifications. |
| Registry description only | 5 | No dedicated role contract or qualified runtime binding verified. |
| Missing explicit role definition or reuse mapping | 10 | Reuse suitable Hermes skills/workers rather than automatically build ten new agents. |
| **Total W responsibilities** | **47** | **37 have some artifact; this is not 37 fully connected workers.** |

Separate counts: **1 main assistant definition + 8 task-profile definitions + 6 app presets**. Only **3 profile variants** share the qualified selected-file route. There are 29 Atlas registry entries, many aggregated or differently named; `47 - 29` is not a missing-worker count.

## Dependency gates for an atomic implementation plan

These gate IDs identify dependencies; the main phase plan can assign its own phase numbers.

| Gate | Smallest deliverable | Meaningful pass criteria |
| --- | --- | --- |
| R1: contracts and capability truth | Versioned role IDs, explicit reuse mappings, task/result/context/action adapters and a feature-to-handler matrix. | Every advertised operation resolves to one qualified binding or a concrete blocked reason. Unknown fields, mismatched versions and output-only authority claims are rejected. No silent W10→W35 substitution. |
| R2: bounded Hermes dispatch | Adapt the installed Hermes execution interface to the selected worker definitions with tool/context allowlists. | One synthetic selected-source job reaches the intended definition and validates its result. Wrong role/scope/version, unexpected tools, direct memory credentials and invalid structured output are rejected. Check actual installed compatibility before adding adapters. |
| R3: bounded workflow execution | Persisted node/request identities and immutable workflow input/output references over existing services and Hermes execution. | Dependency order, independent-node concurrency, deadlines/budgets, cancel, restart, duplicate delivery and validation failure have distinct observed outcomes; no effect replay. Start with a fixed multi-step read workflow before a free-form editor. |
| R4: approved-source-to-context reads | Project bounded Google/Notion/Tavily/file observations into the orchestrator-only context route. | Resource/account/space/task identity, source provenance and truncation survive; content reaches a model only after applicable disclosure; revocation/rotation or late responses withhold results. Injection text cannot mint grants or choose arbitrary tools. |
| R5: controlled provider effects | Qualify one exact write at a time behind the existing action/approval/receipt pattern. | Reject changed payloads, stale preconditions, expiry, revocation and cross-task access. Independently verify outcomes; reconcile lost acknowledgement before retry. Separate user-approved live fixtures from mocks. |
| R6: repository execution | Read-only repository analysis, then scoped edits/tests and individual Git/GitHub operations through the managed environment. | Path escape, redirected Git metadata, hook execution and arbitrary commands are denied. Review exact diff/command where required. Disposable repo tests prove actual operation, cancellation and result identity before a user repo is exposed. |
| R7: memory task integration | Context/personalization/proposal/conflict/maintenance interfaces over existing Iron Web APIs. | Read/write provenance and owner/space/task scopes survive; workers cannot access stores or credentials. Dry-run has no effect. Corrections require exact approval; clearing an artifact is not global erasure. |
| R8: reminders/scheduling | Explicit W17 reuse of installed Hermes scheduling, with trusted occurrence routing and scoped standing permission where applicable. | Inspect installed scheduler support; cancellation/timezone/expiry/restart and duplicate-occurrence delivery are tested. No replacement scheduler and no blank “always allow.” |
| R9: desktop boundary | Keep W33/W36 explicit-input/planning roles distinct from W37 execution. | W33/W36 cannot capture/act implicitly. W37 stays unavailable until the user re-enables native testing and a real driver completes a scoped test with independent verification. Mock success cannot unlock it. |
| R10: deferred fitness | Leave provider-dependent fitness roles blocked pending a selected, authorized source. | Existing local CSV tests remain labelled local CSV. No invented account data, health inference or fitness-provider badge. A later source must pass identity/provenance and overlap/missing-period tests. |

## Every W role, exactly once

Owner labels: **Worker** = task configuration/contract/reuse mapping; **Platform** = execution, routing, connectors, policy and audit; **Both** = a worker configuration consumed through a platform adapter. Ownership is a development boundary, not permission to access resources.

| ID | Logical responsibility | Current evidence | Main gap / next bounded step | Owner; gates |
| --- | --- | --- | --- | --- |
| W01 | Intent Analyst | Dedicated definition and offline contracts. | Bind intent output to M00 routing; classify conversation/read/proposal without granting authority. | Both; R1–R2 |
| W02 | Context Retriever | Scoped ContextGateway over existing Iron Web. | Extend verified evidence projections to selected tasks; preserve source freshness and provenance. | Platform; R4/R7 |
| W03 | Task Planner | Dedicated plan definition/contracts. | Adapt TaskPlan into executable validated dependencies; never execute model-specified arbitrary capabilities. | Both; R1–R3 |
| W04 | Capability Scout | Atlas candidate retrieval; only W35 binding qualified by catalog. | Intersect actual installed tools, qualified adapters and resource grants for each added binding. | Platform; R1–R4 |
| W05 | Workflow Coordinator | Fixed read-only recipe with deadlines/cancellation/persistence. | General dependency routing and bounded concurrency remain missing; extend integration over Hermes. | Platform; R3 |
| W06 | Result Validator | Dedicated offline contract; current controller has its own bounded validation. | Bind structured validation before synthesis/effects; expose failure without auto-looping. | Both; R1–R3 |
| W07 | Synthesis Worker | Dedicated offline contract; current read workflow returns W35 result/provenance. | Integrate multi-source synthesis with source references and explicit uncertainty. | Both; R2–R4 |
| W08 | Web Researcher | Dedicated definition; manual Tavily search handler exists. | Connect bounded search/extract evidence through trusted context. Manual search is not a live W08 run. | Both; R2/R4 |
| W09 | Source Verifier | Dedicated offline contract. | Bind supported/contradicted/unverified claims to authorized source evidence. | Both; R2/R4 |
| W10 | Document Analyst | Dedicated offline contract; existing W35 overlap. | Define a versioned explicit reuse/adapter mapping; do not silently alias identities. | Both; R1–R2 |
| W11 | Data Analyst | Dedicated offline contracts/helper checks. | Bind selected bounded data and deterministic calculations; show missing/invalid input. | Both; R2/R4 |
| W12 | Knowledge Synthesizer | Dedicated offline contract. | Integrate source-grounded knowledge output through current evidence route. | Both; R2–R4 |
| W13 | Calendar Analyst | Dedicated definition; scoped manual Google event reads. | Bind selected event observations to analysis; account check does not qualify schedule changes. | Both; R2/R4 |
| W14 | Task Manager | Dedicated definition; scoped manual Google task reads. | Integrate task observation first; controlled task writes remain separate. | Both; R2/R4 then R5 |
| W15 | Schedule Optimizer | Dedicated offline contract/helper rules. | Plan from calendar/tasks/preferences; review changes separately from recommendations. | Both; R2–R4/R7 then R5 |
| W16 | Commitment Tracker | Dedicated offline contract. | Connect authorized selected message evidence; Gmail headers/snippets are not full-body ingestion. | Both; R2/R4 |
| W17 | Reminder Manager | No explicit role/reuse mapping. | Document Hermes scheduling reuse and qualify trusted occurrences; keep disabled until then. | Both; R1/R8 |
| W18 | Meeting Preparation Worker | Dedicated offline briefing contract. | Bounded read-only meeting brief from selected calendar/email/document/context inputs. | Both; R2–R4/R7 |
| W19 | Repository Analyst | Dedicated offline contract. | Qualify scoped local/hosted repository reads; distinguish repository access from all files. | Both; R2/R6 |
| W20 | Code Researcher | No explicit role/reuse mapping. | Specialize/reuse W08/W09 with coding sources and an explicit contract. | Worker; R1/R2/R4 |
| W21 | Implementation Planner | No explicit role/reuse mapping. | Reuse W03 with scoped repository evidence and a reviewable implementation plan. | Worker; R1/R2/R6 |
| W22 | Code Worker | No explicit role/reuse mapping. | Add bounded editing adapter in managed workspace; no general host terminal grant. | Both; R1/R2/R6 |
| W23 | Test Analyst | No explicit role/reuse mapping; project test scripts exist. | Bind allowlisted relevant tests and parse actual exit/output; never infer success from text. | Both; R1/R2/R6 |
| W24 | Code Reviewer | Dedicated offline review contract. | Bind exact diff/revision and findings; reviewer remains advisory. | Both; R2/R6 |
| W25 | Git Workflow Worker | Qualified exact local `codex/` branch action. | Preserve current action; qualify commits/pushes/PRs individually rather than broad Git authority. | Platform; R5/R6 |
| W26 | Activity Analyst | Scoped canonical activity CSV service. | Bind local CSV reasoning separately; provider source remains deferred. | Platform; R2/R10 |
| W27 | Progress Analyst | No explicit role/reuse mapping. | Define trend/unknown-period contract using permitted historical data; fitness remains deferred. | Worker; R1/R2/R10 |
| W28 | Routine Planner | No explicit role/reuse mapping. | Define constraint-based routine proposal using allowed preferences/data; no health or calendar write authority. | Worker; R1/R2/R7/R10 |
| W29 | Message Analyst | Atlas role description only. | Define contract and selected-message input; bind only authorized reader output. | Both; R1/R2/R4 |
| W30 | Response Drafter | Atlas role description only. | Prepare an app-local draft first; drafting must not imply send or provider draft creation. | Both; R1/R2/R4 |
| W31 | Communication Reviewer | Atlas role description only. | Review immutable selected draft/recipient context; separate advisory judgment from approval. | Both; R1/R2/R4 |
| W32 | Message Action Worker | Atlas role description only; no enabled send handler. | Add one exact authorized message-send operation only after independent qualification. | Both; R1/R5 |
| W33 | Desktop Context Analyst | Explicit shared-image implementation/tests; current client surface excluded. | Keep file-selected image input distinct from screen capture; re-enable surface only with qualification. | Both; R2/R9 |
| W34 | File Discovery Worker | Deterministic scoped FileBroker; current app selection/search. | Reuse; qualify additional consumer bindings without handing out arbitrary filesystem paths. | Platform adapter; R1/R4 |
| W35 | Local File Analyst | Isolated Hermes implementation and selected-source evidence; current app exposure. | Reuse as first end-to-end binding; broaden formats/consumers only with actual extraction tests. | Platform adapter; R2/R4 |
| W36 | Desktop Action Planner | Schema-validated proposal/outline implementation; current client surface excluded. | Preserve advisory-only behavior and exact target requirements; no invented window identity or effects. | Both; R2/R9 |
| W37 | Desktop Action Worker | Approval boundary/fixture driver; no proven native completion. | Remain disconnected. Native reauthorization, real host driver and verified scoped completion required. | Platform; R9 |
| W38 | Memory Query Worker | ContextGateway/Iron Web integration, shared with W02. | Reuse the existing gateway; no duplicate memory engine or worker store credentials. | Platform; R4/R7 |
| W39 | Preference Interpreter | No explicit role/reuse mapping. | Translate scoped attributed preferences into planning constraints, with uncertainty and conflict handling. | Both; R1/R2/R7 |
| W40 | Memory Update Proposer | No explicit worker/reuse mapping; proposal service exists. | Identify proposed facts as advisory output; apply only through current reviewed event service. | Both; R1/R2/R7 |
| W41 | Memory Conflict Analyst | Existing conflicts/freshness exposed through memory services. | Integrate advisory conflict interpretation; never overwrite merely because an LLM prefers one claim. | Platform; R2/R7 |
| W42 | Memory Maintenance Worker | Scoped dry-run/correction/retraction infrastructure. | Qualify scoped recommendations and supported maintenance events; global forget/dedup not implied. | Platform; R7 |
| W43 | Error Investigator | Atlas description only. | Define diagnostic/evidence contract and bounded log adapter; keep secrets out and avoid automatic effect replay. | Both; R1/R2/R3 |
| W44 | Workflow Recovery Worker | Explicit read retry, interrupted state and read-only reconciliation paths. | Extend eligible recovery over the general workflow; effect uncertainty must reconcile before any retry. | Platform; R3/R5 |
| W45 | Security Reviewer | No explicit advisory role/reuse mapping; enforcement already exists. | Supply structured advisory findings using scoped evidence; cannot mint grants or override policy. | Both; R1/R2 |
| W46 | Action Auditor | Scoped persistent action/audit services for implemented operations. | Keep exact request/approval/receipt/outcome references as connectors expand. | Platform; R3/R5 |
| W47 | Workflow Evaluator | Artifact checks and latency/failure/dispatch metrics. | Add task-specific quality rubrics; keep literal checks distinct from semantic accuracy and unknown cost/tokens null. | Platform; R3 |

## Main assistant, eight task agents and six app presets

The table names all planned profiles and modes. They compose the W responsibilities above; they must not create duplicate frameworks or separate permanent processes.

| ID | Name | Current state | Next activation gate and acceptance example |
| --- | --- | --- | --- |
| M00 | Main Wayfinder Assistant | Defined routing owner; independent tool-free CHAT route works. No qualified general intent→tool orchestration. | R1–R4: one user request chooses the correct qualified lead, discloses selected context, records the run and returns cited output; simple chat need not fan out. |
| A01 | Research & Verification | One selected UTF-8 file via W35; no live tool-using profile. | R2/R4: bounded search plus independent source verification and synthesis, with source identity and injection refusal. |
| A02 | Planning & Productivity | Definition only at profile execution layer; manual calendar/task reads exist. | R2–R4/R7: feasible read-only daily plan or meeting preparation using selected inputs; recommendations do not modify calendars. |
| A03 | Communications | Definition only; Gmail headers/snippets manual reads. | R1/R2/R4: selected authorized message evidence → local draft → review; R5 separately for send. |
| A04 | Software Development | Definition only; separate local branch action exists. | R2/R6: disposable repo investigation → plan → scoped edit → actual tests/review; GitHub effects need individual R5 qualification. |
| A05 | Knowledge & Learning | One selected UTF-8 file via W35. | R2/R4: multi-source study/report from authorized evidence with resolvable citations, retaining current selected-file fallback as an explicit variant. |
| A06 | Files & Desktop | One selected UTF-8 file via W35; W34 selection/search separate. | R2/R4: scoped discovery→selection→analysis first. Image/planning surfaces R9 separately; W37 remains blocked. |
| A07 | Memory & Personalization | Links current scoped Memory UI, not a general reasoning-profile executor. | R2/R7: attributed recall/preferences plus reviewed update proposal; no automatic capture or global erasure claim. |
| A08 | Fitness & Habits | Deferred definition; no provider chosen. | R10: retain honest unavailable state. Local canonical CSV, if selected, is a separately labelled supported input. |
| P01 | Google Workspace Assistant | Defined but unavailable; no compound execution route. | R2–R4: supported read-only variants after per-service qualification. Missing Docs/Sheets content must not block a smaller valid calendar/task variant or be invented. |
| P02 | Gmail Assistant | Defined but unavailable; manual headers/snippets reader is separate. | R2/R4: choose exact message/label evidence; content-dependent requests remain blocked until a body reader is independently qualified. Sending requires R5. |
| P03 | Calendar & Tasks Assistant | Defined but unavailable; manual reads separate. | R2–R4: selected-calendar/task-list planning and explicit proposals; reminders R8, writes R5. |
| P04 | Notion Workspace Assistant | Defined but unavailable; shared-page search/bounded excerpt reads separate. | R2/R4: explicitly selected shared page → scoped synthesis. Never broaden Notion access silently or write a page from model text alone. |
| P05 | GitHub Project Assistant | Defined but unavailable; no qualified hosted connector binding. | R2/R6: selected repository reads and revision-bound analysis first; each effect R5. Codex's GitHub connection is not Wayfinder product authorization. |
| P06 | Drive, Docs & Sheets Assistant | Defined but unavailable; Drive list and Docs/Sheets metadata reads separate. | R2/R4: honest metadata/selected-file variant first; full document/cell content needs bounded identity/size/pagination qualification before a content task runs. |

## Recommended integration order

1. Reconcile capability/role truth and strict contracts (R1), including stale UI/manifest wording.
2. Connect W01/W03/W06/W07 to one bounded selected-source route through installed Hermes (R2), retaining the currently working W35 path.
3. Connect W05/W44/W46/W47 workflow persistence, cancellation/recovery/audit/evaluation (R3) before offering an arbitrary visual workflow builder.
4. Add read-only research/knowledge and scoped memory context (R4/R7); then selected Google/Notion data for A02/A03 and P01–P04/P06 variants. Do not enable all presets with a single aggregate green provider badge.
5. Add repository reads, then bounded code edits/tests/review (R6); hosted GitHub authorization/handler qualification unlocks P05 separately.
6. Add exact effects one provider/operation at a time (R5), with a real disposable live fixture only when user authorization is available.
7. Qualify Hermes reminder occurrence routing (R8) if included in the release's committed scope.
8. Keep W37/R9 native execution and A08/R10 fitness disabled until their human/environment dependencies are met. The final EXE must show a reason, not a fake success or hidden automatic fallback.

The exact final release inclusion matrix should list every W role, A profile and P preset as verified for a named variant, source/fixture-only, blocked or deferred. “Connect every agent” must mean every definition has an explicit qualified binding or visible dependency gate; it must not mean enable every tool for every role.

## Verification performed for this audit

Only filesystem/source/JSON inspection and catalogue counting were performed. The current tree contains 16 `W*/definition.yaml` files, 29 Atlas worker entries, eight profile definitions and six presets. No test suite or live worker was run for this document. Existing 0.4.1 reports, the earlier 98 offline worker-contract tests and previous backend/UI checks remain historical evidence with their original scopes; they are not a fresh pass for this proposed rebuild.
