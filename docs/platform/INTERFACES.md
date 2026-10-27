# Platform interfaces: wayfinder.platform/1

Status: platform implementation and synthetic fixtures available. On 26 October the user instructed us to proceed without waiting for the other developer's branch or agreement. Existing interfaces remain the compatibility baseline; no worker task/result definition or worker prompt is changed. Later configurations can use an explicit adapter when supplied, without blocking independent platform work.

The existing loopback `/v2/` API and bearer authentication are reused. Every platform endpoint requires an authenticated **orchestrator**, a space owned by that identity, and an explicit task. Owner identity comes from authentication, never request data. Worker/model outputs cannot mint context/file grants or approvals. The [platform expansion](EXPANSION.md) documents the additional memory, evaluation/recovery, activity CSV and read-only Google interfaces and their qualification limits.

## Context, capabilities and workflow binding

All calls below use the existing Python `wayfinder.api.Client.call` helper, with common `space` and `task` fields.

| Operation | Additional fields | Behavior |
|---|---|---|
| `platform_inspect` | none | Read installed Hermes package/SDK/registry evidence and run the existing isolation probe; no inference, optional dependency probes, or desktop actions. |
| `platform_capabilities` | `query` | Existing Atlas keyword retrieval, intersected with qualified handlers. Every discovery row has `executable: false`; final handlers still authorize access. |
| `platform_context` | `query: {subject, predicate}` | Reuse orchestrator-only scoped Iron Web recall; return bounded evidence, provenance, warnings, revision and an opaque context reference. |
| `platform_validate_context` | `context_ref` | Validate owner/space/task, lifetime, and existing Iron Web freshness proof. |
| `platform_read_start` | `request` | Start the fixed read-only recipe below. |
| `platform_read_result` | `id` | Advance completed worker output through validation, or return the stored workflow artifact. |
| `platform_read_cancel` | `id` | Forward cancellation to the existing worker lifecycle and prevent result delivery. |
| `platform_audit` | `id` | Return the latest 100 scoped transitions, with sequence numbers. |

Platform-owned JSON Schemas are in [contracts/](contracts/). `Scope.owner` is internal. `ContextPacket` is for the orchestrator; W35 receives only the selected field's values/status, claim/source references and warnings. It receives no bearer token, freshness proof, context reference, owner/space ID, memory client, or direct storage handle.

The initial binding is **Atlas `wayfinder.files.analyze` → existing `/v2/worker_start` role `W35`**. Its schema version identifies the actual application API (`wayfinder.api/v2`), not a claimed upstream Hermes tool schema. Registered Hermes tool IDs and their actual schema hashes are separately listed by the runtime inspector. Registered tools are labelled `registered_not_probed`, not available or enabled in this worker.

Example request, after explicitly granting and discovering a synthetic input file through existing `worker_grant` / `worker_search` routes:

```json
{
  "contract": "wayfinder.platform/1",
  "request_id": "synthetic-read-001",
  "question": "Compare the selected release note with the supplied retention memory.",
  "reference": "OPAQUE_FILE_REFERENCE_FROM_THIS_TASK",
  "context": {"subject": "me", "predicate": "retention_days"},
  "deadline_seconds": 110
}
```

The controller stores this fixed plan: capability selection → scoped context → existing W35 job → validation → synthesis response. The synthesis is the validated worker text packaged with provenance, not a second agent or extra model call. The existing W35 implementation and installed Hermes own inference.

Worker configurations can exercise this binding against `FixtureWorker` in `tests/test_platform_integration.py` and the generated schemas. This fixture is explicitly mocked and does not prove live Hermes behavior. Existing worker task/result definitions remain unchanged; later configurations can use an explicit adapter. Unknown roles and tools have no dispatch binding.

## Enforcement and limits

- Context: one exact subject/field in the authenticated task, at most eight evidence rows and 2,600 serialized bytes; tickets expire in 120 seconds. Conflicts and missing/unconfirmed fields remain explicit. Oversized evidence fails rather than silently selecting a value.
- Runtime evidence: installed SDK signatures and schema hashes plus the existing zero-tools/no-memory probe, cached for five minutes. No default-profile tool or connector is claimed qualified from module presence. Expiry or refreshed fingerprints invalidate pending completion.
- Workflows: at most two active workflows; one worker invocation per workflow; deadline 5–110 seconds; existing WorkerHub/Hermes iteration/output/time limits remain in force. A deadline timer only cancels that existing job; it is not a replacement task or cron scheduler.
- Request identity: immutable payload digest within owner/space/task. Concurrent duplicate submissions return the same attempt; changed payload under the same ID is rejected. This proves local dispatch deduplication, not exactly-once external effects.
- Delivery: validate memory freshness, current file hash, grant validity, runtime fingerprint and bounded isolated worker output. No stale result is published as a new completion. Returned completed records are historical artifacts stamped with `verified_at`; they do not grant authority for later actions.
- Restart/close: pending work is interrupted, timers stop, existing workers receive cancellation, and no automatic redispatch occurs. Deadline, failure, cancellation, interruption, validation and completion are persisted with audit transitions.
- Persistence: workflow inputs, bounded context snapshots, results and audits live in the existing private application SQLite store. They are not a second semantic memory store. No new memory write is performed by this read-only recipe. `platform_read_clear` removes a terminal platform artifact and its evaluations while keeping deduplication/audit metadata. It does not erase WorkerHub artifacts, Iron Web facts, transcripts or backups.
- Metrics: elapsed time and worker invocation count are recorded. Model token usage and monetary cost are `null` because the current bridge does not report them. Source checks do not prove factual answer quality; task-level evaluators remain necessary.

## Action interface

`ActionBinding` is a versioned reference to the existing `ActionGate` digest, lifetime and action reference. The gate supports trusted `DesktopPlan`, `GitPlan` and `MemoryPlan` bindings in three separate whitelisted stores. `ActionBinding.backend` accepts `desktop_action_gate`, `git_branch_gate` and `memory_event_gate`. The existing desktop routes remain unchanged. The [bounded Git connector](CONTROLLED-GIT.md) and [memory integration](EXPANSION.md) supply their own scoped entry points; no arbitrary-operation execution endpoint was added.

The existing `DesktopPlan` schema is exported unchanged alongside the platform schemas. Treat action outcomes as verified receipts or explicit uncertainty. A workflow result or Atlas candidate cannot approve an action. W37 remains disconnected and unqualified, with native testing disabled.

## Remaining dependencies

Optional worker-configuration binding; real-account qualification of prepared Google read adapters; external calendar/task/message writes and hosted-GitHub operations; fitness-vendor source mapping beyond the qualified local CSV format; broader workflow dependencies through Hermes delegation; provider token/cost reporting; qualified W37 host integration. Scoped memory previews/change events, one explicit read-only retry, artifact checks, telemetry and terminal artifact clearing are implemented in the expansion. Store-wide memory maintenance is not exposed under task-level authority.
