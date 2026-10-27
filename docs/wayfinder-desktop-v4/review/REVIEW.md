# Cumulative redesign review

This log distinguishes a written requirement, an offline model/handler result and real product qualification. The last remains **Not run**. The v3 plan and stress audit are preserved byte-for-byte; current work is only in the new v4 directory.

## Batch 1 — First-release foundations

Addressed F01–F07, F23, F25 and F36: 10 findings. Defined canonical chat history, isolated tool-closed Hermes input, runtime ownership/authentication, durable request acceptance/dispatch, event/cancel semantics, observation versus command retry, migration/build floor and rendering policy. Reused existing service lock, policy/action patterns, storage and Hermes integration; no new backend/runtime was built.

Recheck: old action/chat safety models, deliberately bad controls, event orderings, integer boundaries, date examples and original source hashes. New risk review identified stale-lock takeover, lost request identity, conservative stuck reservations, false cancellation, stream pressure and unsafe rollback (N01–N06). Some implementation compatibility choices remain hard gates, not assumed working capabilities. Missing later document links were expected in intermediate snapshots and are required to resolve by batch 5.

## Batch 2 — Evidence, memory and retention

Addressed F08–F10, F20, F22, F24 and F34: 17 cumulative. Retained orchestrator-only Iron Web and existing parsers/file broker; defined read/disclosure separation, forget barrier, new-chat boundary, restore ledger and meaningful neural evaluation. Added record-class retention/quotas instead of promising universal erasure.

Recheck repeated batch 1 models/hashes. A new finite authority/context-epoch model exposes stale delivery in the deliberately permissive variant and withholds it in the guarded variant. This is not a model/provider implementation test. Checking the fix interactions found that pruning dedup rows could revive a command; C03 now uses expiring runtime-bound admission namespaces. Derived paraphrases and old backups motivated N07–N12. Accept conservative view-only old conversations after forget rather than pretend reliable automated paraphrase erasure.

## Batch 3 — Accounts and independent tasks

Addressed F11, F13, F14 and F21: 21 cumulative. R3 core now reads Google and manages separate local tasks. No implicit synchronization; status/date/version projection is explicit. Writes move to separately qualified optional R7 modules with per-operation attribution/reconciliation. Account identity is stable; connection generations fence revoked/late access.

Recheck repeated all earlier checks. The first manifest validation **failed** because the optional native feature had no explicit review-stage assignment and inherited the wrong default. Corrected the manifest to give every optional feature its real batch; rerun passed. N13–N16 cover misleading copies, identity/transport confusion, overly broad uncertain-action locks and privileged reconciliation reads. No existing task adapter was edited or declared qualified.

## Batch 4 — Bounded workflows, scheduler and role lifecycle

Addressed F12, F15–F19, F32 and F33: 29 cumulative. Initial workflows are six-step linear reads, not a DAG/runtime rewrite. Existing Hermes scheduling is required to pass the trusted-entry/time/occurrence/stop rules; no second scheduler. Initial daily policy explicitly skips missed/gap times, uses first repeated time and defaults edits effective next day. Skill rollback changes future configuration only. Research/notes/fitness are explicitly deferred. All 47 IDs will be accounted for without inventing bindings.

Recheck repeated batch 1–3 models/hashes. N17–N22 cover pinned revoked permissions, standing-grant lifetime, duplicate schedule edit/resume, shared-host Quit, upstream concurrency and misleading coding qualification. The host, OAuth, scheduler and native integrations still require actual evidence later.

## Batch 5 — Interaction, acceptance and cross-contract review

The original five preview defects were corrected in a new offline preview: release-wide gating, reachable navigation drawer, actual desktop inspector toggle, IME-safe Enter and visible focus. The first 28 targeted checks passed in its finite graph traversal.

Expanding focus checks then found **two new failures**: a dialog trigger removed by rendering had no live focus fallback, and rebuilt inspector buttons lost logical selected-button focus. The failed evidence is preserved in [preview-before-focus-fix.json](preview-before-focus-fix.json). Corrected the prototype handlers and C22; the next targeted run passed all 31 checks. N27 records the regression so it is not lost after the fix.

A separate cross-contract pass found N28: using a connection generation in an unknown-effect lock could allow repetition after reconnecting the same provider account. C13 now binds duplicate risk to stable provider identity, with conservative resource/operation-family locking and an explicit privacy tradeoff if semantic evidence is deleted. A new finite comparison model checks this case; it is not provider exactly-once evidence.

A final authority/UX check found N29: calling an inline button trusted does not make an approval IPC proof of human intent when the conversation renderer is untrusted. C06 now requires a main-owned bounded confirmation and service proposal reload; larger optional effects need a qualified isolated review surface. This is a design requirement and future negative test, not a native interaction performed here.

The final full traversal and cumulative artifact/model result are recorded in [preview-results.json](preview-results.json) and [batch-5.json](batch-5.json). Refer to those generated results for executed counts. All 36 original findings have a specific amendment; all 29 second-order entries have a proposed containment/regression; application acceptance stays unrun.

| Final review evidence | Result | Limit |
|---|---|---|
| Preview BFS and DFS | 1,404 states / 35,316 transitions; same reachable graph | Finite handler/navigation state, not a rendered app |
| Targeted preview checks | 31 pass / zero fail after the two added focus failures were corrected | Includes static CSS observations; real focus/IME/layout untested |
| Earlier action/chat and event-order models | Repeated at every numbered checkpoint; deliberately permissive controls still expose violations | Assumptions/bounds inherited from v3, not existing backend behaviour |
| New authority/context-epoch model | 23-state negative control exposes stale delivery; 18-state guarded model has no encoded violation | One input and one revision/account change |
| New uncertain-effect-lock model | 7-state negative control exposes reconnect replay; 4-state guarded model has no encoded violation | One stable account/resource/family, no provider proof |
| Original artifacts | 23 v3 files unchanged against recorded hashes | Only enumerated original files; not an audit of unrelated concurrent work |
| Acceptance design | 148 unique cases, all Not run; feature/variant/release references validated | No actual application/provider/native acceptance yet |
| Worker coverage | W01–W47 accounted for as supplied or unresolved mappings | Bindings unverified; no workers recreated |

Final preview evidence records the exact HTML/script/manifest hashes. The cumulative checker refuses to reuse it after those inputs change. The final checkpoint also records plan/contract/flow/manifest/acceptance/risk hashes so later amendments can trigger a deliberate recheck.

## Reproduce, without running an app

From the repository root, with the existing Python environment:

    & 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -B .\docs\wayfinder-desktop-v4\review\build_preview.py
    & 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -B .\docs\wayfinder-desktop-v4\review\build_cases.py
    node .\docs\wayfinder-desktop-v4\review\check_preview.cjs
    & 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -B .\docs\wayfinder-desktop-v4\review\review.py --batch 5

The final review command repeats old safety controls, new epoch/uncertainty models, historical-file hashes, acyclic/cumulative release dependencies, exact finding references, 47 worker IDs, case feature/variant applicability, all-Not-run statuses and resolved document links. Scripts write only this design directory. Intermediate batch JSON files retain the actual checks/scope available at each checkpoint; later checks were not retroactively claimed at earlier checkpoints.

## Limits and open qualification gates

No full app exists here. Fake DOM tests cannot establish browser layout, native focus/IME/screen-reader behaviour, Electron isolation, runtime durability or account/native effects. Finite models assume their bounded state variables and do not prove provider idempotency, SDK retry behaviour, lock atomicity or OS security. Negative controls show these models detect the defects they encode, not that all possible failures are encoded.

Before each release, actual installed-version compatibility, required wire schemas, persisted-state fault tests, packaged UX and appropriate live evidence remain required under C23. There is no claim of no loose ends in all possible implementations; the redesign converts known ambiguities into explicit choices, tests, exclusions and honest no-go gates.
