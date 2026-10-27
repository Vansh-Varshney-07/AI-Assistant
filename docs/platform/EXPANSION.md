# Platform expansion — 26 October 2026

This increment extends the working read-only and controlled local Git slices. It preserves existing worker prompts and task/result contracts, all local work, and the terminal-only constraint. No account data, desktop windows, clipboard, screen capture, message dispatch or project push was used.

## Reuse and inspection

The installed managed Hermes runtime was inspected again: **0.21.3**, **99 registered tools**, compatible SDK, and **zero effective tools** in the isolated probe. Delegation, cron, MCP and the existing reader modules are present; this does not qualify their optional connections. Private inspection evidence is `.local/verification/expansion-prerequisites.json`.

New code uses the existing `AppService`/Iron Web event APIs, `ActionGate`, SQLite application state, file broker, `TaskItem` provider representation, installed `google-auth` **2.62.0**, Python CSV reader and IANA timezone support. No agent loop, memory engine, document parser, general scheduler or desktop driver was replaced. New integration exists only to bind these components to scopes, review, provider resources, evidence and recovery.

## Scoped memory changes and maintenance

`wayfinder/platform/memory_control.py` exposes the existing assertion, correction, supersession and retraction events through exact approvals. This is a bounded maintenance operation that preserves history; it does not expose store-wide decay, deduplication, consolidation or deletion under a task-scoped grant.

All endpoints require the authenticated orchestrator, owned `space` and explicit `task`:

| Endpoint | Additional fields | Behavior |
|---|---|---|
| `platform_memory_preview` | `body` | Existing proposal validation with no memory or proposal-store mutation. Returns the exact normalized body and revision. |
| `platform_memory_propose` | `body`, `request_id` | Immutable pending plan; body task must match, at most eight explicit target claims. No fact is published. |
| `platform_memory_decide` | `id`, `digest`, `approve` | Exact approval/rejection. Approval binds owner/space/task, full payload and 120-second lifetime. |
| `platform_memory_revoke` | `id` | Revoke pending approval. |
| `platform_memory_result` | `id` | Scoped status and independently verified receipt or uncertainty. |
| `platform_memory_reconcile` | `id` | Read-only inspection of an uncertain event; no replay. |
| `platform_memory_audit` | `id` | Latest 100 scoped audit events. |

`body` is the existing `MemoryProposal` interface. For correction, supersession or retraction, the caller must name matching target claims and give a reason. The existing recall/`platform_context` API supplies conflict evidence and uncertainty; no new conflict detector chooses a winning fact.

The driver revalidates the original proposal, scope and memory revision, then uses the existing coordinated Iron Web publication. An additive trusted callback checks expiry immediately before storage dispatch. Platform-managed proposals cannot be approved through the legacy `decide` endpoint. Verification reads both stores and checks the proposal digest, exact scoped field and value. Retractions are verified against Iron Web's existing `__retracted__.<field>` history event, including original target IDs and reason. A receipt proves that the event was published; it is not a promise that the field will remain current indefinitely.

Lost acknowledgements stay `outcome_unknown`; repeated approval cannot redispatch. Reconciliation checks the original event identity and payload. Restart expires pending actions and preserves uncertain actions. An absent or unverified event does not authorize a retry. Retraction is not a purge of historical records.

## Workflow recovery, evaluation and telemetry

`wayfinder/platform/evaluation.py` adds these interfaces around the existing controller:

| Endpoint | Additional fields | Behavior |
|---|---|---|
| `platform_read_retry` | `id`, `request_id`, `reference` | Explicit retry of an unsuccessful read-only workflow. One child per original attempt, no chained retries. Rechecks current runtime, context and file grant. |
| `platform_workflow_evaluate` | `id`, `request` | Persist a versioned rubric against a completed artifact hash. Optional literal phrases and expected file hash, plus bounded-output/provenance checks. |
| `platform_workflow_metrics` | optional `limit` 1–100 | Scoped recent status counts, worker dispatch count, median/max observed terminal latency. |
| `platform_read_clear` | `id` | Remove a terminal workflow's body/context/result and evaluations. Keep identity/digest tombstones and audit metadata to prevent replay. |

Evaluation requests use `EvaluationRequest`; reusing an evaluation ID with a changed rubric/artifact is rejected. Evaluation is a deterministic artifact check, **not a factual-accuracy judge**. `semantic_accuracy`, model token usage and monetary cost remain unknown when unsupported. A historical artifact is never fresh authorization for an action.

Retries are never automatic and never apply to Git, memory or desktop effects. They use `PlatformService.start` and existing WorkerHub execution, not a new scheduler. The original question/context query are retained; the orchestrator supplies an explicitly selected file reference. Ordinary new workflow requests remain subject to the existing two-active-workflow limit.

Artifact clearing is deliberately limited: associated WorkerHub job artifacts, Iron Web facts, prior backups and transcripts have their own retention. It is not a global erasure claim. Cleared request tombstones survive restart and cannot dispatch again under the same request ID.

## W26 local activity data connection

`platform_activity_read(space, task, reference)` uses a file previously selected through existing `worker_grant` and `worker_search` APIs. `activity.py` reads **wayfinder.activity.csv/1** using the standard CSV library, with these exact ordered columns:

```text
provider,record_id,revision,metric,value,unit,start_time,end_time,timezone
```

The exported `ActivityRecord` schema and existing synthetic `docs/personal-ai-companion/manual-test-kit/fitness-provider-a.csv` are development fixtures. Supported source metrics are steps/count and workout_duration/minute. The read is limited to 366 records and the existing 2 MiB broker limit. It rejects non-finite/negative values, fractional step counts, wrong units, invalid intervals, offset/timezone mismatches and repeated provider record identities. It checks the source hash and grant again before delivery.

Overlapping intervals withhold the affected total. Different providers stay separate because cross-provider equivalence is unproven. Missing periods remain unknown, never zero. Results include source/hash provenance and perform no memory write or health inference. This qualifies the local CSV interface, not a named fitness vendor's live API or its export conversion.

## Google read adapters — account qualification pending

`google_read.py` reuses installed `google-auth` authorized sessions and the existing `scripts/auth_google.py` connection convention. It provides fixed **GET-only** routes for Calendar events, Google Tasks and Gmail message references. It does not fetch Gmail bodies or send messages.

| Endpoint | Additional fields | Behavior |
|---|---|---|
| `platform_google_status` | none | Credential-file presence and supported read operations; never tokens or private file contents. Presence is not live qualification. |
| `platform_google_grant` | `service`, `resource`, optional `limit`; Calendar also `time_min`, `time_max` | Five-minute exact calendar/task-list/Gmail-label grant in the caller's task. Calendar window at most 31 days; read limit 1–50. |
| `platform_google_read` | `grant` | One bounded provider page with whitelisted fields and explicit truncation. |
| `platform_google_revoke` | `grant` | Revoke future reads and suppress delivery of an in-flight revoked response. |

Provider routes and parameters follow the primary references: [Calendar events.list](https://developers.google.com/workspace/calendar/api/v3/reference/events/list), [Tasks tasks.list](https://developers.google.com/workspace/tasks/reference/rest/v1/tasks/list), and [Gmail messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list). The existing `TaskItem` representation is reused for task results; other worker-owned contracts remain unchanged.

The host owns credential loading, and the configured Google connection is bound to the runtime's authenticated owner. Callers cannot supply paths, tokens, HTTP methods or URLs. Credential loading checks existing OAuth scopes without relabelling a token with broader scopes. The private connection fingerprint is bound to the grant; changing the credential file requires a fresh grant. Redirects and environment proxy overrides are refused in both the provider session and the inspected SDK's separate OAuth refresh session. Responses are capped at 128,000 bytes, one page and bounded fields; requests have five-second socket/refresh timeouts and an additional stream-time guard. Provider exception text is sanitized. Credentials and raw responses are not logged or written to the repository.

No Google account was read during development. HTTP tests use an explicit fixture session; credential-loader tests use synthetic token data and prohibit network access. `live_qualified` remains false until a separate account test is authorized and passes. Neither Atlas metadata nor a passing fixture transport proves account connectivity.

Optional runtime dependencies are listed in `requirements/platform.txt`. After the user selected Google Calendar/Tasks and Gmail, the missing OAuth helper was installed under ignored `.local/google-oauth` using `requirements/google-connect.txt`. The [Google setup handoff](GOOGLE-SETUP.md) documents the narrowed consent flow, local checks and exact human steps. The shared Python environment was not changed.

## Human input needed for real accounts

1. Provider selection is complete: the user chose **Google Calendar/Tasks and Gmail**, with fitness later.
2. For Google, choose an OAuth desktop client/project with the required APIs enabled and place its downloaded configuration at private `secrets/credentials.json`. Complete account consent locally using the existing setup. The missing OAuth helper can be installed as part of setup; the account consent is the human step. The resulting private `secrets/token.json` is never to be pasted into chat or committed.
3. Select the exact calendar, task list or Gmail label, and a small read-only qualification case. New write scopes and explicit action approval are required for future account writes. Message recipients and content must be reviewed before dispatch.
4. Choose a fitness source or a local export to map to the canonical activity format. Synthetic fixtures do not qualify real health data access.
5. Re-enable native desktop testing explicitly only when ready to revisit W37. It remains disconnected; no old uncertain desktop attempt is replayed.

Hosted GitHub writes and broader coding operations are still not qualified; the existing local Git branch transaction remains the proven operation. Arbitrary multi-worker dependency graphs still require qualification through existing Hermes delegation and actual worker configurations. No replacement scheduler or permissive delegation fallback has been introduced. Real provider usage/cost accounting requires usage evidence from the existing Hermes/provider route.

## Verification

Run `ops/Test-Platform.ps1`. Tests use real disposable FalkorDB and embedded Qdrant with deterministic fixture embeddings, real Git in synthetic repositories, real scoped CSV files, and explicitly mocked Google HTTP. Model inference is mocked in this suite; `-Live` selects the separate existing installed-Hermes read-only test. Native UI stays excluded.

Final regression result: **139 passed, one live-Hermes test skipped, one UI test deselected**, in 206.32 seconds (`.local/verification/platform.xml`). After the final OAuth-session and owner-binding hardening, the focused source suite passed **29 tests** in 28.75 seconds (`platform-sources.xml`). A fresh live installed-Hermes synthetic read passed separately: **one passed, 140 deselected**, in 33.10 seconds (`platform-live.xml` and `platform-live.json`), with 18.891 seconds inside the workflow and one worker invocation. These counts overlap by tier and must not be added as unique tests.

All **12 exported schemas** match their implementations. Ruff and tracked diff whitespace checks passed. The original repository HEAD remains `4913ee9` on `codex/platform-integration`; work remains local and uncommitted. No project push, native desktop action or live Google/account read was performed. The live Hermes result qualifies the synthetic reasoning path, not Google connections or W37.
