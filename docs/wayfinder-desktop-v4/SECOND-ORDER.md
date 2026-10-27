# Problems a fix could introduce

Each entry states a new dependency caused by an amendment, its containment, and the regression that must remain in later batches. These are design resolutions, not evidence that the runtime implements them.

| ID | Introduced by | New failure path | Containment | Regression |
|---|---|---|---|---|
| N01 | One runtime owner | Stale heartbeat causes lock stealing and two writers | C02 uses process identity plus existing safe lock recovery; timeout alone never steals | Double launch, crashed owner, alive but unresponsive owner |
| N02 | Durable request dedup | Host crash loses request ID and creates another attempt | C03 journals identity before send; recover by that ID; journal never claims canonical history | Crash before send, after commit, before acknowledgement |
| N03 | Conservative no replay | A reserved but never-sent request stays stuck indefinitely | Mark interrupted/unconfirmed; explicit new bounded read attempt, visible possible prior cost; effects use C13 | Reserve/crash, stop/restart, explicit retry |
| N04 | Strict cancellation | UI says cancelled although external effect or upstream cost still occurs | C04 separates delivery, upstream status and C13 effect outcome; retain accounting | Cancel before/after dispatch, final races, deadline |
| N05 | Typed stream/snapshots | Slow window exhausts memory or snapshot mixes spaces | C04 bounded buffers, scoped snapshots and unsubscribe; generation/attempt routing | Gap, duplicate, huge frame, two spaces/windows |
| N06 | Required schema check/backup | Old app corrupts newer store or rollback restores forgotten data | C05 refuses unsupported schema; isolated supported restore plus C09 deletion policy | Old writer, disk-full migration, missing deletion ledger |

| N07 | Forget invalidates derived text | A remembered fact survives as an untracked paraphrase in chat | C09 puts all pre-barrier chats in the affected space into historical view-only inference mode; fresh conversation, epoch checks and purge barriers | Forget while queued/running, historical reopen, fresh recall |
| N08 | Storage retention/compaction | A pruned request ID is accepted as a new command | C03 service-issued admission namespaces expire and cannot create after runtime restart; C21 preserves minimal unknown-effect markers | Prune dedup rows, resend old ID, clock rollback, restart |
| N09 | Backup recovery | Restoring an old backup bypasses current deletion | C09 latest verified deletion ledger required before activation; otherwise quarantine/refuse | Missing/corrupt ledger, backup before forget |
| N10 | Bounded document artifacts | Cleanup removes citation evidence while UI still promises a source | C08 distinguishes retained excerpt from temporary artifact/current file; C21 lists their retention separately | Reopen expired artifact, changed file, retained excerpt deletion |
| N11 | Strict disclosure policy | A provider switch silently uploads an already-selected private file | C01 freezes binding; C08 rechecks egress before dispatch and rejects incompatible queued data | Provider change before/after acceptance |
| N12 | Privacy versus action audit | Erasing payload makes outcome attribution impossible | C21 honors content deletion and retains explicit uncertainty/minimal non-content identity; C13 no replay | Delete chat while an action is unknown |

| N13 | Independent local tasks | A one-time copy looks synchronized and user assumes a checkbox changed Google | C12 separate provider/local identities, explicit copy label, no writeback and no sync badges | Edit/delete copied local task then refresh provider |
| N14 | Account generations | Normal network outage accidentally invalidates all authority or replacement leaks old data | C11 distinguish transport health from identity/scope change; epoch on real replace/disconnect/revoke | Offline/reconnect same account versus different account |
| N15 | No-replay uncertain actions | A generic duplicate lock blocks every unrelated action forever | C13 operation-specific lock; unrelated permitted work proceeds; initial UI cannot risk-repeat | Unknown A, permitted unrelated B, alternate-ID replay A |
| N16 | Reconciliation reads | A Checking button becomes a new privileged account access path | C13 requires fresh read-only grant, account binding and attribution; no write fallback | Disconnect/expire access before checking unknown effect |

| N17 | Pinning workflow/skill versions | A pinned version keeps using permissions revoked after the run started | C14/C18 pin identity but revalidate policy before each step; disabling blocks the next step | Edit version plus revoke permission mid-run |
| N18 | Standing schedule authorization | A long-lived schedule becomes an unbounded permanent grant | C17 scope, 30-day maximum, fresh occurrence grants and aggregate admission; no schedule writes | Restart, expired authority, disabled account, changed resource |
| N19 | Stable occurrence identity | Editing/resuming or DST creates another same-day occurrence | C16 fixed UTC identity, next-day edit default, first-fold/skip-gap, no catch-up | Duplicate callback, backward clock, edit before/after occurrence |
| N20 | Background Quit | Shared Hermes continues dispatching after the UI claims stopped | C17 durable app admission fence and trusted callback route; mode unavailable until qualified | Quit, crash before fence acknowledgement, stale shared callback |
| N21 | Foreground priority | Preempting background work releases a slot while upstream is still running | C15 no silent preemption, retained slot/accounting and visible bounded queue | Chat during slow brief, stop request before upstream abort |
| N22 | Narrow R7/read-only scope | UI wording implies existing branch qualification covers arbitrary coding | C20 explicit per-operation inventory and required read qualification; no generic terminal | Unsafe Git config/helper, foreign path, missing read adapter |

| N23 | Quick window shares state | Two views submit one draft as two different commands | C19 composing lease/version plus C03 one canonical request and per-conversation admission | Main/quick submit race, close and take over draft |
| N24 | Responsive drawer/inspector fixes | Two modals trap focus or hide the only navigation control | C22 one overlay, native preview dialog, Escape/focus restore and explicit responsive transition | Drawer to inspector, resize open sheet, keyboard Escape |
| N25 | Optional capability variants | Required broken functionality is silently relabelled N/A | C23 frozen advertised set, mandatory absence/denial checks and real tier when enabled | Core R3 without writes; advertised native variant without driver |
| N26 | Central manifest | Client stale manifest hides a button but API still admits an unavailable operation | C22 service-side operation inclusion/qualification/auth checks on every admission | Old renderer, direct unsupported intent, disabled binding |

| N27 | Rerendered accessible controls | Inspector tabs or the original dialog trigger are replaced, losing keyboard focus | C22 explicit selected-control focus plus a live opener fallback; two failing handler checks were reproduced and corrected in the offline prototype | Rebuild active detail button; detach opener then Escape |

| N28 | Connection-generation fencing and payload erasure | Reconnecting the same provider account bypasses an unknown-effect lock, or erased semantic evidence secretly remains | C13 locks use stable provider account identity across generations; after semantic-key deletion widen to resource/operation family with explicit restricted-state UX | Unknown effect → reconnect same account → repeat; delete payload then same-family create |

| N29 | Renderer treated as untrusted plus inline approval UX | A forged approval IPC is mistaken for a real user approving the exact action | C06 inline review requests main-owned bounded confirmation; only trusted callback can decide; large payload requires qualified isolated review surface | Forge approval intent/confirmation flag, stale dialog, changed payload while review open |

All 29 entries have a proposed containment and acceptance regression. They remain implementation obligations. N27 was observed in the new offline prototype; N28/N29 were found by reviewing the interaction of proposed fixes. No claim is made that a finite redesign eliminates every possible new failure.
