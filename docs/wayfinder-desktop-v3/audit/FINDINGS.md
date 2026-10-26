# Detailed findings

Design review of the v3 plan. P0 blocks committing to the R1 implementation contract; P1 must close before its affected release; P2 is a concrete usability, integration or coverage gap. These are not claims of exploitable production vulnerabilities. Existing backend guards are not assumed absent merely because a future desktop contract is incomplete. Refer to REPORT.md for methods, evidence and limits.

## F01 · P0 · Canonical chat history and authority are not contracted

**Release:** R1. **Evidence:** Design gap. **Status:** Open.

- **Basis:** PLAN.md:92; PLAN.md:172; wayfinder/service.py:417.
- **Failure path:** New conversation -> Hermes inherited session/profile -> unselected history or tools enter reply.
- **Required amendment:** Define canonical transcript/session mapping; R1 tools and automatic memory closed; R2 memory only through scoped gateway; bind model/profile versions.
- **Acceptance:** Fresh R1 chat with an existing Hermes profile/history; Switch space/model while a prior reply is pending.
- **Expected:** No implicit old-space context or broadened tools; original run retains its binding.

## F02 · P0 · Runtime attach, authentication and ownership handshake is incomplete

**Release:** R1. **Evidence:** Design gap. **Status:** Open.

- **Basis:** PLAN.md:170; wayfinder/runtime.py:28; wayfinder/service.py:67.
- **Failure path:** Double launch -> each discovers a different endpoint or starts a new root -> split state; Quit may stop a shared runtime.
- **Required amendment:** Specify stable app-data root, instance/API/schema descriptor, authenticated attach/start lease and owned-versus-shared shutdown. A port or PID alone is not proof of identity.
- **Acceptance:** Double-launch during slow startup; Quit a UI attached to an already shared backend.
- **Expected:** Exactly one owner of the selected data root; authenticated attach; no unrelated service termination.

## F03 · P1 · Crash-safe chat acceptance and dispatch are only an intention

**Release:** R1. **Evidence:** Missing contract. **Status:** Open.

- **Basis:** PLAN.md:172; ACCEPTANCE.csv:R1-04.
- **Failure path:** Submit -> durable acceptance -> lost acknowledgement -> new request ID -> duplicate inference/cost.
- **Required amendment:** Persist request hash, user message and run identity atomically; reserve dispatch before calling Hermes; reconnect observes; explicit read retry creates a separate bounded attempt.
- **Acceptance:** Lose the accepted response then resend identical request ID; Crash between dispatch reservation and provider acknowledgement.
- **Expected:** One local dispatch per attempt; changed input rejected; uncertainty never masquerades as unsent.

## F04 · P1 · Stream ordering, terminal precedence and cursor recovery are undefined

**Release:** R1. **Evidence:** Missing contract. **Status:** Open.

- **Basis:** PLAN.md:98; PLAN.md:172; model-results.json.
- **Failure path:** Cancel confirmed -> late completion; switch view -> old delta; reconnect -> duplicate final.
- **Required amendment:** Define scoped event envelope, monotone sequence, snapshot fallback, terminal transition rules and bounded buffering. Separate stop requested from stop confirmed.
- **Acceptance:** Reorder and duplicate final frames after cancellation; Reconnect from a pruned cursor after switching conversation.
- **Expected:** No wrong-view output, duplicate final or cancelled-run resurrection; recover by snapshot without resubmission.

## F05 · P1 · UI data-fetch and action retry policies are not separated

**Release:** R1 onward. **Evidence:** Missing acceptance. **Status:** Open.

- **Basis:** PLAN.md:46; PLAN.md:174.
- **Failure path:** IPC times out after applying an action -> data library reconnect/retry resubmits operation.
- **Required amendment:** Use read observation only in retryable queries; explicit idempotent command handlers with canonical request IDs; uncertain writes only reconcile. No generic replay on reconnect.
- **Acceptance:** Time out after an action takes effect; Reconnect while a mutation response is outstanding.
- **Expected:** No automatic effect replay; observation and commands have distinct policies.

## F06 · P1 · Data schema/version and supported downgrade rules need a first-release floor

**Release:** R1. **Evidence:** Design gap. **Status:** Open.

- **Basis:** PLAN.md:162; PLAN.md:178; ACCEPTANCE.csv:R7-06.
- **Failure path:** R2 changes SQLite -> user returns to R1 -> old app silently writes new schema.
- **Required amendment:** Initialize schema/API version negotiation in R1; later migrations need exclusive ownership, recovery points and supported downgrade rules; unsupported writer refuses.
- **Acceptance:** Open a newer test schema with an older app; Interrupt the first migration before completion.
- **Expected:** No silent incompatible write or concurrent live-store copy; a defined recovery path exists.

## F07 · P1 · Untrusted Markdown and source-opening policy lacks concrete tests

**Release:** R1. **Evidence:** Missing negative tests. **Status:** Open.

- **Basis:** PLAN.md:45; PLAN.md:166.
- **Failure path:** Model/source output contains active HTML, tracking images, dangerous URI or forged local-file link.
- **Required amendment:** Specify sanitization and CSP; remote content cannot call IPC; external images require permitted loading; citation resolver uses scoped resource IDs; sender/frame and URL checks are authoritative.
- **Acceptance:** Render HTML, scripts, event handlers and tracking image URLs; Open javascript/file/data/custom-scheme links from model output.
- **Expected:** No script, unexpected network request or arbitrary OS/file operation; source grants enforced.

## F08 · P1 · Local read consent and provider disclosure consent are not the same grant

**Release:** R1/R2. **Evidence:** Design gap. **Status:** Open.

- **Basis:** PLAN.md:94; PLAN.md:108.
- **Failure path:** User selects a private document for local reading -> its contents go to a remote model without a defined disclosure policy.
- **Required amendment:** Define first-run provider disclosure and per-data-class egress; bind provider/model policy to run; attachments obey both read and disclosure permissions.
- **Acceptance:** Select a permitted file whose data class forbids remote inference; Switch provider with a sensitive queued request.
- **Expected:** No prohibited upload; user sees actual provider and compatible choices without repeated meaningless prompts.

## F09 · P1 · Forget is not closed over transcripts, caches, pending runs and restore

**Release:** R2. **Evidence:** Missing contract. **Status:** Open.

- **Basis:** PLAN.md:104; prior MEMORY-QUALITY-CONTRACT.md.
- **Failure path:** Retract/forget fact -> new context includes old transcript or restored cached source -> fact returns as current.
- **Required amendment:** Define correction/retraction versus erasure; tombstones, derived-context invalidation, pending-run handling, exports/backups and fresh-session behaviour; add an explicit forget path.
- **Acceptance:** Forget a fact while a derived reply is pending; Restore an older isolated backup after the forget event.
- **Expected:** No current-use resurrection within the declared deletion scope; retained history/backup limits are explicit.

## F10 · P1 · Concurrent review and changing context need an atomic decision contract

**Release:** R2 onward. **Evidence:** Missing acceptance. **Status:** Open.

- **Basis:** PLAN.md:170; FLOWS.md:39.
- **Failure path:** Two windows approve/reject the same proposal; editor changes content; account switches before dispatch.
- **Required amendment:** Bind exact resource/account generation, payload, version and expiry; consume approval with backend compare-and-set; pending edit invalidates old digest; final dispatch revalidates.
- **Acceptance:** Approve and reject simultaneously from two views; Edit payload or switch account after review but before dispatch.
- **Expected:** At most one accepted decision; exact original target only; no stale authority.

## F11 · P1 · Connection expiry, reconnect and disconnect lifecycle is underspecified

**Release:** R3. **Evidence:** Design gap. **Status:** Open.

- **Basis:** PLAN.md:114; GOOGLE-SETUP.md; Google OAuth reference.
- **Failure path:** Testing-mode token expires -> scheduled read fails -> UI still says connected; reconnect selects a different account.
- **Required amendment:** Separate configured/authenticated/qualified/authorized status; detect scope loss, expiration and account identity changes; disconnect revokes grants and suppresses late delivery; distinguish disable, remove credential and provider revocation.
- **Acceptance:** Expire/revoke a token while a read is active; Reconnect with a second account while proposals exist.
- **Expected:** Actionable re-consent state; no account substitution or late revoked data delivery.

## F12 · P1 · Persisted workflows cannot reuse process-local short-lived grants after restart

**Release:** R4/R5. **Evidence:** Observed integration constraint. **Status:** Open.

- **Basis:** PLAN.md:138; wayfinder/platform/google_read.py:50; wayfinder/platform/context.py:68.
- **Failure path:** Save a five-minute read grant or two-minute context ticket in a template -> scheduled run days later/restart.
- **Required amendment:** Templates bind resource intentions/versioned standing authorization, not temporary tickets; mint fresh task grants only within valid standing scope; revalidate evidence at use.
- **Acceptance:** Restart before a scheduled occurrence with old grant IDs; Run a workflow longer than its original context ticket lifetime.
- **Expected:** Expired references are not revived; fresh narrowly authorized grants/context or an explicit blocked state.

## F13 · P1 · Local task and Google task synchronization rules are absent

**Release:** R3. **Evidence:** Observed projection plus design gap. **Status:** Open.

- **Basis:** PLAN.md:118; wayfinder/platform/google_read.py:286; wayfinder/atlas/harness/base.py:39; model-results.json.
- **Failure path:** Google needsAction passes through an object documented as pending/completed, while etag/updated are omitted; later local/provider edits have no defined normalization or conflict basis.
- **Required amendment:** Define raw versus canonical task status, local/provider IDs, retained provider versions, source authority, conflict UI and complete/delete tombstones. If no sync, label an explicit import/draft.
- **Acceptance:** Edit the same mapped task in both places; Complete or delete a task while a stale page is cached.
- **Expected:** No silent overwrite, duplicate task or completed-task resurrection; conflicts remain reviewable.

## F14 · P1 · A generic receipt pattern does not qualify every external write

**Release:** R3/R7. **Evidence:** Missing provider contracts. **Status:** Open.

- **Basis:** PLAN.md:118; PLAN.md:158; FLOWS.md:39.
- **Failure path:** Provider accepts a send/event change -> acknowledgement lost -> verify using an unrelated matching item.
- **Required amendment:** Per operation define provider IDs/versions, attribution, verified/failed/unknown states and read-only reconciliation; transport success alone is insufficient.
- **Acceptance:** Lose acknowledgement after a test message or event change; Create an unrelated matching item before reconciliation.
- **Expected:** Completion is attributed to the reviewed operation; absent/unattributed remains unknown without automatic retry.

## F15 · P1 · Typed dependency outputs, version pinning and evidence expiry need exact rules

**Release:** R4. **Evidence:** Missing contract. **Status:** Open.

- **Basis:** PLAN.md:128.
- **Failure path:** Template edited during run; malformed step output feeds synthesis; old evidence silently reused.
- **Required amendment:** Freeze template/capability versions per run; schema-validate each edge; reject missing outputs/cycles; track observed-at/source versions and refresh or withhold stale context.
- **Acceptance:** Edit template and disable a binding mid-run; Return invalid output or expire context between steps.
- **Expected:** Active run is not retargeted; bad/stale output does not become trusted downstream input.

## F16 · P1 · Cancellation, queue fairness and aggregate budgets are not defined for a run tree

**Release:** R4. **Evidence:** Design gap. **Status:** Open.

- **Basis:** PLAN.md:128; PLAN.md:184; wayfinder/workers/hub.py.
- **Failure path:** Each child meets its own limit but total calls grow; background work starves chat; cancel releases capacity while upstream work continues.
- **Required amendment:** Bound total steps/calls/tokens/time/concurrency across descendants; interactive versus background queue policy; cancel propagation and retained receipts; unknown cost stays unknown.
- **Acceptance:** Start a long background run then submit chat; Cancel while two child calls are in flight.
- **Expected:** UI remains responsive; bounded queue/budgets; no child continues with newly revoked rights; cancellation limits visible.

## F17 · P1 · DST gaps/folds, overlap and missed-run policies remain choices rather than contracts

**Release:** R5. **Evidence:** Missing schedule semantics. **Status:** Open.

- **Basis:** PLAN.md:138; model-results.json:date_boundaries.
- **Failure path:** A local time occurs twice or never; laptop sleeps through several occurrences; prior run is still active.
- **Required amendment:** Store IANA zone and explicit gap/fold/fixed-versus-follow-device policy; default no overlap; bounded missed-run/coalescing; occurrence identity and clock-change handling.
- **Acceptance:** Schedule at a nonexistent or repeated local time; Sleep through multiple occurrences then resume during a running job.
- **Expected:** Documented number/timing of runs; no duplicate occurrence or unbounded backlog.

## F18 · P1 · Cron dispatch and application Quit must preserve the same authority

**Release:** R5. **Evidence:** Architecture gate. **Status:** Open.

- **Basis:** PLAN.md:138; PLAN.md:142; FLOWS.md:74.
- **Failure path:** Hermes scheduler remains alive after UI Quit or dispatches a raw prompt with inherited tools.
- **Required amendment:** Qualify a fixed trusted scheduling entry through Wayfinder; background grants explicit; Quit/stop-all semantics cover Wayfinder jobs without killing unrelated Hermes tasks. No unrestricted fallback.
- **Acceptance:** Quit with background execution disabled; Invoke a scheduled occurrence while policy/backend is unavailable.
- **Expected:** No unauthorized background effect; failures stay blocked; shared host is not indiscriminately stopped.

## F19 · P1 · Skill/plugin update and rollback can change permissions under a saved workflow

**Release:** R6. **Evidence:** Missing lifecycle tests. **Status:** Open.

- **Basis:** PLAN.md:148; WORKER-SURFACES.md:53.
- **Failure path:** Approved workflow resolves a newly installed skill/tool version; rollback is mistaken for undoing prior effects.
- **Required amendment:** Pin versions and required rights; review manifest changes; disable/revoke invalidates relevant pending authority; rollback changes future configuration only, not external history.
- **Acceptance:** Upgrade a skill to request a new tool; Rollback or disable it while a dependent proposal waits.
- **Expected:** No inherited new rights or silent version substitution; previous effects retain their receipts.

## F20 · P1 · Memory quality is not established by storage fixtures and one model run

**Release:** R2. **Evidence:** Evidence gap. **Status:** Open.

- **Basis:** PLAN.md:110; prior MEMORY-QUALITY-CONTRACT.md.
- **Failure path:** Fixture embeddings pass but paraphrased/historical/conflicting retrieval chooses wrong evidence.
- **Required amendment:** Retain explicit held-out current/history/conflict/missing cases, source fidelity and disclosure checks; qualify neural path separately from deterministic fixtures; thresholds before judging release.
- **Acceptance:** Ask a held-out paraphrase with conflicting current evidence; Ask a historical or genuinely unsupported memory question.
- **Expected:** Correct scoped evidence or explicit uncertainty; no invented current fact; report actual evaluation tier.

## F21 · P2 · Google task due dates are not timed reminders

**Release:** R3. **Evidence:** Provider semantic gap. **Status:** Open.

- **Basis:** PLAN.md:118; Google Tasks resource reference; model-results.json:date_boundaries.
- **Failure path:** Display due date via generic UTC-to-local timestamp conversion -> preceding day; promise a 10:00 task reminder the API cannot retain.
- **Required amendment:** Separate due_date, local reminder time and scheduled occurrence; preserve date-only semantics; unsupported timed behaviour is explicit.
- **Acceptance:** Read a date-only task west of UTC; Propose a timed reminder through a date-only task field.
- **Expected:** Date stays the intended calendar date; timing uses a separately qualified scheduler/calendar operation.

## F22 · P2 · Old citations may point to expired grants or changed resources

**Release:** R2. **Evidence:** Missing historical UX. **Status:** Open.

- **Basis:** PLAN.md:112; wayfinder/platform/context.py:68.
- **Failure path:** Reopen an old chat -> source grant expired or file changed -> open link silently reads the new source.
- **Required amendment:** Separate historical retained evidence from current source access; show observed version and unavailable state; request a fresh selection/grant where needed.
- **Acceptance:** Open a citation after app restart; Change a source before reopening a historical result.
- **Expected:** No unauthorized refresh or claim that changed content is the original evidence.

## F23 · P2 · Event sequence and identifier types can be rounded by JavaScript

**Release:** R1. **Evidence:** Missing wire contract. **Status:** Open.

- **Basis:** PLAN.md:172; wayfinder/api.py:wire.
- **Failure path:** A large sequence, timestamp or ID crosses JSON as Number -> duplicate/order checks compare rounded values.
- **Required amendment:** Use opaque strings and decimal-string large counters; explicit TypeScript decoding and schema tests; never turn IDs into Number for routing.
- **Acceptance:** Round-trip values around 2^53; Reconnect using a very large event cursor.
- **Expected:** Exact identity/order preserved without coercion or serialization failure.

## F24 · P2 · Attachment limits, parser truncation and temporary-copy retention need user behaviour

**Release:** R2. **Evidence:** Missing edge cases. **Status:** Open.

- **Basis:** PLAN.md:108; wayfinder/workers/files.py; wayfinder/workers/hermes_runner.py.
- **Failure path:** Oversize/unsupported/renamed/locked file appears attached; partial parsing shown as complete; remote copies outlive local grant.
- **Required amendment:** Validate selected file and disclose actual support/limits; retain source hash; show partial extraction; define temporary/sandbox copy cleanup and revoke semantics.
- **Acceptance:** Choose a locked, changed or oversized Unicode-path file; Parse a supported document with truncated output.
- **Expected:** Actionable selection error or explicit partial result; no silent format fallback or retention claim.

## F25 · P2 · A single runtime-ready label hides different dependency and cold-start failures

**Release:** R1/R2. **Evidence:** Bootstrap gap. **Status:** Open.

- **Basis:** PLAN.md:94; wayfinder/runtime.py:28; config.yaml.
- **Failure path:** Hermes is ready but FalkorDB/model cache is unavailable; first embedding download looks like a frozen app.
- **Required amendment:** Component-level health/startup states and dependency prerequisites; cold-cache/offline/disk-full paths; no automatic privileged restart/install to hide failure.
- **Acceptance:** Cold start with WSL or Docker stopped; First neural retrieval with no cached model and no network.
- **Expected:** Honest usable or blocked state; progress is accurate; other projects/services remain untouched.

## F26 · P2 · Composer focus outline overrides its own focus-visible design

**Release:** R1. **Evidence:** Observed preview defect. **Status:** Open.

- **Basis:** preview.html:8; preview-results.json:P11.
- **Failure path:** Keyboard reaches composer -> outline:none!important defeats declared focus style.
- **Required amendment:** Remove the conflicting rule or provide a clear focus-within indicator; verify in real keyboard/high-contrast tests. Do not infer screen-reader quality from the fake DOM.
- **Acceptance:** Tab from navigation into composer; Use Windows forced-colour/high-DPI settings.
- **Expected:** Visible focus and readable composer; no focus trap or clipped controls.

## F27 · P2 · Feature gating applies to navigation but not inspector or sample conversation

**Release:** R1/R2. **Evidence:** Observed preview defect. **Status:** Open.

- **Basis:** preview.html:35; preview.html:52; preview-results.json:P02-P04.
- **Failure path:** Choose R1 -> Google plan/review remain; choose R2 -> Google calendar/tasks request is shown.
- **Required amendment:** Use the same release/capability manifest for all surfaces, examples, actions and inspector tabs. Keep unavailable capabilities inaccessible except an explicitly labelled roadmap.
- **Acceptance:** R4 to R1 while Review is open; R1 to R2 chat and sources.
- **Expected:** No R3 task approval/Google data in earlier releases; appropriate phase-specific examples.

## F28 · P2 · Narrow layout hides the sidebar with no reopening path

**Release:** R1. **Evidence:** Observed preview defect. **Status:** Open.

- **Basis:** preview.html:8; preview-results.json:P08.
- **Failure path:** Below 760px -> Tasks/Memory/Workflows sidebar disappears -> rail offers no drawer opener.
- **Required amendment:** Implement accessible navigation drawer with open/close, focus and Escape; preserve route and selected context.
- **Acceptance:** Navigate on a narrow R3 window; Resize from wide to narrow with an active detail view.
- **Expected:** All enabled destinations remain reachable; no keyboard or pointer dead end.

## F29 · P2 · Wide inspector does not obey the show/hide toggle

**Release:** R1. **Evidence:** Observed preview defect. **Status:** Open.

- **Basis:** preview.html:8; preview.html:53; preview-results.json:P09.
- **Failure path:** At desktop width toggle show-inspector -> inspector stays visible because only the narrow media rule reacts.
- **Required amendment:** Use one actual visibility state for grid/sheet; update control label and aria-expanded; preserve user preference deliberately.
- **Acceptance:** Toggle inspector twice at 1920px; Cross the inspector breakpoint while hidden.
- **Expected:** Inspector opens and closes correctly at all supported widths without losing review state.

## F30 · P2 · IME Enter is treated as submit

**Release:** R1. **Evidence:** Observed preview defect. **Status:** Open.

- **Basis:** preview.html:54; preview-results.json:P06.
- **Failure path:** Confirm composed text with Enter -> handler prevents default and runs submit path.
- **Required amendment:** Ignore submit during composition (and relevant platform key composition states); keep multiline and screen-reader input intact.
- **Acceptance:** Confirm an IME composition with Enter; Use Shift+Enter and ordinary Enter after composition.
- **Expected:** Composition is not submitted; intended newline/submit behaviours remain correct.

## F31 · P2 · Optional subreleases and optional W37 lack machine-readable gate status

**Release:** R3/R7. **Evidence:** Acceptance ambiguity. **Status:** Open.

- **Basis:** PLAN.md:120; PLAN.md:180; ACCEPTANCE.csv:R3-05; ACCEPTANCE.csv:R7-05.
- **Failure path:** Read-only R3a or deferred native testing appears blocked by an unqualified write/native case.
- **Required amendment:** Add required/optional, capability precondition, release variant, justified N/A, evidence tier and owner fields; no blanket N/A for mandatory scope.
- **Acceptance:** Accept read-only R3a while Google writes remain unavailable; Accept an R7 coding subset with W37 deliberately disabled.
- **Expected:** Advertised scope is testable and honest; optional work does not fake-pass or indefinitely block unrelated accepted features.

## F32 · P2 · Web research and knowledge/notes roles have no concrete delivery slice

**Release:** R3/R4. **Evidence:** Coverage gap. **Status:** Open.

- **Basis:** WORKER-SURFACES.md:42; PLAN.md:114; PLAN.md:124.
- **Failure path:** User asks for web research or notes promised by worker coverage -> no release defines its connector and test.
- **Required amendment:** Assign a named optional read-only research/knowledge slice with actual Tavily/notes qualification, disclosure limits and source verification; or explicitly defer it in the release manifest.
- **Acceptance:** Ask for a cited online research brief; Request a note from an unconnected knowledge source.
- **Expected:** Available operation is real and sourced; unshipped capabilities are clearly unavailable.

## F33 · P2 · The full W01-W47 to concrete runtime binding catalogue is not reconciled

**Release:** R6. **Evidence:** Declared open dependency. **Status:** Open.

- **Basis:** WORKER-SURFACES.md:27; wayfinder/atlas/registry/workers.json.
- **Failure path:** User enables a numbered role -> overlapping named registry entries resolve differently or cannot resolve.
- **Required amendment:** One versioned ID/alias/contract/owner/binding inventory; every planned role mapped, deferred or unsupported; never invent a prompt to fill a missing mapping.
- **Acceptance:** Resolve each planned numbered role and legacy alias; Inspect two overlapping specialist/general roles.
- **Expected:** No duplicate worker or false Available status; missing contracts remain explicit.

## F34 · P2 · Transcript, drafts, run artifacts and logs have different deletion/storage pressure behaviour

**Release:** R1/R2. **Evidence:** Retention gap. **Status:** Open.

- **Basis:** PLAN.md:178; wayfinder/platform/evaluation.py.
- **Failure path:** Clear an artifact -> copies persist in worker jobs/transcripts; storage fills while app promises a completed save.
- **Required amendment:** Define retention and purge scope per record type, safe redacted export and disk-full handling; delete wording matches actual copies and backup limits.
- **Acceptance:** Clear chat versus workflow versus durable memory separately; Fill a disposable runtime disk during persistence.
- **Expected:** No false erasure/save; clear recovery and independent lifecycle controls.

## F35 · P2 · Quick-window position, hotkey conflicts and close/reopen recovery are untested

**Release:** R5. **Evidence:** Small interaction gap. **Status:** Open.

- **Basis:** PLAN.md:142; ACCEPTANCE.csv:R5-04.
- **Failure path:** Undock monitor or change DPI -> quick window restored offscreen; global hotkey conflicts silently.
- **Required amendment:** Clamp saved bounds to available displays, provide visible restore/reset entry, handle hotkey registration failure and document close/minimize/tray/Quit separately.
- **Acceptance:** Remove a monitor before reopening quick chat; Register an unavailable hotkey then use tray restore.
- **Expected:** Window remains recoverable; no silent hijack or uncloseable always-on-top state.

## F36 · P2 · Build/runtime version matrix is not resolved for the selected host

**Release:** R1. **Evidence:** Compatibility gate. **Status:** Open.

- **Basis:** PLAN.md:58; RESEARCH.md; upstream desktop/package.json.
- **Failure path:** Current upstream host requires newer build tooling than the installed Node; copied UI code fails before the R1 package exists.
- **Required amendment:** Record pinned host/SDK/Node/Python/Electron/API compatibility and license basis; resolve in the host spike without upgrading the active Hermes runtime by assumption.
- **Acceptance:** Build the chosen pinned host on the actual laptop; Start an incompatible API/schema/runtime version.
- **Expected:** Reproducible supported build or explicit no-go; no silent main-runtime upgrade or permissions fallback.
