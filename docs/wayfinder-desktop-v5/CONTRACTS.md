# Integration contract additions U01–U12

Proposed requirements, not implemented endpoints. These supplement the preserved [C01–C23 reference](reference/v4-contracts.txt); they do not silently relax it or rewrite worker task/result definitions. Where the existing implementation is narrower, keep the narrower operation until a versioned change is qualified.

## U01 — Source reconciliation and build identity

Bind every integration build to an upstream Git commit, reviewed local source hashes, conflict resolutions, dependency lockfiles, build variant and contract manifest hash. Keep a stable file import ledger; a changing source cannot be accepted as a single coherent snapshot. Exclude private/runtime/generated artifacts from imports. Preserve supplied worker directories and merge initializers explicitly.

The original checkout is read-only to this integration effort except for the already requested fetch of shared remote refs. No stash/reset/checkout/cleanup, process shutdown or registry rewrite there. No credentials or model/database directories are copied into the branch. Source import into the new branch is not live-data migration.

Build metadata separates actual executable/runtime versions from declared package pins and design labels. The GitHub UI's `v2.4` and static host/user identities cannot become product facts. Prior test reports retain their exact source/build/tier identity; they do not certify a new imported combination.

Acceptance: A01–A08, M01–M04.

## U02 — Presentation port and isolated developer previews

The GitHub design controls visual identity and composition. React components port the design; the old app is not simply reskinned with unrelated colors or linked beside the new dashboard. Preserve a screen/component/token mapping and original references for review. Reuse existing functional forms after replacing their presentation.

Production bundles all required styles/icons/fonts/assets locally, with recorded licenses. Use build-time Tailwind or equivalent generated local CSS; no runtime CDN compiler, external scripts/fonts/avatars, inline event handlers, eval, webview or remote iframe. Restrictive CSP does not get widened to accommodate the prototype. Decorative controls are removed or explicitly inert. Displayed source text is inert even inside a reference-like label.

MockWorkbench, fallback workers/spaces and random telemetry are developer fixtures only. Production never enters a fixture route after backend failure. Every preview is plainly labelled, has no production credentials and cannot write real app data. A fixture status cannot become a runtime health/qualification badge.

Acceptance: V01–V12, P01–P06.

## U03 — One inclusion manifest, two kinds of truth

Build inclusion declares which operations a named variant advertises. Runtime availability separately requires current qualified binding/version, health, scope and resource authority. Enforce both at final service admission; a renderer filter is insufficient. Unknown operation/version is rejected, not passed through as generic JSON.

Use one manifest to generate navigation, command palette entries, examples, import validation, shortcuts and allowed bridge routes. Do not add unavailable Notion/pet/scheduler/Gmail-send controls to suggest completeness. Historical records may be read-only if their schema is supported and access permitted; they never authorize replay.

An internal `workspace-parity` milestone retains the exact existing scoped backend-workspace functions. It is not advertised as an accepted core R1/R2 release. Core R1 keeps Chat/Runs/Settings and its exclusions. Core R2 includes memory/documents only after its full gates. One codebase and service serve these declared build capabilities; do not introduce competing runtimes or a user-facing unchecked feature-unlock switch.

Acceptance: A07–A08, V10–V12, W01–W03, M05–M07.

## U04 — Typed boundary and transport budget

Generate and validate concrete request/result/event types at preload, main/Python and final service boundaries. Replace permissive `Row`/arbitrary dictionary dispatch with decoders for advertised intents. Existing worker schemas and ToolResult remain upstream-owned; adapters explicitly validate supported fields/versions and preserve warnings/provenance. An envelope success field is not authority or effect verification.

All persistent IDs, versions, generations, revisions and sequence counters remain opaque strings or exact decimal strings at the JS boundary. Never convert INT64 counters/identities to JS Numbers. Service-derived owner/account/runtime identity is not accepted from renderer input. Reject additional command fields, oversized strings, nesting and unknown enum values before dispatch.

Retain C04's 64-KiB frame target, bounded chunks and 128-frame/1-MiB out-of-order buffer. Existing 128-KiB host framing is an inspected limit, not a reason to weaken C04. Large records need bounded pagination/artifact viewing, not silent truncation or a larger unreviewed bridge. The effective limit is the minimum of every layer's qualified bounds. Renderer input never contains host credential material or arbitrary local paths; a trusted picker returns scoped selection references.

Acceptance: B01–B08, Q03–Q05, E07–E08.

## U05 — Runtime ownership and admission namespace

Verify stable data-root identity, instance generation, process ownership, contract versions and host pairing before operations. Preserve existing runtime/storage locks. Existing project-relative `.local/wayfinder-electron` is a development default; stable packaged data-root selection/migration remains an explicit implementation task. Moving the executable or failing attach must not create an unexplained empty replacement.

Use authenticated inherited bootstrap for an owned child or an explicitly paired existing service. No PID/port guessing, weak heartbeat takeover, generic URL fallback or new storage owner. A shared Hermes process is not this app's owned child. Shutdown owns only the app's admissions, children and subscriptions; its effect uncertainty remains separately recorded.

Implement C03's main pending-command journal, expiring service namespace and durable dispatch reservation before claiming accepted execution. Expired/prior-generation namespaces may observe known status but cannot create new commands after dedup compaction. No automatic command retry, namespace renewal or new request ID on reconnect. Ordinary polling observes only.

Acceptance: H01–H10, Q01–Q08, M01–M04.

## U06 — Canonical chat and late-event fencing

Home/New chat submit ordinary conversation inference, never `store`, `claim`, a W35 request or broad tool delegation. Remember/Correct/Retract are separate named reviewed operations. Freeze provider/model/profile, bounded canonical turn IDs and disclosure policy at acceptance. A selector change affects future work only.

Use the existing managed Hermes path with tool/session/memory isolation proved for the selected binding. Provider credentials remain managed. No duplicated Hermes/global transcript and no new agent loop. If only final responses qualify, render Generating followed by the real result; animation is not streaming evidence.

Persist one authoritative final/terminal outcome. Every event carries immutable runtime/space/conversation/attempt/generation/sequence; route by those fields, not visible selection. Missing/gapped cursors recover by authenticated snapshot, not resubmission. Service compare-and-set determines completion/stop races. Cancelled partial text is labelled and excluded from future default history; upstream abort/cost stays unknown unless demonstrated.

Acceptance: Q01–Q10, E01–E08, R01–R08.

## U07 — Preserve exact review and reconcile conflicting approval systems

Use the production persistent AppService/ActionGate path for memory and qualified connector effects. Preserve upstream ApprovalService for its existing tests/contracts until an adapter is justified, but do not accept its in-memory/spent token as a second application authority. Keep a documented mapping from proposed worker action to persistent scoped service action.

A renderer review IPC asks main to load and display the exact backend proposal. The main-owned confirmation alone supplies a trusted approval decision; no renderer confirmation boolean, fabricated native callback or Markdown button can approve. If a full bounded payload cannot fit, refuse and use a separately qualified trusted review surface. Revalidate digest, owner/space/task, resource/account/binding generation, preconditions, expiry and revocation at effect admission.

Use both wall deadline and monotonic remaining lifetime in-process. A backwards wall-clock change cannot extend authority. Restart expires one-shot pending approvals. Current wall-only implementations need hardening and tests, not a plan-level assertion that this property exists.

One decision must win under multiple windows/clients. Pending, rejected, expired, revoked, dispatched, verified and uncertain states remain distinct. No frontend success badge before the service receipt. Reconciliation never mints a grant or performs a new effect.

Acceptance: P01–P10, X01–X08.

## U08 — Privacy and source limit reconciliation

Preserve scoped file handles/root identities, selected byte/hash/coverage and current authority on every access. Initial parity supports one selected qualified UTF-8 text source within the existing **2-MiB** service limit. v4's larger draft limits remain unimplemented; a UI cannot widen them. Effective extraction/model/root budgets may narrow the limit further. Revocation prevents future access/delivery and cannot undo prior provider disclosure.

Preserve source/history/current distinctions and parser uncertainty. Historical citations resolve retained scoped evidence; reopening current content requires new permitted access and labels changes. A source URL/path is never an app command or unrestricted file opener.

Full forget requires the C09 barrier, context epoch, lineage invalidation, purge tracking and latest-deletion-ledger restore gate. Retraction and current artifact clearing are narrower existing operations. Label them accordingly. After forget, pre-barrier conversations are view-only for inference; a new conversation excludes old paraphrases/turns. A failed purge leaves the scope privacy-blocked.

Separate transcripts, facts, retained excerpts, temporary artifacts, logs, credentials and minimal receipts. Content deletion does not secretly preserve unsalted content hashes as an uncertainty key. Recovery of older backups is quarantined until the newest verified deletion ledger is applied. No universal secure-erasure/provider-delete claim.

Acceptance: D01–D10, F01–F10, N01–N04, M01–M04.

## U09 — Account identity, projection correctness and local tasks

Keep connection configuration, authenticated account identity, granted scopes, operation qualification, exact resource permission and health separate. The existing credential-file fingerprint is useful change detection; it is not stable Google account identity. Qualify an appropriate provider identity binding before production use; no extra identity scope is assumed silently.

Google reads stay fixed-endpoint, bounded, explicitly paginated/partial and credential-free in workers/renderer. Current Calendar/Tasks/Gmail-reference adapters require account lifecycle and projection tests, not a new OAuth server. An app-owned human consent surface never posts tokens through chat. Switching/disconnecting/replacing accounts bumps generation and suppresses late old-generation delivery. Stable account uncertainty locks survive reconnecting that same account.

Preserve task provider ID/list ID/raw status/version/observation time in trusted projections. Map `needsAction` to displayed pending, completed to completed, and unknown to unsupported. A due date is a date, not a midnight timestamp to timezone-shift. Display calendar zone/range/coverage and partial reads; two endpoint reads are not an atomic schedule snapshot.

Local WorkItems live in existing app storage with owner/space/version checks. Direct user reversible edits have explicit target/version; model-proposed edits use trusted review. One-time Copy to local is a new independent draft with provenance. No provider writeback, implicit import, duplicate linking, automatic task resurrection or two-way sync. Disable/disconnect/provider revoke are different labelled operations.

Acceptance: G01–G12, T01–T08, X01–X08.

## U10 — Unknown effects, root workflows and imported role contracts

An upstream TaskPlan is a proposal, not authorization for its workers/tools. Validate the exact advertised allowed step kinds, pinned role/schema/binding versions, resources, disclosure and aggregate budgets. R4 admits ≤6 linear steps with earlier dependencies, not an imported arbitrary DAG or recursive delegate. Required source failure blocks synthesis; stale five-minute source edges cannot become fresh via UI refresh.

Existing fixed recipes keep their tighter limits. Proposed workflow ceilings are ≤2 model calls, 10 minutes, one globally active actual model call and ≤3 attempts per qualified provider read, all charged to the root. Child creation cannot reset a budget. Cancellation prevents new children; restart interrupts rather than replays. Read-only retry and effect reconciliation are separate routes.

Stable account/resource/operation-family duplicate locks are service enforced across all clients, connection generations and list pagination. A UI/Main-only duplicate guard is useful but insufficient as final global authority. A new title/request ID or deleting a visible run cannot unlock an unknown effect. If erasure removes fine attribution, retain only a minimal conservative family lock and explicit uncertainty.

Only a separately advertised exact-operation module may write/send/execute. The local branch module does not enable other Git operations. Actual provider/host receipts and independent attribution are required; similar items, ACKs and fixtures are insufficient. Worker identity and a successful validation schema never approve their own rights.

Acceptance: W01–W10, X01–X08, J01–J08.

## U11 — Existing scheduler and shared quick view

R5 requires real installed-Hermes callback evidence: exact fixed IANA zone, first fold only, gap/late/offline skips, no overlap, unique durable occurrence ID, app-bound callback and disabled/retired generation fencing. A recurring prompt or browser timer is not the qualified path. Default background is off; ≤30-day standing read authority is separately reviewed and bounded.

Changing a schedule/template/resource/policy needs a future-effective reviewed revision. Pause stops future admission, cancel-active is separate, and resume covers future occurrences only. Quit commits the app admission-stop epoch before success; unsupported stop fencing keeps background unavailable. Never kill shared Hermes to simulate successful app shutdown.

Quick chat is another view of the same runtime and canonical conversation. Main owns one revisioned composing draft lease; a second window observes or explicitly takes over. Same-command replay rules remain authoritative. Hotkeys are opt-in, conflicts remain visible, bounds recover across DPI/display changes and notifications contain no private body or approval capability.

Acceptance: S01–S12, K01–K08, H06–H10.

## U12 — Acceptance evidence and rollback discipline

Each build declares source hashes, schema/operation inclusion, dependency versions/licenses, asset manifest, migration floor and exact variant before its acceptance run. Every required case is Pass, Fail, Blocked or Not run with tier-specific evidence; N/A needs a predeclared exclusion and reason. Historical source/fixture/build counts do not establish a new packaged UI, neural memory, account or native pass.

Run static/contract/storage/rendered/package/live tiers separately and retain failures. Test layout/focus with real rendering, and native dialogs/accessibility on the packaged Windows application. No screenshots, screen reader, W37 or account actions are executed during this planning task. Actual Windows app usage is distinct from authorizing a computer-use worker.

No automatic main merge, system upgrade, active-runtime reconfiguration, remote publishing, installer signing or distribution. Binary rollback is not data rollback. Use verified compatible backups in isolated roots with current deletion/uncertainty barriers. Measure UI performance and actual/unknown cost; never present random or estimated values as telemetry.

Acceptance: V01–V12, L01–L08, M01–M08, N01–N06.
