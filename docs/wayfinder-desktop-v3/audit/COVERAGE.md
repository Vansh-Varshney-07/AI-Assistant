# Breadth, depth and boundary coverage

This file distinguishes reviewed paths from executed model/preview checks. No app/provider/native acceptance row is marked passed by this audit.

## BFS: subsystem sweep

| Area reviewed | Finding references |
|---|---|
| Host choice and build/runtime compatibility | F01, F02, F36 |
| Packaging, startup and degraded dependencies | F02, F06, F25 |
| Chat transcript/session authority | F01, F03 |
| Submission, dispatch, lost acknowledgement and replay | F03, F05 |
| Streaming, reconnect, view switching and cancellation | F04, F16, F23 |
| IPC/authentication and untrusted rich content | F02, F07 |
| Provider/model disclosure and attachment egress | F08, F24 |
| Memory current/history/conflict quality | F09, F20 |
| Forget, caches, transcripts, exports and restores | F09, F22, F34 |
| File selection, limits, parser output and citations | F22, F24 |
| Exact review, expiry and concurrent decisions | F10, F14 |
| Google OAuth and account lifecycle | F11, F12 |
| Local and remote task models/synchronization | F13, F21 |
| Provider writes and reconciliation | F14 |
| Workflow templates, typed edges and pinned versions | F12, F15 |
| Work queues, aggregate limits and cancellation | F16 |
| Schedule time semantics and occurrence identities | F17 |
| Scheduler routing, background permissions and Quit | F18 |
| Skills, plugins, workers and configuration versions | F19, F33 |
| Release/feature availability and scope completeness | F27, F31, F32 |
| Keyboard, IME, inspector and responsive navigation | F26, F28, F29, F30, F35 |
| Data/schema lifecycle and operational retention | F06, F34 |

The preview's finite graph independently enumerates release selection, visible navigation, design flows, inspector tabs and its toggle state. BFS and iterative DFS reach the same 366 states/7,620 transitions. It is deliberately not a graph of implemented backend features.

## DFS: end-to-end path review

| Journey | Branches followed | Required outcome / references |
|---|---|---|
| First launch | Healthy; WSL/Docker absent; cold model cache; disk full | Truthful prerequisites/recovery and no false ready/save state; F02/F25/F34 |
| Existing instance | Same root; wrong/stale endpoint; second launch; incompatible version | Authenticate/attach one owner or refuse safely; F02/F06 |
| Chat submit | Accepted; timeout before/after commit; lost response; restart | Same canonical attempt observed, not repeated; F03/F05 |
| Chat receive | Ordered; duplicate; gap; stale cursor; prior conversation | Snapshot/dedup/scoped delivery; F04/F23 |
| Stop | Before dispatch; after dispatch; provider cannot cancel; late final | Honest stop requested/confirmed; no resurrected output; F04/F16 |
| Remember/change | Approve; reject; edit; expire; revoke; concurrent decision | Exact authoritative event or no effect; F09/F10 |
| Grounded answer | Correct fact; conflict; missing fact; changed source; expired proof | Correct evidence or uncertainty/withheld result; F15/F20/F22 |
| Forget | Pending reply; old transcript; cached card; old backup | Declared deletion/invalidation scope retained; F09/F34 |
| Attach | Supported; unsupported; too big; locked; replaced/link; partial parsing | Respect existing broker plus truthful UI/retention; F08/F24 |
| OAuth | Missing client; consent denied/partial; token expiry; account changed | No fake connected state or substituted authority; F11 |
| Account disable/remove | No active job; in-flight read; pending write; scheduled occurrence | Revoke/suppress delivery and prevent future dispatch appropriately; F11/F12/F18 |
| Task/calendar view | Empty; truncated; all-day; date-only due; timezone conversion | Explicit coverage and correct date/time types; F13/F21 |
| Task changes | Local only; mapped provider item; concurrent edit; completion/delete | Stable identity and reviewable conflicts; F13/F14 |
| Write result | Verified; rejected; expired; lost ack; unrelated matching result | Attributed receipt or uncertainty, never ordinary write replay; F10/F14 |
| Workflow | Valid DAG; cycle; invalid output; edited version; disabled binding | Frozen valid plan and scoped typed outputs; F15/F19 |
| Workflow interruption | One child done; another fails; cancel; timeout; resource exhaustion | Partial receipts retained with bounded descendants; F16 |
| Scheduled occurrence | On time; sleep; gap/fold; clock change; previous run active | Explicit occurrence/missed-run/overlap policy; F17 |
| Pause/stop/Quit | Before dispatch; during effect; app-owned versus shared service | No claimed undo or unrelated process termination; F02/F18 |
| Skill update | Reject; publish; new rights; revoke; rollback | No hidden rights/version substitution; prior effects unchanged; F19 |
| Sources and links | Trusted source ref; changed grant; raw URI; tracking image | No arbitrary file/process/network bridge; F07/F22 |
| Main/quick views | Simultaneous review; different visible spaces; old notification | Immutable original scope and recoverable window; F04/F10/F35 |
| Upgrade/restore | Success; interrupted migration; unsupported downgrade; deletion ledger | One owner and supported schema/recovery path; F06/F09 |
| Responsive/keyboard | Narrow navigation; wide inspector; IME; focus; DPI/monitor change | Reachable controls and predictable focus/input; F26–F30/F35 |
| Release acceptance | Mandatory blocked case; read-only variant; W37 deferred | Explicit capability/required/optional/justified-N/A criteria; F31 |
| Full feature coverage | Web/notes worker; missing numbered role; overlapping alias | Qualified named slice or explicit deferred/unsupported state; F32/F33 |

These 25 reviewed journeys include success/failure/cancellation/restart/revocation branches where relevant. They are review coverage, not executed E2E tests.

## Combinations and boundary cases

The generated matrix crosses five entry points, four lifecycle states, four authority states, three operation classes, four evidence conditions and four input classes: **3,840 combinations**. [All combinations](designed-scenarios.csv) remain Not run. Unsupported combinations are denial cases, not a promise that every entry point supports every operation.

A greedy pairwise selection chooses [24 scenarios](pairwise-scenarios.csv) covering all **239 distinct two-factor pairs**. This is useful implementation smoke coverage; it does not replace higher-order race cases or the original/supplemental acceptance suite.

Executed model boundaries include old/new account selection, monotone expiry/revoke, changed payload, uncertain acknowledgement, duplicate dispatch/final, current-view mismatch, cancellation, two effects and explicit independent verification. All five finite state graphs have matching BFS/DFS reachable sets. 288 abstract race orders are checked against both permissive and guarded variants.

The existing backend's pure `wire()` function was executed via its extracted function AST on nine nested boundary inputs, without importing/starting a backend. Its large-integer conversion passes. This is evidence that a useful backend guard already exists, not proof that the new TypeScript/event layer preserves it.

The actual extracted Google task-read projection was also exercised with a synthetic response and fake session. It preserves raw `needsAction`, rather than converting to the generic model's documented pending label, and omits provider etag/updated from the presentation object. This is a normalization/versioning decision for F13, not a live-provider failure or evidence that a not-yet-built task UI currently loses tasks.

Real timezone arithmetic reproduces DST gap/fold and date-only display hazards. Actual cron leases, system clock changes, power cycles, quota/rate limiting, network partitions, provider partial writes, memory pressure and disk faults still require appropriate implementation tests in disposable/test-account environments.
