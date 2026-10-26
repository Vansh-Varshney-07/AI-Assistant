# Finding-by-finding redesign

Every amendment is a proposed requirement. Implementation remains unverified. The original v3 finding and its evidence remain preserved; use the contract and acceptance references below rather than treating this ledger as a production pass.

## F01 — Canonical chat history and authority are not contracted

Batch 1 · Addressed in proposed contract · [Contract C01](CONTRACTS.md)

Application-canonical bounded history; tool-closed isolated Hermes binding; frozen provider policy.

Recheck: F01-T1;F01-T2; second-order risks N05;N11 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F02 — Runtime attach, authentication and ownership handshake is incomplete

Batch 1 · Addressed in proposed contract · [Contract C02](CONTRACTS.md)

Authenticated stable-root runtime ownership; safe lock recovery; owned/shared lifecycle and component health.

Recheck: F02-T1;F02-T2; second-order risks N01;N20 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F03 — Crash-safe chat acceptance and dispatch are only an intention

Batch 1 · Addressed in proposed contract · [Contract C03](CONTRACTS.md)

Host request journal before send; atomic acceptance; durable reservation; explicit new read attempt only.

Recheck: F03-T1;F03-T2; second-order risks N02;N03;N08 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F04 — Stream ordering, terminal precedence and cursor recovery are undefined

Batch 1 · Addressed in proposed contract · [Contract C04](CONTRACTS.md)

Scoped string-ID sequenced events; snapshots/bounded buffers; terminal CAS and truthful upstream cancellation.

Recheck: F04-T1;F04-T2; second-order risks N04;N05 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F05 — UI data-fetch and action retry policies are not separated

Batch 1 · Addressed in proposed contract · [Contract C03](CONTRACTS.md)

Observation-only retries; command identity cannot be refreshed automatically; unknown effects never ordinary retry.

Recheck: F05-T1;F05-T2; second-order risks N02;N03;N15 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F06 — Data schema/version and supported downgrade rules need a first-release floor

Batch 1 · Addressed in proposed contract · [Contract C05](CONTRACTS.md)

API/schema negotiation, exclusive supported migration and isolated compatible restore start with R1.

Recheck: F06-T1;F06-T2; second-order risks N06;N09 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F07 — Untrusted Markdown and source-opening policy lacks concrete tests

Batch 1 · Addressed in proposed contract · [Contract C07](CONTRACTS.md)

Concrete content/IPC/source-opening deny policy, size limits and negative acceptance.

Recheck: F07-T1;F07-T2; second-order risks N24;N26 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F08 — Local read consent and provider disclosure consent are not the same grant

Batch 2 · Addressed in proposed contract · [Contract C08](CONTRACTS.md)

Freeze provider binding and require both local read and permitted outbound disclosure.

Recheck: F08-T1;F08-T2; second-order risks N11 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F09 — Forget is not closed over transcripts, caches, pending runs and restore

Batch 2 · Addressed in proposed contract · [Contract C09](CONTRACTS.md)

Durable forget barrier, context epoch, pre-barrier chats view-only, purge verification and latest-ledger restore gate.

Recheck: F09-T1;F09-T2; second-order risks N07;N09;N12 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F10 — Concurrent review and changing context need an atomic decision contract

Batch 2 · Addressed in proposed contract · [Contract C06](CONTRACTS.md)

Trusted immutable proposal, atomic competing decision and final scope/version/account checks.

Recheck: F10-T1;F10-T2; second-order risks N04;N14;N17;N29 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F11 — Connection expiry, reconnect and disconnect lifecycle is underspecified

Batch 3 · Addressed in proposed contract · [Contract C11](CONTRACTS.md)

Separate connection/qualification/authority health; immutable account identity and generations; bounded read retry.

Recheck: F11-T1;F11-T2; second-order risks N14;N28 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F12 — Persisted workflows cannot reuse process-local short-lived grants after restart

Batch 4 · Addressed in proposed contract · [Contract C15](CONTRACTS.md)

Templates store intentions; manual/standing authority issues fresh short-lived step references within limits.

Recheck: F12-T1;F12-T2; second-order risks N18;N19 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F13 — Local task and Google task synchronization rules are absent

Batch 3 · Addressed in proposed contract · [Contract C12](CONTRACTS.md)

Local/provider task independence; raw/canonical status and versions; explicit one-time copy; two-way sync deferred.

Recheck: F13-T1;F13-T2; second-order risks N13 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F14 — A generic receipt pattern does not qualify every external write

Batch 3 · Addressed in proposed contract · [Contract C13](CONTRACTS.md)

Provider writes moved to optional R7 modules; per-operation receipts/attribution/reconciliation and conservative stable-account duplicate locks.

Recheck: F14-T1;F14-T2; second-order risks N12;N15;N16;N28 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F15 — Typed dependency outputs, version pinning and evidence expiry need exact rules

Batch 4 · Addressed in proposed contract · [Contract C14](CONTRACTS.md)

Linear maximum-six-step read recipes; pinned versions, typed edges, required inputs and five-minute freshness.

Recheck: F15-T1;F15-T2; second-order risks N17;N18 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F16 — Cancellation, queue fairness and aggregate budgets are not defined for a run tree

Batch 4 · Addressed in proposed contract · [Contract C15](CONTRACTS.md)

Root budgets include all children/retries; bounded queues, foreground priority and retained uncertain accounting.

Recheck: F16-T1;F16-T2; second-order risks N04;N21 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F17 — DST gaps/folds, overlap and missed-run policies remain choices rather than contracts

Batch 4 · Addressed in proposed contract · [Contract C16](CONTRACTS.md)

Daily fixed IANA-zone only; skip gaps/missed, first fold, no overlap/catch-up; unique intended-UTC admission.

Recheck: F17-T1;F17-T2; second-order risks N19 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F18 — Cron dispatch and application Quit must preserve the same authority

Batch 4 · Addressed in proposed contract · [Contract C17](CONTRACTS.md)

Existing scheduler must enter trusted adapter and pass durable app Quit fence; otherwise feature unavailable.

Recheck: F18-T1;F18-T2; second-order risks N18;N20 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F19 — Skill/plugin update and rollback can change permissions under a saved workflow

Batch 4 · Addressed in proposed contract · [Contract C18](CONTRACTS.md)

Reviewed immutable skill/binding versions and effective rights; pinned execution plus live revocation; rollback future-only.

Recheck: F19-T1;F19-T2; second-order risks N17;N26 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F20 — Memory quality is not established by storage fixtures and one model run

Batch 2 · Addressed in proposed contract · [Contract C10](CONTRACTS.md)

Retain hard memory invariants; proposed preregistered 40-case held-out neural suite with at least 38 correct and zero boundary failures.

Recheck: F20-T1;F20-T2; second-order risks N07;N11 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F21 — Google task due dates are not timed reminders

Batch 3 · Addressed in proposed contract · [Contract C12](CONTRACTS.md)

Date-only task semantics remain dates; timed reminders not promised by a task field.

Recheck: F21-T1;F21-T2; second-order risks N13;N19 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F22 — Old citations may point to expired grants or changed resources

Batch 2 · Addressed in proposed contract · [Contract C08](CONTRACTS.md)

Historical retained excerpt differs from temporary artifact and fresh current-source access.

Recheck: F22-T1;F22-T2; second-order risks N10 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F23 — Event sequence and identifier types can be rounded by JavaScript

Batch 1 · Addressed in proposed contract · [Contract C04](CONTRACTS.md)

Opaque IDs/decimal-string counters with existing wire regression and future decoder qualification.

Recheck: F23-T1;F23-T2; second-order risks N05 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F24 — Attachment limits, parser truncation and temporary-copy retention need user behaviour

Batch 2 · Addressed in proposed contract · [Contract C08](CONTRACTS.md)

Qualified UTF-8 text/Markdown first; byte/extraction limits, target/hash checks, partial indicators and tracked cleanup.

Recheck: F24-T1;F24-T2; second-order risks N10;N11 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F25 — A single runtime-ready label hides different dependency and cold-start failures

Batch 1 · Addressed in proposed contract · [Contract C02](CONTRACTS.md)

Component-specific prerequisites and degraded states; no silent empty-root fallback or privileged dependency repair.

Recheck: F25-T1;F25-T2; second-order risks N01;N06 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F26 — Composer focus outline overrides its own focus-visible design

Batch 5 · Addressed in proposed contract · [Contract C22](CONTRACTS.md)

Prototype conflicting outline removed; visible and forced-colour focus rules; rendered verification still required.

Recheck: F26-T1;F26-T2; second-order risks N24;N27 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F27 — Feature gating applies to navigation but not inspector or sample conversation

Batch 5 · Addressed in proposed contract · [Contract C22](CONTRACTS.md)

One generated manifest governs routes, samples, inspector and attachments; direct unsupported intents denied.

Recheck: F27-T1;F27-T2; second-order risks N25;N26 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F28 — Narrow layout hides the sidebar with no reopening path

Batch 5 · Addressed in proposed contract · [Contract C22](CONTRACTS.md)

Prototype native navigation dialog with real open/close/Escape and live focus fallback.

Recheck: F28-T1;F28-T2; second-order risks N24;N27 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F29 — Wide inspector does not obey the show/hide toggle

Batch 5 · Addressed in proposed contract · [Contract C22](CONTRACTS.md)

Prototype actual wide visibility plus narrow dialog and synchronized aria-expanded/labels.

Recheck: F29-T1;F29-T2; second-order risks N24;N27 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F30 — IME Enter is treated as submit

Batch 5 · Addressed in proposed contract · [Contract C22](CONTRACTS.md)

Prototype composition latch/event/key229 guards; normal Enter and Shift+Enter remain distinct.

Recheck: F30-T1;F30-T2; second-order risks N27 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F31 — Optional subreleases and optional W37 lack machine-readable gate status

Batch 5 · Addressed in proposed contract · [Contract C23](CONTRACTS.md)

Explicit feature variants, required-when-advertised cases, exclusion reasons and mandatory omitted-capability denial.

Recheck: F31-T1;F31-T2; second-order risks N25;N26 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F32 — Web research and knowledge/notes roles have no concrete delivery slice

Batch 4 · Addressed in proposed contract · [Contract C20](CONTRACTS.md)

Live web research and external notes explicitly deferred; no misleading model-only substitute.

Recheck: F32-T1;F32-T2; second-order risks N25;N26 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F33 — The full W01-W47 to concrete runtime binding catalogue is not reconciled

Batch 4 · Addressed in proposed contract · [Contract C20](CONTRACTS.md)

All 47 IDs inventoried; unresolved bindings remain unavailable until developer reconciliation; no invented prompts.

Recheck: F33-T1;F33-T2; second-order risks N17;N26 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F34 — Transcript, drafts, run artifacts and logs have different deletion/storage pressure behaviour

Batch 2 · Addressed in proposed contract · [Contract C21](CONTRACTS.md)

Record-class retention, pending privacy barriers, quotas and truthful disk-full state; expired command namespaces prevent pruned replay.

Recheck: F34-T1;F34-T2; second-order risks N02;N08;N09;N12 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F35 — Quick-window position, hotkey conflicts and close/reopen recovery are untested

Batch 5 · Addressed in proposed contract · [Contract C19](CONTRACTS.md)

Quick view shares broker/draft lease; clamped bounds, hotkey conflict, tray restore and private notification rules.

Recheck: F35-T1;F35-T2; second-order risks N23;N24;N27 in [risk register](SECOND-ORDER.md). All app cases remain Not run.

## F36 — Build/runtime version matrix is not resolved for the selected host

Batch 1 · Addressed in proposed contract · [Contract C05](CONTRACTS.md)

Pinned host/build/runtime/license matrix and no-go gates before implementation; no automatic runtime upgrade.

Recheck: F36-T1;F36-T2; second-order risks N06;N22 in [risk register](SECOND-ORDER.md). All app cases remain Not run.
