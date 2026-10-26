# Wayfinder desktop: small releases with explicit boundaries

Revision 4 · 26 October 2026 · Windows first · proposed, not implemented

Build a real **Electron + React + TypeScript** desktop app around the existing Python/Wayfinder/Hermes services. Keep the Codex-inspired conversation workspace and progressively add useful capabilities. R1 is ordinary real chat; later releases retain and improve it. This revision replaces the [v3 desktop proposal](../wayfinder-desktop-v3/PLAN.md) after its [36-finding stress review](../wayfinder-desktop-v3/audit/REPORT.md). It changes planning artifacts only, in this new directory.

**Main scope correction:** Google reads plus a separate local task list first. No early two-way sync or external writes. Initial workflows are small linear read recipes; initial recurrence is one daily read-only brief. Unknown worker mappings and native execution are not filled in by inventing replacements.

## Read this package

- [Offline interaction preview](preview.html) — no backend, network calls, saving, model or real account.
- [Flowcharts](FLOWS.md) and [worker coverage](WORKER-SURFACES.md).
- [Contract v1](CONTRACTS.md) — authoritative details C01–C23. Worker-owned task/result schemas remain separate.
- [Manifest](manifest.json), [acceptance](ACCEPTANCE.csv), [finding-by-finding amendments](REMEDIATIONS.csv).
- [Second-order risks](SECOND-ORDER.md) and [batch/recheck record](review/REVIEW.md).

The two formerly blocking design decisions now have a concrete answer: application records own conversation history, with isolated bounded Hermes invocation (C01); one authenticated runtime owns one stable data root, with explicit attach/start/shutdown (C02). Implementations must demonstrate these requirements, not merely inherit a documented API name.

## 1. Keep the existing stack; add presentation and missing enforcement only

| Layer | Proposed choice | Reuse/qualification condition |
|---|---|---|
| Host | Qualified Hermes Desktop extension; otherwise one thin Electron shell | Installed/pinned SDK must preserve all service boundaries and exact UX. A failed gate selects the shell, never a bypass. |
| UI | React, TypeScript, Vite, Tailwind; accessible component primitives and Lucide | Prefer compatible Hermes SDK/UI primitives; use one design system and packaging path. |
| Conversation | Evaluate existing assistant-ui primitives; sanitized Markdown/code | Presentation only; canonical history and run state remain in the service. |
| Data views | TanStack Query snapshots plus local React view state | Automatic retries for observation only. No automatic command/effect replay. |
| Privileged bridge | Narrow preload intents → validated main broker → authenticated Python API | No renderer credentials, generic HTTP/shell/path bridge or weakened Origin check. |
| Application | Existing AppService/API, WorkerHub, Atlas, policy/action gate and receipts | Add versioned facades/adapters where absent; no Node duplicate backend. |
| Reasoning/execution | Existing managed Hermes/OpenShell runtime | Qualify installed tool/session/cancellation boundaries; no replacement agent loop. |
| Persistence | Existing SQLite application records and Iron Web/FalkorDB/Qdrant | One owner; supported APIs, schema/migration floor from R1. |
| Build/test | Pinned electron-vite/electron-builder or qualified upstream equivalent; pytest, Vitest/RTL, Playwright plus Windows manual checks | One chosen host. Experimental/unsupported tooling cannot replace actual packaged-app evidence. |

The [earlier research](../wayfinder-desktop-v3/RESEARCH.md) is the reference basis, not proof of installed compatibility. Pin exact versions/licenses in the implementation spike. Do not upgrade Node/Hermes/system services automatically to match moving upstream sources. If the extension cannot isolate Wayfinder sessions from broad built-in tools/routes, choose the thin shell. Tauri is not a second implementation branch. Reconsider the host only against measured unmet requirements.

Hermes-first inspection happens **before each new subsystem adapter**, not only before the UI: installed version/capability → existing code/tool/skill/MCP → suitable reuse → smallest missing integration → recorded reason. This is not authorization to reconfigure the active runtime during this planning task.

## 2. One workspace, progressively useful destinations

Wide: navigation rail → conversation/list sidebar → main workspace → optional inspector. Narrow: navigation drawer and one optional inspector sheet, with real open/close controls and keyboard recovery. One principal conversation, not mandatory split chat. Typography, scroll/focus, readable review text and error recovery are release work every time.

R1 navigation contains Chat, Runs and Settings only. Each release adds functioning destinations; examples, inspector, shortcuts and commands use the same manifest. Ordinary users see readable worker names/evidence; advanced details expose IDs/versions. Connection and qualification status come from actual evidence, not metadata badges.

## 3. Deliver these cumulative releases

| Release | Complete usable slice | User walkthrough | Hard boundary / gate |
|---|---|---|---|
| R1 · Conversation | Launchable app; real bounded model reply; new/reopen chats; stop; honest runtime/settings; persisted completed history | Launch → ask a novel question → get a real answer → stop another run → quit/reopen → disconnect/recover without duplicate send | C01–C07, C21–C23. No files, tools, automatic memory, Google or background work. |
| R2 · Evidence and memory | Explicit remember/correct/retract/forget; current/history/conflict inspection; selected supported local files and citations | Remember 30 days in a synthetic space → fresh recall → compare 42-day file → reject then approve correction → forget → fresh chat and no stale derived context | C08–C10; C06 review; isolated stores and held-out neural evaluation. Formats only after installed parser qualification. |
| R3 · Today and local tasks | Connect Calendar/Tasks/Gmail references; read-only brief with source times; separate persistent local tasks | Connect test account → compare permitted reads → create/complete local item → copy one provider task as explicitly independent draft → reconnect/disconnect without account substitution | C11/C12. Gmail bodies/send, provider writes and task sync absent. Expired credentials are Needs consent, not fake online. |
| R4 · Repeatable reads | Save/validate/version a linear read step list; manual run; timeline; bounded budgets; explicit interrupted/partial outcome | Calendar read → Tasks read → brief; run twice → two run records; cancel → reopen; fail required input → synthesis withheld | C14/C15. At most 6 steps, no loops/nested autonomous delegation/external writes. Fresh run authority, not stored ticket IDs. |
| R5 · Daily brief and quick access | One fixed-zone daily read schedule, pause/future resume, next/last/missed outcomes; optional background mode; quick-chat view | Review next occurrence → observe one → pause → sleep/restart with documented skip → quick/main share one conversation and command identity | C16/C17/C19. Existing scheduler must pass trusted routing/time/stop gates. No catch-up, overlap, background writes or 24/7 promise. |
| R6 · Skills and roles | Inspect actual bindings and tools; synthetic qualification; reviewed version publish/rollback; dependency view | Inspect Document Analyst → run bounded fixture → reject skill update → approve version → disable and observe dependent workflow blocked | C18/C20. Reconcile all 47 IDs as mapped/deferred/unresolved; no invented prompts or inherited new rights. |
| R7 · Project review | Scoped repository status/diff inspection and a draft plan | Select permitted repo → inspect actual bounded diff → reject unsupported command → reopen evidence | C20. Read-only core. Each write/send/native module is an optional separately advertised, genuinely qualified addition under C13. |

R7 optional modules are not a bundled promise: exact Google operation, Gmail send, one coding operation, or native desktop each has a separate qualification gate. Current local branch-creation evidence does not qualify arbitrary Git reads/writes. W37 stays disabled; native testing requires fresh explicit permission. The animal companion is a future UI surface, not a new agent. Fitness, live web research, external notes connectors, voice, mobile and cross-device sync are explicitly deferred. Plain model chat is not live research.

Each release refines previous focus/navigation, error recovery, citations, performance and run continuity. A new feature cannot degrade a shared permission or persistence boundary. No calendar dates are promised before the host/runtime spike is measured.

## 4. R1 implementation sequence, with stop conditions

1. **Record actual compatibility.** Inspect installed Hermes/SDK/tools and current service APIs; select extension only if C01–C07 can be enforced. Record versions, licenses, architecture and failure reasons. A tool-closed chat that cannot be demonstrated is blocked, not replaced by W35 or an echo.
2. **Package a blank but honest shell.** Windows shortcut, one data-root identity, typed IPC and real component health. Prove no renderer/generic route bypass and no second embedded-store owner. This is an internal milestone, not an accepted R1 chat product.
3. **Connect durable bounded chat.** C03 request namespace/journal, atomic acceptance and dispatch reservation, genuine Hermes invocation, canonical transcript, snapshots/cancellation and restart states. Existing transcript storage is not inference. If only final-response callbacks are qualified, display Generating then the real final; never fake streaming. Deltas require their own event qualification, not an R2 deadline promise.
4. **Bind the UX.** One-active-attempt policy, drafts/queue, composition-safe composer, inspector, keyboard/navigation and structured unavailable/error states. Provider/source output cannot execute privileged intents. No manual terminal is needed for ordinary use after documented setup.
5. **Qualify R1.** Disposable contract/fault tests → packaged Windows walkthrough → live model evidence → prior-boundary regression. Show actual outcomes and remaining limits. Fix ordinary-user friction before adding later destinations.

No separate general scheduler, memory engine, document parser, desktop driver, worker prompt framework or fallback agent loop is part of this work. New service code is integration/enforcement around existing components, with a recorded missing capability.

## 5. State and authority that every release preserves

Authoritative conversation/run/action records live in the existing service. Durable acceptance is not a UI Sending animation. Retrying a query observes; a new execution requires an explicit new bounded attempt. A command namespace cannot admit after expiry/restart even when dedup history is pruned. No exactly-once external-effects claim.

Cancel is a request until the service resolves its race; provider cost/effects may outlive local delivery. Unknown effects enter checking with fresh read authorization, not automatic retry. A new request ID cannot bypass an unresolved effect lock. All grants/approvals are task/resource/account/version/time bound and rechecked at final access. A role, retrieved document or model output cannot mint them.

Memory correction, forgetting and chat deletion have different meanings. A forget barrier fences active/derived context, makes old affected chat view-only for inference and requires a fresh conversation. Historical/provider/backup retention limits are visible. Restore cannot activate old memory without the latest deletion ledger. C21 defines deletion, quotas and compaction without retaining raw content forever merely for deduplication.

External account connection, source read permission, provider disclosure and exact action approval are separate. The app should reuse valid compatible permissions rather than repeatedly asking; it must never infer a new permission from a convenient UI route.

## 6. Evidence and handoff

All application acceptance cases currently say **Not run**. Each delivered build declares core/optional variants before testing. Mandatory advertised cases cannot be N/A; absence/denial cases remain required for omitted optional effects. Mock/contract/model/real UI/live model/live provider/native tiers are separate. Numerical model exploration in review files is finite design evidence, not application verification.

The service owner receives C01–C23, scoped synthetic fixtures and additive wire-schema requirements; worker developers keep their own task/result/prompt contracts. Before implementation, generate concrete request/event/context/action types from agreed schemas and test them against both clients. Do not silently change central registry contracts during UI work.

Later human steps, only when the relevant build is ready: confirm the actual provider/account and supported setup; complete model/Google consent outside chat; perform ordinary-user accessibility/usability walkthroughs; explicitly re-enable native testing if desired; approve signing/distribution setup before sharing. None is required to review this offline redesign, and no prior native permission is presumed re-enabled.

## 7. What this redesign closes, and what it cannot prove

[REMEDIATIONS.csv](REMEDIATIONS.csv) maps every original finding to an exact proposed contract and acceptance cases. [SECOND-ORDER.md](SECOND-ORDER.md) records risks created by those fixes, including stale lock takeover, dedup compaction, forget-derived chat, restoration, account generations, uncertainty locks, schedule edits, background Quit and multi-window drafts. The [review record](review/REVIEW.md) shows the cumulative checks rather than treating a prose rewrite as a passed app test.

Remaining dependencies are intentionally hard gates: installed host isolation/build compatibility, supported runtime pairing and migration, neural memory quality, account consent/live connector projection, actual scheduler callbacks and optional effect attribution/native driver. Until demonstrated, the relevant feature is unqualified. This plan is concrete enough to implement in order; it is not evidence that those integrations already work.
