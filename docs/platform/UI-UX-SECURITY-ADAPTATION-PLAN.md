# Wayfinder UI, UX and security adaptation plan

Research date: 27 October 2026. Baseline: Wayfinder desktop 0.4.1, commit `47f0dca`. Status: planning only.

## 1. Decision and scope

Improve how people understand and operate the features Wayfinder already provides. Study the six requested applications and the locally cloned REA repository for useful interaction and security patterns. Implement Wayfinder-specific designs through the current Electron client, Hermes integrations, Iron Web gateway and trusted services.

The first delivery should make existing features easier to find, their data boundaries easier to understand, and their outcomes easier to verify. It should not expand the assistant's authority.

The references are design evidence, not dependencies to install or applications to embed. No third-party agent runtime, storage engine, scheduler, computer-use driver, provider catalogue or automatic memory capture is proposed. No source, visual assets or branding will be copied as part of this plan.

Global overlays, a new OS-wide hotkey, screen watching, clipboard capture, voice, recurring automation and provider writes are outside this change. Fast entry will use Wayfinder's existing in-app Ctrl/Cmd+K destination palette and Chat page. W33/W36 desktop surfaces and W37 execution remain disabled in the current client.

## 2. Research findings and adaptation choices

The initial pass used documentation and static source review. A subsequent [actual REA investigation](../research/desktop-reference-rea/README.md) built the cloned REA CLI and analyzed downloaded public distributions for all six references. Those reports distinguish successful operations, timeouts with retained partial Evidence, derived scripts, native-only metadata and source-study supplements. No reference application was installed or launched; neither pass constitutes runtime qualification or a full security audit.

| Reference | Evidence reviewed | Adapt for Wayfinder | Keep outside the change |
| --- | --- | --- | --- |
| AnythingLLM | Official desktop-assistant introduction/features; source for a tool-review card in its public web client | Fast route into a conversation; understandable context selection; compact review with expandable exact parameters and expiry | Application capture, new overlay, its agent execution system, and skill-wide “always allow.” The public web approval component does not prove the desktop overlay uses the same implementation. |
| CLAI | Official product description; inline approval component; Windows fallback command runner | Workspace identity beside work; attention for pending decisions; readable operation previews; run history that stays with its workspace | Permanent teams, its scheduling/runtime, arbitrary shell modes and persistent shared-agent permissions. Its Windows fallback starts commands without the Linux/macOS OS sandbox; a permissions UI is not proof of containment. |
| Keel | Official product site; KnowledgeBrowser, citation formatter, session indicator and export-content guard | Inspectable personal context; source navigation; distinguish active work from unread results; show intended content separately from a completion claim | Markdown replacing Iron Web, automatic capture, model fallback, tasks/reminders and Google export. Its heuristic export guard is not authorization or independent verification. |
| Khoj | Official repository and privacy documentation; reference-panel source | A source pane beside an answer, with titles, excerpts and provenance; explain when retrieved context leaves the device | Its index, custom-agent framework, scheduling, cloud storage or telemetry. Use Wayfinder's escaped rendering; do not transplant HTML rendering paths. |
| Handrail | Official repository; IPC contract and main-process IPC source | A small, named renderer bridge; resource handles instead of arbitrary paths; secrets held outside the renderer; request-correlated UI state | Periodic screenshots, automatic step watching, pointing arrows, stealth behavior and its provider choices. |
| Hearth | Official repository and security policy | Understandable permission prompts; clear workspace boundaries; visible operation history; candid security limitations | Arbitrary shell/browser/app control, global auto-approval, its memory or agent loop. Its policy explicitly describes broad host permissions and limitations; it is not the security baseline for Wayfinder. |
| REA | Local commit `570abe95f`; SECURITY.md; provider deadline and diagnostic-redaction source | Session-bound private transport, bounded work, cancellation/deadline distinction, redacted diagnostics, evidence with stated limitations | Reverse-engineering tools inside Wayfinder, binary-analysis providers, instrumentation, or a new process/sandbox framework. Private authenticated transport does not defend against every process running as the same OS user. |

Primary documentation: [AnythingLLM introduction](https://docs.useanything.com/desktop-assistant/introduction), [desktop features](https://docs.useanything.com/desktop-assistant/features), [CLAI](https://clai.run/), [Keel](https://keel.keel-labs.org/), [Khoj](https://github.com/khoj-ai/khoj), [Handrail](https://github.com/M19K/handrail), [Hearth security policy](https://github.com/0pen-Sourcer/Hearth/blob/4c3a7965e4e1ec173384e42e4de31597c7b1eee7/SECURITY.md), [REA security boundary](https://github.com/morluto/rea/blob/570abe95f/SECURITY.md).

Pinned source references and review limits are recorded in [the research source index](UI-UX-SECURITY-SOURCES.json).

### REA package findings that constrain this plan

The source-derived interaction ideas below must be filtered through the actual package reports:

- Handrail's storage fallback may persist a key without OS encryption. Wayfinder retains fail-closed encryption and re-import guidance.
- Keel's packaged settings carry credential fields and its new-install cloud default differs from a blanket local-only interpretation. Wayfinder keeps a secret-free renderer and shows the actual approved model destination.
- Hearth's published permission UI includes Enter-to-approve and shortened payload previews. Wayfinder keeps Cancel as default and complete immutable payload review in a trusted surface.
- AnythingLLM's packaged assistant includes screenshot context; adapt its conversation continuity and status patterns only through existing Wayfinder Chat and navigation.
- Khoj's investigated desktop companion is historical; its hosted service has shut down. It does not prove current web-interface behavior or justify background synchronization.
- CLAI's recovered native metadata does not establish its embedded UI or Windows permission enforcement. Its workspace/review layout remains a separately labelled source-design reference.

Retained partial coverage and untested behavior are explicit in the six reports. No reference's broader permissions, memory system, provider list or native actions are imported into Wayfinder.

## 3. What exists and what needs qualification

The current client has an isolated renderer, named preload methods, sender checks, blocked navigation/popups/webviews, denied browser permissions, a main-process credential vault, trusted confirmation dialogs and scoped service handlers. These are foundations to retain, not controls to replace.

The current application can:

- Create/select spaces; chat with the approved managed model using bounded recent history, without tools or automatic memory publication.
- Select authorized files, discover/read within grants, run W35 analysis and the fixed document-plus-memory comparison.
- Run the supported selected-file variants of A01/A05/A06; display the wider task/app profile catalogue without implying every variant executes.
- Inspect Iron Web evidence and propose/review scoped fact changes.
- Inspect runs, cancel supported work, inspect audits, evaluate historical artifacts and explicitly retry eligible read workflows.
- Read connected Google sources, search Tavily, and search/open bounded shared Notion page excerpts.
- Prepare and approve a new local `codex/` branch at the observed HEAD.
- Read a canonical local activity CSV; inspect runtime capabilities and presentation settings.

Provider reads are limited: Gmail headers/snippets rather than full bodies; Docs/Sheets metadata rather than document/cell content; Calendar/Tasks reads rather than scheduling or synchronization. Manual connection reads do not qualify account-backed task agents or permit account content to enter chat.

Specific source-level issues to address first:

1. Settings still states that no Google reads are enabled, although Connections supports them.
2. The Agents introduction still describes general conversation as unqualified, although the Chat page exists.
3. The feature manifest contains historical exclusion wording that mixes quick chat with scheduling, despite general chat being present. Preserve the distinction between existing chat and an unavailable global overlay.
4. Connections loads status on entry; its green badge checks `passed` without checking `expires` as time passes. Backend enforcement exists, but presentation can remain stale.
5. Several detail views lead with raw structured data. Critical scope and outcome information needs a readable summary before optional technical evidence.
6. Permissions mostly explains policy; it should not appear to be a complete inventory of active grants when the service does not return one.
7. Existing general-task labels and profile descriptions can imply broader execution than the selected-file adapter actually supports.

These findings come from the source, not a new visual or live-account test.

## 4. Proposed interface

### Navigation and visual direction

Keep existing route IDs and handlers. Group the existing destinations more clearly:

- Everyday work: Home, Chat, Documents, Memory, Agents & apps.
- Operations: Runs & reviews, Connections, Local Git.
- Controls: Permissions, Capabilities, Settings.

Retain Wayfinder's compass identity, existing fonts, light/dark themes and reading-size setting. Reduce dashboard decoration, all-caps labels and developer terminology in primary flows. Give each screen one clear primary action. Show advanced IDs, hashes and protocol details only when useful for review or troubleshooting.

Use a stable workspace header, readable central work area and optional source/detail pane. At narrow sizes, the detail pane becomes a labelled, dismissible drawer; primary actions and scope must remain visible. Statuses use text and icons as well as color.

The command palette remains navigation-only. Opening it, changing spaces or choosing a profile must never run a task or grant permission.

### Page-by-page changes

| Existing surface | Proposed UX | Existing integration to reuse |
| --- | --- | --- |
| Home | Recent conversations and actual runs; pending reviews and uncertain outcomes first; one “Open chat” action plus document/memory shortcuts. Count only observed records, with freshness and bounded-list wording. | Current spaces, chats and snapshot methods. Do not label a bounded snapshot count as a total. |
| Chat | Readable conversation list, restrained message layout, distinct generating/stopping/interrupted/error states, visible stop action and an expandable “What is sent” explanation. | Existing chat methods and pending-request lookup. No tool calls, automatic attachments, streaming tokens or source citations unless the service actually supplies them. |
| Documents | Choose file → inspect scope/expiry → enter question → review model disclosure → run → inspect answer and supplied source evidence. Keep comparison as the existing fixed recipe. | File picker/broker, W35, comparison handlers, trusted disclosure. |
| Agents & apps | Task-oriented cards with separate catalogue identity and executable variant. Say “Research supplied files” for current A01 execution. Explain app presets that have no connected execution route. | Existing profile catalogue and selected-file adapters. A shared connector does not activate every profile. |
| Memory | Fact/source browser; current versus historical/retracted evidence; readable proposed before/after change with source context. | Iron Web gateway, source/recall/inventory and current memory proposal/review handlers. No arbitrary database editor or new capture mechanism. |
| Runs & reviews | Separate Runs and Changes tabs; factual stage timeline, result, evidence, audit and next permitted action. Unknown outcomes receive prominent attention. | Current snapshot/result/audit/cancel/retry/reconcile methods. No workflow canvas or scheduler. |
| Connections | One card per existing provider; exact available read types, imported/check status, last-check/expiry, local disconnect and provider-side revocation explanation. Results show source, observation time and truncation. | Current Windows-encrypted vault, status/check/grant/read/revoke handlers. No new OAuth provider or content-to-chat route. |
| Local Git | Select repository → inspect HEAD/destination → prepare branch proposal → exact trusted review → verified receipt or uncertainty. | Current local branch connector. No checkout, commit, push, hosted PR or merge buttons. |
| Permissions | Explain resource access, model disclosure and effect approval separately; show existing scoped selections/expiry and relevant receipts when available. Link to supported revoke/review controls. | Current selection/grant/revoke and action services. Missing grant inventory remains labelled unavailable; no fake “revoke everything” control. |
| Capabilities | Human-readable availability and reason, with inspected runtime evidence under Details. Separate discovered candidates, configured tools, qualified bindings and disabled operations. | Existing Runtime Inspector and Atlas. Discovery never grants authority. |
| Settings/onboarding | Consistent model/data-location/connection information; progressive setup; “saved locally” versus “sent to provider” explanations; precise deletion limits. | Existing setup manager, approved model policy, settings and connection status. No new provider selector, background agent mode or installer framework. |

### Shared presentation components

Propose small reusable components: StatusBadge, FreshnessLabel, ScopeSummary, SourceCard, EvidenceDrawer, RunTimeline, ActionReviewSummary and EmptyErrorState. They present existing data; they cannot approve, infer successful effects or invent progress.

For sources, show the real title/type, bounded excerpt, observed time and available provenance. Bind source navigation to an authorized service reference. A citation emitted by a model is unverified until it resolves to supplied evidence. An old artifact can remain inspectable as historical evidence without pretending its expired grant allows a fresh read.

For connection results, explain “up to three records,” “excerpt” or “metadata only” where applicable. Show absent information as unavailable rather than filling it with model-generated content.

## 5. Security and permission interaction

### Keep three distinct decisions

1. **Resource access:** allow this existing read operation against the selected resource within its grant.
2. **Model disclosure:** allow the declared file/evidence and question to go to the approved model for the supported operation.
3. **Change approval:** authorize this immutable memory or local-branch proposal once.

Connection import and a successful provider check do not authorize model disclosure or writes. Keep current chat consent and per-operation document disclosure behavior; do not add repetitive prompts to already authorized bounded reads.

### Exact review design

The in-app preview will show the operation, exact target, space/task, complete relevant parameters, expiry, preconditions and resulting effect. For memory, show old and proposed values; for Git, repository, new branch and expected HEAD. Add an optional technical digest/evidence section.

The existing main-owned trusted confirmation remains the final decision boundary, followed by service revalidation. The preview must describe the same immutable proposal fetched by that boundary. Changed/expired/revoked proposals cannot remain approvable. Render bidirectional/control characters visibly in security-sensitive values. Do not truncate away critical targets or payloads.

Use “Review exact change” in the app and retain an explicit one-time confirmation. Do not add “always allow,” silent consent reuse for changed payloads, or approvals inferred from a profile's name. Approval means authorized; completion needs a verified result.

Use purpose-specific confirmation language for model disclosure, rather than describing it as a data change. Default focus remains on Cancel. Display the scope the handler actually enforces: the current broker uses task `general`; it must not be advertised as a separate per-conversation or per-profile grant.

### Honest state and recovery

| Observed condition | Display and allowed interaction |
| --- | --- |
| Credentials imported | Saved for this Windows account; access not yet checked. |
| Current provider check passed | State the provider/probe scope, time and expiry. Do not imply every service/resource works. |
| Check expired or status unavailable | Show recheck required/unknown; remove green “working now” treatment. A UI clock is advisory; the backend remains authoritative. |
| Read completed | Show bounded results as an observation with time and scope. |
| Cancellation requested | “Stopping” until the service reports the result. Do not claim upstream billing or all external work stopped. |
| Action pending / approved | Distinguish awaiting review from execution and verified completion. |
| Outcome unknown | “Needs verification”; offer existing read-only reconciliation, never ordinary replay. |
| Restart/reconnect | Reobserve existing IDs. No resubmission, automatic retry or automatic approval. |
| Local disconnect | Remove local credentials and invalidate applicable grants; explain that provider revocation is separate. |

Refresh status on entry and after current operations, and expire display badges using their receipt time. On scope change, clear inappropriate selections/results and ignore late responses from the previous scope. Avoid polling loops that create provider traffic; reuse bounded local status reads.

### Security engineering to preserve or verify

- Keep renderer isolation, sandbox, CSP, main-frame sender validation, denied navigation/popups/webviews and named IPC. New presentation components get no generic execute, filesystem or network bridge.
- Keep credentials in the existing main-process Windows vault and owned private bootstrap. No secret values in React state, prompts, URLs, raw evidence panels or logs.
- Continue final-handler validation of scopes, grants, resource identity, payload digest, expiry, revocation and relevant preconditions.
- Treat retrieved text as data. It cannot create grants, submit approval, load remote code or choose an arbitrary external protocol. Continue escaped text rendering. Keep current safe link presentation unless a separately validated link-opening handler is required.
- Reuse current process ownership, deadlines and cancellation. Compare diagnostic handling against REA's explicit-token and truncated-prefix redaction pattern; add a narrow missing safeguard only if an actual Wayfinder gap is demonstrated.
- Private transport is not equivalent to an OS sandbox. Retain the managed OpenShell/NemoClaw boundary and explicitly state the limits of protection against same-user malware.
- Preserve unknown-outcome records, receipts and audit trails. Deleting a chat, clearing an artifact or retracting a fact does not imply erasure of backups or every associated copy.

These choices follow the official [Electron security guidance](https://www.electronjs.org/docs/latest/tutorial/security). Keyboard/dialog behavior should follow the [WAI modal-dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/), including initial focus, focus containment, Escape and focus restoration.

## 6. Implementation order and completion gates

| Phase | Work and likely files | Completion gate |
| --- | --- | --- |
| 1. Reconcile facts | Review `FEATURES.json`, renderer copy, current handlers and source evidence. Create a feature-to-route/action matrix and state/copy specification. Reconfirm installed Hermes only if an actual runtime integration change becomes necessary. | Every enabled action maps to an existing handler; no stale claim that Google reads/general chat are absent; no claim that manual reads qualify autonomous app workflows. |
| 2. Establish common UI | Existing App/Workspace/theme styles; common status, scope, source and error components. Keep existing routes and in-app palette. | Keyboard navigation, reading size, light/dark and narrow layout work in component tests. No fake activity or invented counts. |
| 3. Complete one vertical flow | Documents → current disclosure → W35/comparison → run/result/source. Then apply the same evidence and status presentation to Chat, Memory and supported profile variants. | Existing handler contract unchanged; stale/expired evidence cannot be represented as current access; cancellation and restart do not duplicate work. |
| 4. Connections and security controls | Connections, Settings, Permissions, review summaries and Runs. Expiring status display; complete exact previews; clear disconnect/revocation semantics. | Changed approvals, scope switches, revoked grants, failed checks and uncertain outcomes all produce correct permitted next steps. No change to provider permissions or automatic model access. |
| 5. Regression and packaging | Existing frontend, sender/broker/vault/API-boundary and disposable backend suites; static package checks; updated inclusion evidence and usage notes. | Existing regression tests plus the new meaningful state/security tests pass. Package includes no private data. Native visual/accessibility qualification remains a separately authorized test tier. |

Hermes, Atlas, Iron Web and the trusted authorization services stay intact. If a UI needs missing provenance/status fields, first project existing service evidence through a narrow read-only DTO; do not infer it in the renderer or build a parallel registry. Any such field change must be versioned and contract-tested.

## 7. Acceptance scenarios

1. **Document analysis:** select a synthetic file, inspect scope, cancel disclosure, then approve a new explicit attempt. Cancellation before dispatch causes no model call. A completed result has real source evidence and an observed status.
2. **Comparison:** compare selected synthetic evidence with isolated test memory using the existing recipe. Show the two sources separately. Literal artifact evaluation must not be labelled a factual-accuracy score.
3. **Memory correction:** preview a synthetic fact correction, reject it, expire another proposal and approve a fresh one. Changing payload/scope invalidates approval; only a verified receipt yields success.
4. **Local branch:** use a disposable repository. Change HEAD between proposal and execution and confirm refusal. Simulate lost acknowledgement and offer reconciliation without creating another branch.
5. **Connections:** fixture credential import/check/read, expired checks, restart, disconnect and credential rotation during a read. Never reveal tokens or late revoked results. Gmail/Docs/Sheets limits remain explicit.
6. **Scope change:** switch spaces while a read/chat/result request is pending. The late response cannot populate the new space. No automatic replay follows reconnect.
7. **Injected source content:** a document/Notion result includes script, protocol links and “approve this” instructions. It stays inert data; renderer/preload/handler checks prevent authority escalation.
8. **Keyboard and failure states:** test focus order/restoration, Escape, screen-size reflow, no color-only statuses, reduced motion, empty/error/offline states and long exact payloads.

Use synthetic data, fixture providers and disposable databases. Separate component, contract, backend, package-integrity, live-provider and native-UI results. Existing tests are regression evidence, not proof the proposed redesign already works. No live account read, external write, desktop capture, clipboard access or native window test is part of producing this plan.

## 8. Deliverables and human involvement

The implementation should deliver the feature/state matrix, page/state wireframes, small shared UI components, improved existing pages, targeted security/state tests, updated feature inclusion evidence and a package verification report. Start with the corrected availability language and expiring connection badges, then the complete document flow.

No human action is needed for this plan. Later native visual, file-picker and screen-reader walkthroughs require the user to re-enable that testing. New provider scopes or writes remain separate work and need their own authorization. This plan does not request those permissions or activate those features.
