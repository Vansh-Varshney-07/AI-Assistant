# Wayfinder desktop: new GitHub interface, existing application backend

Revision 5 · 26 October 2026 · Windows first · proposed, not implemented

**Goal:** use the newly supplied Wayfinder/Stitch interface as the presentation source, connect the user's existing application services and completed features, and deliver the remaining product in small releases with explicit acceptance gates. Preserve the reference plan's C01–C23 requirements. This plan changes neither worker prompts nor the memory/runtime architecture.

**Current instruction:** planning only. The GitHub fetch and isolated branch creation have happened; UI/backend integration has not started. No source import, application edit, dependency installation, account connection, database migration, desktop launch or native automation is authorized merely by this document.

## Read this package

- [Readiness and source reconciliation](READINESS.md): observed code versus reported tests versus proposed work.
- [Integration contracts U01–U12](CONTRACTS.md): UI migration and backend adapters, supplementing [reference C01–C23](reference/v4-contracts.txt).
- [Screen and feature integration map](SCREEN-MAP.md): what each GitHub screen becomes, which service it uses and what stays unavailable.
- [Flows](FLOWS.md): ownership/startup, accepted requests, reviews, memory privacy, account reads and scheduling.
- [Acceptance matrix](ACCEPTANCE.csv): specific scenarios and required outcomes; every implementation case starts **Not run**.
- [Risk and self-review register](RISKS.csv): design findings, new failure modes, containment and regression IDs.
- [47-role coverage](WORKER-COVERAGE.csv): supplied definitions, local infrastructure, aliases and unresolved IDs without invented roles.
- [Proposed release manifest](manifest.json): a planning artifact, never a live permission/availability file.
- [Source fingerprints](SOURCES.json) and [reference plan](reference/v4-plan.txt).

No mock, fixture, reported count, source review or generated package substitutes for a tested application release. No claim is made that a finite review proves all risks absent.

## 1. Freeze the actual starting point

| Input | Inspected state | Consequence |
|---|---|---|
| GitHub | `origin/main` fetched to `7b59c06d817a08b53d1f139764a757ac9acfdbd9` | Contains the new interface and 16 numbered worker definition directories. Freeze this exact commit for integration; do not chase moving main mid-batch. |
| New branch | `codex/ui-backend-integration` at that commit | Separate checkout; no merge to main or push is part of this planning task. |
| New UI | `workbench/index.html`, `app.js`, `style.css`, plus `stitch_wayfinder_ai_desktop_interface/` references | Visual source, not proof of working product routes. Keep the recognizable design; replace sample data and unsafe runtime wiring. |
| GitHub workbench backend | `workbench_server.py`, direct `Workbench`/MemoryEngine routes and an explicit MockWorkbench preview | Developer workbench only. Do not route production desktop operations through it. |
| Local app backend | Uncommitted `wayfinder/service.py`, API, workers, platform modules and tests | Must be imported by an explicit reviewed file manifest. GitHub alone does not contain all application work. |
| Local desktop client | Uncommitted `desktop-app/`: Electron/React/TypeScript, narrow preload/main broker, Python host and feature inventory | Candidate reuse for the delivery host and existing feature forms; not the visual authority and not accepted as complete R1–R7. |
| Local planning | v4 plan and C01–C23, including privacy, request journal and release requirements | Retain as requirements. Reported local test results do not prove every requirement already exists. |

The worktree was created at `C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant`. Codex's attachment retry reported that this side-chat ID could not be registered. The checkout and branch exist; automatic chat attachment is not established. Use the explicit path and confirm it before future commands. Do not create another worktree to conceal the registration failure.

The original checkout remains `D:\Opencode_\AI assistant` on `codex/platform-integration`. It has concurrent uncommitted work. Do not switch it, stash it, reset it, clean it, stop its services or overwrite its files. Fetching updated shared remote refs; it did not merge its working files.

### Source-import procedure before implementation

1. Record branch/commit, source paths and hashes for upstream UI/worker contracts, the local backend/client and all relevant dependency/contract files.
2. Read each selected local file into a frozen import snapshot; verify metadata/hash again after reading. A changed file is retried or flagged, not silently mixed with an earlier contract version.
3. Copy only reviewed source, tests and necessary documentation into the isolated branch. Exclude `.local`, node_modules, build/release outputs, credentials, data, databases, model caches, OAuth files and unrelated benchmark work.
4. Preserve GitHub's worker directories, shared schemas and upstream package initializers. Merge the local flat worker modules by exact path; never replace the whole workers directory or registry with an older local tree.
5. Review collisions separately: root requirements/README, `wayfinder/__init__.py`, worker initializers, registry fragments and scripts. Use a recorded resolution; no blanket ours/theirs.
6. Run old and new contract suites before UI migration. A green old suite does not qualify imported worker execution. Record failed imports and missing prerequisites without repairing live data.
7. Only integration-branch commits are eligible for review. Main remains unchanged until a later explicit merge request and acceptance evidence.

## 2. Keep one stack and one authority chain

```text
GitHub design references → local React components and bundled assets
                       ↓
untrusted renderer → named preload intents → validated Electron main broker
                       ↓
owned/paired Python host → authenticated AppService/API
                       ↓
existing policy, WorkerHub, Atlas, memory gateway and connector handlers
                       ↓
managed Hermes/OpenShell + existing Iron Web/FalkorDB/Qdrant + selected providers
```

| Layer | Decision | Qualification / stop rule |
|---|---|---|
| Host | Reuse the existing thin Electron host as the integration candidate. | Verify runtime pairing, isolation, startup and package behavior. Do not reopen an extension/Tauri rewrite unless a measured unmet requirement justifies a separate decision. |
| UI | Port the new GitHub structure, tokens, typography, navigation and page composition into React/TypeScript. | Side-by-side design mapping and rendered checks; no new unrelated redesign. Preserve useful existing backend forms in the new design. |
| Assets | Build CSS locally; bundle approved fonts/icons/assets with license records. | No Tailwind CDN, external font request, remote avatar or executable remote asset in the desktop renderer. Fail packaging on missing assets. |
| Client state | React view/draft state plus validated service snapshots. | No second transcript, optimistic success authority, stored access tickets or raw drafts in localStorage. A query library is optional and must not retry commands. |
| Bridge | Existing named preload/main/Python adapter, hardened where a C01–C23 gap is demonstrated. | No generic HTTP, shell, filesystem, eval or renderer-controlled approval method. Verify every originating top frame and decoder. |
| Backend | Existing AppService, API, WorkerHub, scoped memory gateway, file broker and ActionGate. | Add small versioned service facades where needed. Do not open raw SQLite or stores from renderer/Node. |
| Upstream tools/contracts | Preserve supplied worker definitions, `ToolResult` and deterministic helpers. | Adapt semantics explicitly; fixture success and an envelope `success` flag do not grant rights or independently verify effects. |
| Approval | Existing persistent exact-action/service boundary is authoritative for application effects. | Upstream in-memory ApprovalService is not a parallel approval authority. Any imported token is advisory until a qualified trusted adapter validates the exact persistent action. |
| Chat | Existing Hermes managed execution, application-owned history. | No new reasoning loop and no W35-as-chat fallback. Tools, inherited history and automatic memory must be demonstrably closed for R1. |
| Scheduling | Existing Hermes scheduler only, through a qualified fixed app callback. | No renderer interval, Node cron or replacement scheduler. Defer R5 if trusted routing/time/stop semantics fail. |

Before each subsystem: inspect installed runtime/SDK/effective capabilities, existing repository adapters/tools/skills/MCP, select suitable reuse, record the missing integration, then implement only that gap. Source/version inspection is not authorization to upgrade or reconfigure active services.

## 3. Preserve the new interface without preserving its demo behavior

Visual anchors to preserve: the WAYFINDER identity, compact grouped navigation, command-portal header, cyan accent, technical typography, square/precise panel treatment, light/dark themes, card/list hierarchy, activity timeline and source inspector. Refine spacing/reading size rather than increasing dashboard density indiscriminately.

Remove from production: random CPU/RAM values, sample worker runs, default fake spaces, static connected-service counts, SYS_ADMIN/LOCAL-HOST-01 labels presented as facts, sample calendar/tasks, hardcoded verified policy badges and fake pet/window controls. Runtime version and ownership come from the selected instance. Undefined readings show Not measured or Unavailable.

The current Home submission calls a store operation. The integrated Home composer must submit ordinary chat only. Remember is a separate named action and review. Entering a sentence, pressing a quick action or selecting a worker must never silently publish durable memory.

MockWorkbench and design previews may remain explicitly isolated developer references with a visible fixture label; they cannot be selected by production startup failure or an API exception. Remove fallback workers/spaces from production adapters. A real error remains an error with recovery instructions.

The new UI's home/planner/Notion/workflows/activity/connections/permissions/pet/memory/settings screens are not ten promises to enable immediately. [SCREEN-MAP.md](SCREEN-MAP.md) maps each to an accepted capability or a declared unavailable/deferred state. Hidden features cannot be reached through palette, deep link, import, shortcut, stale renderer or API bypass.

### Layout and interaction

- Wide: grouped navigation → current conversation/list → main content → one optional inspector. The Home heading/summary and command composer remain recognizable from GitHub.
- Narrow: a real navigation drawer and one inspector sheet, never two simultaneous modal layers. Escape, focus trap, opener restoration and resize recovery are required.
- Main conversation remains primary; metadata is progressively disclosed. IDs, raw schemas and tool lists live in Advanced evidence, not every ordinary action.
- Every screen has loading, genuinely empty, stale, partial, denied, unavailable and error states. Last observed data is timestamped and cannot masquerade as fresh.
- Composer supports IME, Enter versus Shift+Enter, keyboard-only use and visible focus. No fabricated streaming or token counts.
- Window controls call only the host's close/minimize/maximize intents; they do not terminate shared Hermes or authorize desktop automation.
- Accessibility targets retain v4: 1280×800 and 1920×1080; 600px narrow layout; 100/125/150% DPI; long content, reduced motion, forced colors, keyboard, IME and screen reader.

## 4. Delivery ladder: parity first, then the unchanged core release gates

**I0/I1 are integration milestones, not an excuse to call the current workspace R1 or R2.** One application codebase and backend are used throughout. An internal `workspace-parity` build preserves and verifies currently completed scoped features in the new design. It is labelled with that exact capability set and is not advertised as the complete v4 core. Core R1–R7 retain their original inclusion/exclusion rules; no failed required feature is reclassified as optional after testing.

| Milestone / release | Deliverable | User-visible test | Gate / explicit exclusion |
|---|---|---|---|
| I0 · Frozen integration baseline | Reviewed source import, conflict map, compatibility matrix, regression report and one authoritative route/feature map. | Inspect exact upstream/local revisions and see that the original checkout is preserved. | No UI launch, production-data copy, dependency upgrade or invented worker implementation. |
| I1 · New-design backend parity | New GitHub visual system around existing spaces, scoped memory events/evidence, file selection/W35, fixed comparison, runs/reviews/audit, runtime discovery/settings and separately declared existing local-branch module. | Complete the current backend-workspace walkthrough in the new design; offline errors remain honest; approvals remain trusted. | This is not general chat, full forget, Google live access, workflow builder or scheduler acceptance. Activity CSV remains an optional local diagnostic; fitness is deferred. |
| R1 · Real conversation | Ordinary bounded model chat, canonical persisted conversation history, stop/recovery and component health. Core navigation Chat, Runs, Settings. | Novel question → actual answer → stop another run → quit/reopen → lost response recovery without duplicate execution. | C01–C07/C21–C23. No files, automatic memory, Google, tools or background work in core R1. |
| R2 · Evidence and memory | Explicit remember/correct/retract/forget; current/history/conflict inspection; selected qualified documents and citations. | Synthetic 30-day memory versus 42-day file; reject/approve correction; forget; new chat excludes old derived context; restore cannot resurrect it. | C08–C10. Current retraction/artifact clearing alone do not meet full forget. Held-out neural gate remains required. |
| R3 · Today and local tasks | Selected Google Calendar/Tasks/Gmail-reference reads; timestamps and exact resource grants; separate durable local tasks. | Connect intended account, compare bounded reads, edit a local task, copy a provider item once, reconnect/disconnect without account substitution. | C11/C12. Gmail bodies/send, provider writes and two-way task sync absent. |
| R4 · Repeatable reads | Versioned linear templates of at most six qualified steps, manual starts, timeline, budgets/cancellation and explicit interrupted/partial outcomes. | Calendar → Tasks → brief; two deliberate runs; cancel/reopen; required source failure withholds synthesis. | C14/C15. No arbitrary DAG, nested agent spawning, external writes or resuming half-executed effects. |
| R5 · Daily brief and quick access | One fixed-zone daily read schedule, skip/missed states, pause/resume, optional visible background mode and shared-runtime quick chat. | Preview next occurrence; duplicate callback; DST gap/fold; sleep/restart; Quit fence; main/quick same conversation/draft identity. | C16/C17/C19. No catch-up, overlap, general cron editor or independent quick-chat database/session. |
| R6 · Skills and worker inventory | Reconciled W01–W47/aliases; versioned existing bindings, evidence, synthetic qualification, reviewed publish/rollback and dependencies. | Inspect a real binding; reject then approve a permitted configuration version; disabling blocks dependent next steps. | C18/C20. No inferred mappings, new worker prompts, automatic plugin installs or permission increases from skill text. |
| R7 · Read-only project review | Bounded repository status/diff and qualified draft review. | Select permitted repo; inspect actual diff; reject unsafe helpers; reopen historical evidence. | C20. Local branch creation does not qualify arbitrary reads, hooks, tests, commits, checkout, push or merge. |
| Optional modules | One exact external write/send/coding/native operation per declared variant. | Real provider/host action with exact review, attributed receipt and lost-ack reconciliation. | C13 and U10. Default off. W37 still disabled until separately re-enabled and qualified. |

Existing backend functions are not deleted to make the new UI look cleaner. Their service contracts and regression tests remain; the release manifest controls which precisely named build advertises and admits each operation. No second product runtime is introduced for a preview variant.

## 5. Concrete implementation batches and stop conditions

### Batch A — Import and compatibility (I0)

Deliver source manifest, collision resolutions, preserved worker contracts, declared dependencies/licenses, route inventory, baseline test report and stable data-root decision. Inspect actual Node/Electron/Python/Hermes/Windows/WSL versions; package.json pins are declarations, not runtime evidence. Choose one supported lockfile/build path. A failure does not trigger system/runtime upgrades.

Block if local source is changing too quickly for a coherent snapshot, existing tests cannot load under the merged package, required contracts conflict, a storage owner cannot be identified, or the selected host needs privileges the service cannot enforce. Do not use a mock backend as an integration substitute.

### Batch B — Local design port (I1a)

Extract upstream tokens and component structure. Build local styles/fonts/icons, preserve source license records, replace inline/CDN scripts and sample identities. Port one screen at a time: shell → memory/evidence → documents → activity/reviews → settings/capabilities → declared repository module. Reuse real feature forms and existing main broker logic after review. Remove decorative no-op buttons or give them explicit disabled reasons.

Deliver design-token/component mapping, original-to-new screen references, responsive layouts, strict CSP, route manifest and inert source-rendering tests. Do not yet add model chat, provider writes or arbitrary workflow orchestration just to populate cards.

Block if renderer needs a generic privileged route, source HTML executes, local assets are missing, a feature falls back to fixtures, or any real backend feature loses its review/revoke/reconcile path.

### Batch C — Authenticated backend parity (I1b)

Connect through the existing preload/main/Python host. Move direct store queries behind narrow service-owned list/read facades with scope checks and bounded pagination; Node/renderer never become application-store owners. One data-root identity and compatibility descriptor must precede service start/attach. Retain existing API browser-Origin rejection.

Acknowledge proposed versus stored versus verified outcomes accurately. Bind all pending views and selections to owner/space/task/runtime generation, not current navigation. Publish component health, real run state, actual current/history memory and opaque citation references. Wire all feature entry points through the same service inclusion check. Test failures with the real disposable storage stack and source-rendered app.

Block if approving from a forged renderer can skip trusted main confirmation, the imported in-memory approval service can independently authorize effects, newer runs contaminate another space, old pending effects disappear behind a recent-page limit, or the host can open a second live embedded store.

### Batch D — Genuine conversation (R1)

Add only missing application-service chat acceptance, history selection, durable reservation, cancellation/events/snapshots and command-journal integration. Hermes owns reasoning/inference. Do not repurpose the W35 task contract or use a transcript echo as a reply. Show provider disclosure and a qualified model/profile; no automatic model/provider fallback.

First qualify a final-response-only path. Stream deltas only if the installed route supplies genuine sequenced callbacks and passes reconnection/race tests. Service commits authoritative final transcript and terminal state together. Test disk full, crash before/after reservation, stale namespaces, duplicate sends, cancellation/completion races and late events across spaces/windows.

Block if effective tools/history/memory cannot be closed, model output is fabricated, usage/abort is misreported, or the existing AppService prerequisites cannot be met without a hidden alternate store. A polished I1 workspace is not a substitute for R1 chat.

### Batch E — Privacy-complete evidence (R2)

Reuse scoped FileBroker, W35/Hermes extraction, ContextGateway, Iron Web claim events and supported deletion APIs. Bind file identity/hash/coverage/disclosure to each request. Add the missing durable forget barrier, lineage/epoch invalidation, cross-copy purge tracking and restore ledger policy before exposing a full Forget label.

Current local FileBroker limit is **one qualified selected file up to 2 MiB** for the first port. v4's draft 3-file/5-MiB limits are aspirations, not permission to raise this limit. Effective limits are the minimum of service, parser, model, disclosure and root-run budgets. Broader formats/multi-file support require separate evidence and versioned acceptance.

Deliver deterministic privacy/scope/durability tests plus pre-registered 40 held-out neural answer cases; retain v4's proposed ≥38/40 target and zero observed unauthorized access, false saves, fabricated sources or forgotten-source resurrection. A failure blocks the advertised memory capability; do not tune on the held-out set then reuse its result.

### Batch F — Selected Google reads and independent local tasks (R3)

Reuse prepared Google OAuth/read adapters and fixed endpoints. Human account consent occurs only when a reviewable app flow is ready. Add verified account identity/generation, selected resource/disclosure policy, projection versions, safe errors and explicit disable/disconnect/revoke semantics. Credential-file presence or a matching file fingerprint alone is not stable Google account identity.

Preserve raw Google status/version/source fields in trusted projections. Explicitly map Tasks `needsAction` to local display `pending`; unknown states remain unsupported. Date-only due dates do not undergo local-time conversion. Calendar view uses an explicit IANA zone and coverage/observed time. Missing pages and permissions are not empty schedules.

Add WorkItem records in existing application storage using scoped version checks. Provider tasks remain separate. One-time Copy to local produces an independent draft with provenance; no synchronization or writeback. Imported model suggestions require review, while direct reversible form edits need no redundant confirmation.

Block if a reauthenticated different account inherits old grants, secrets enter renderer/logs, required fields are dropped silently, provider data becomes commands, or local/provider task identities are conflated. No Gmail body or send control in R3.

### Batch G — Bounded workflows (R4)

Reuse existing workflow/WorkerHub/Hermes routing and lifecycle. Add only template validation, root admission/budget accounting and typed evidence flow. At most six linear steps, declared earlier dependencies, two model calls and ten minutes per root; one actual model call active globally. Read retries are operation-qualified, at most three attempts total and root-deadline bounded; auth/scope/account failures do not retry. Existing fixed recipes retain their stricter limits.

Every run pins template/binding/profile versions, account generations, resource intentions and context epoch. Each source edge carries provenance and five-minute first-recipe freshness. Required input failure stops synthesis. Restart interrupts and permits observation; a new read run needs explicit intent and fresh authority. No stored expiring ticket becomes reusable standing permission.

Block on an invalid import/raw JSON bypass, stale edge used as current, disabled role still executing a next step, nested worker budget multiplication or effect replay through a parent retry.

### Batch H — Scheduler and quick access (R5)

Qualify installed Hermes scheduling against fixed IANA zones, first DST fold only, gap/late/offline skips, no overlap, unique occurrence admission and authenticated app callbacks. Standing read authority is separate from one-shot approval, with ≤30-day validity and current rechecks. Schedule edits/resume affect future occurrences; no catch-up or hidden renewal.

Background defaults off. Tray/Close/Quit semantics must be visible and service-fenced; app Quit never kills shared Hermes. Quick chat shares main's runtime, conversation, command IDs and draft lease. OS hotkey registration is opt-in; conflict is an error, not replacement. No pet, desktop scanning or native control enters through quick access.

Block R5 if actual callbacks cannot preserve the stop fence, time policies or routing limits. Timezone arithmetic tests alone cannot qualify recurrence.

### Batch I — Binding management and projects (R6/R7)

Reconcile all 47 IDs against supplied definitions, aliases, installed profiles and actual source schemas. Import through one versioned registry path. No role counts become running-process counts. Configuration edits are reviewable new versions; capability increases invalidate dependent authority. Rollback changes future configuration only.

Resolve naming/authority conflicts explicitly: the v4 coverage calls W01 Orchestrator, while GitHub defines W01 Intent Analyst. Preserve the supplied definition and record the conflict; never equate that logical worker with the authenticated trusted orchestrator. Similarly, W10 Document Analyst and local W35 Local File Analyst are not automatically interchangeable because their names overlap. A mapping requires an explicit compatible adapter and effective-tool/disclosure evidence.

Read-only Projects requires its own safe adapter: bounded status/diffs, external helpers/hooks disabled, resource/path/size checks, no arbitrary command string and explicit source/version evidence. Existing branch creation remains a separately declared optional operation. Other external effects need operation-specific C13 admission, receipt/attribution/reconciliation and duplicate-family locking, not just shared approval UI.

## 6. Preserve state, authority and retention across every batch

The renderer may request; the trusted service decides. Source text, a model reply, a worker name, Atlas result, UI badge or newly imported approval token cannot mint grants, change scope, approve an action or execute a link.

Application records own conversations/run/action state. One runtime owns one stable data root. An executable move must not silently select a fresh empty root. Startup verifies schema/descriptor and storage ownership before admitting work. A service heartbeat or stale PID is not authority to steal a lock. Migration/rollback uses verified supported backups while stopped/drained; no live-store copy.

Use C03's durable main command journal and service-issued admission namespace. Same ID/same payload observes; changed input fails. Reserve dispatch durably before model/provider access; crash after reservation is interrupted/unknown and cannot silently redispatch. Retired namespaces remain unable to admit old compacted commands. No exactly-once external execution claim.

Approval freezes exact scope, ordered parameters, account/resource/binding versions, preconditions, evidence, expiry and digest. Trusted main re-reads the service record before displaying bounded exact review. A renderer `approved=true` flag is never authority. Enforce wall and monotonic expiry in-process; restart requires fresh one-shot review. This is a qualification requirement, not a claim that every existing gate already implements it.

Unknown outcomes are independently tracked even if the parent chat is cancelled. Stable account/resource/operation-family uncertainty locks survive connection generation changes and pagination. A new title/window/request ID does not bypass them. Reconciliation is current, attributed, read-only inspection of the original effect, not another write. If evidence is erased, widen the minimal family lock instead of retaining hidden deleted prose.

Use v4's separate retention classes and policy: transcripts/explicit memory until deletion; task artifacts 24 hours unless explicitly retained; redacted logs 7 days/10 MiB; content-free receipt/dedup metadata 30 days followed by safe compaction; unresolved effect markers and deletion barriers retain their minimum required identity. Initial app-content quota 250 MiB warning/500 MiB admission stop is proposed and must be measured. Never delete unresolved receipts or facts merely to free space.

Retraction, full memory forget, chat deletion and platform-artifact clearing remain separate controls. After forget, pre-barrier conversations become view-only for inference and a new chat starts without old turns. Restore applies the latest verified deletion ledger before activation; otherwise quarantine. Provider disclosures, independent backups and user exports have separately visible limits.

## 7. Proof required, not merely implementation activity

| Tier | Evidence | Cannot establish |
|---|---|---|
| Source/static | Build/type/lint, exact IPC routes, asset/CSP checks, manifest/schema correspondence. | Runtime behavior, visual quality or provider connectivity. |
| Contract/fault | Actual handlers with declared fixtures; adversarial inputs, races, disk failure and restart. | Neural quality, real UI or actual external effects. |
| Storage integration | Disposable FalkorDB/Qdrant, scoped writes/receipts and recovery. | Production-data migration or general model reliability. |
| Rendered browser | Bundled renderer at required sizes/themes, screenshot comparisons and keyboard behavior. | Packaged Electron sender checks, Windows native dialogs or W37. |
| Packaged Windows | Actual launch/close/reopen, native user pickers/reviews, DPI/navigation/accessibility and owned-process lifecycle. | Computer-use permission or live Google/model correctness. |
| Live Hermes | Selected managed profile, zero-tool/no-memory proof where required, synthetic prompts and measured outcomes. | All 47 roles or provider connectors. |
| Live Google | Selected account/resources, redacted counts/evidence, correct projection and consent lifecycle. | Gmail send, two-way sync or arbitrary account writes. |
| Native optional | Separately authorized real host action with attributed verification and failure reconciliation. | General desktop autonomy. W37 is currently disabled. |

Separate output directories and report labels by tier/build/commit. Keep failed cases. Do not add overlapping test counts into a reliability number. Old parent test reports are historical evidence for those exact snapshots; rerun affected tests after import/port.

A release needs all required acceptance cases for its declared variant, a Windows-launchable build, dependency/license/compatibility inventory, start/stop/recovery instructions, measured performance, a short ordinary-user walkthrough and known limitations. Missing mandatory tests mean Blocked or Not run, not N/A. An omitted optional module still requires denial/absence tests.

Measure UI acknowledgement p50/p95 separately from provider latency; proposed targets remain submit/stop acknowledgement <250 ms and cached chat open <500 ms. Record cold start, idle resources, memory/graph/vector health, long-history behavior and provider cost as measured/unknown. No fake telemetry or invented estimates.

## 8. Human steps and completion definition

Nothing external is needed to review this plan. During implementation, human steps are limited to account/provider consent and disclosure choices, actual-user accessibility/usability confirmation, explicitly re-enabling native testing if desired, and signing/distribution decisions before sharing. Do not repeat compatible authorizations; explain a genuinely new resource/scope/version need at the concrete review surface.

Google Calendar/Tasks and Gmail are the recorded provider choice; fitness is deferred. No credential/token/client JSON should be pasted into chat. This planning task does not start OAuth or inspect private account content.

**I1 complete:** the new GitHub visual system controls the declared backend-workspace functions through the existing trusted app boundary, all parity/denial cases pass on the frozen source set, and no fake state or regressions remain hidden. **Core product complete:** each advertised R1–R7 capability passes its cumulative gate. A beautiful screen, successful package build, role definition or fixture pass alone is insufficient.

Until the next explicit implementation instruction, leave this package as proposed design. Do not merge the original branch, launch the app or connect accounts as a side effect of writing the plan.
