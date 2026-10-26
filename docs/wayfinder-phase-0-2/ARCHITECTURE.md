# Implemented boundary and reuse decision

`Main window + quick window → authenticated loopback API → application service → existing Iron Web MemoryEngine → coordinated FalkorDB + Qdrant storage`

Both native views belong to one process and share a selected space/conversation. The service is a thread in that process, owns its embedded store once, and listens on an ephemeral `127.0.0.1` port. Its random bearer capability is process-local and rotates on launch. There is no token bootstrap endpoint. Browser-origin requests are denied. Every memory handler checks the credential-bound orchestrator role and owner/space relationship before reading records; IDs alone grant no access. Other Windows processes running as the same user are not an OS isolation boundary. Worker filesystem/network isolation remains phase 5.

The model is not the enforcement layer. Workers have no default credentials. Tests issued actual authenticated HTTP requests as a worker, another owner and an unknown token: access failed before inspection. Main memory has no unauthenticated read route in the new API. The older separate workbench API has not been upgraded into this boundary or connected to workers.

## Memory authority

Retain the current engine's coordinated graph/vector authority and its compensating rollback behavior. SQLite owns UI state, ownership, approvals, immutable request digests, receipts and deletion tombstones. It is not a second store from which fact answers are generated. Replacing this engine with journal-replay authority is a separate migration decision, not part of these phases.

Only explicit approved structured claims enter long-term memory. Source origin and actor are assigned by the trusted service. API input cannot supply authority metadata, owner identity or arbitrary claim scopes. Corrections require target claims from the exact owner/space/task/subject/field and a reason. Global aliases/reference creation is unavailable. Current/historical/conflict decisions come from the retained engine lifecycle.

## Versioned generic scope

New explicit operations use `wayfinder_memory_v2`:

```json
{
  "contract": "wayfinder_memory_v2",
  "owner_id": "credential-bound owner",
  "memory_space_id": "registered owned space",
  "task_id": "general or an explicit task identity"
}
```

Recall uses exact scope matching. Existing travel-specific `ContextRequest` / `trip_id` and workbench contracts remain compatible and unchanged. They are not relabeled as a generic runtime. The new API does not yet invoke legacy travel cards or claim to provide model-budgeted three-tier context. Model context assembly belongs to its later integration. This decision permits generic explicit facts now without silently reinterpreting historical records.

## Consent, durability and revisions

Proposals bind a normalized immutable payload, owned space and current engine revision. Approval accepts only the proposal ID and boolean decision, never an edited execution payload. Writes have deterministic source identities derived from owner, space and request. A same-ID changed payload fails; repeated or simultaneous approvals return one effect. Unconfirmed results stay `applying`, without success receipts. Retry reconciles a source committed before a receipt interruption. An uncommitted stale approval cannot execute after other memory changes.

The UI captures the original space when dispatching and discards callbacks after a space switch. Reads provide bounded-lifetime, opaque context proofs bound to owner, space and graph revision. Mid-read changes fail. Writes/deletion invalidate cached proofs; the UI revalidates displayed recall on health polling. Any graph change invalidates proofs conservatively across spaces. These proofs are not reusable worker grants.

Delete intent is durably tombstoned before store deletion, invalidates proofs and blocks affected reads while deletion recovery is pending. Completion checks source and claim removal. Completed source proposals are redacted after forgetting. Tombstones survive restart and participate in the tested restore procedure. Original backups and independent transcript retention need their own controls.

JSON transport serializes INT64 values beyond JavaScript's exact integer range as decimal strings. The native UI has no hosted model or external tool route in these phases. Credentials are not displayed in settings or logged with prompts.

## Effective inventory, 2026-10-24

| Component | Observed version / state | Reuse in this build |
|---|---|---|
| Python | 3.12.14, existing environment | Yes |
| Tcl/Tk | 8.6.12 | Native desktop widgets |
| FalkorDB image | v4.20.7; live service healthy, restart count 0 after recovery | Existing engine; separate new app graph |
| Python FalkorDB client | 1.7.1 | Yes |
| Qdrant client | 1.18.0 | Embedded vectors in separate runtime |
| Redis Python client | 8.1.0 | Engine leases/revisions |
| FastEmbed / ONNX Runtime | 0.8.0 / 1.19.2 | Local BGE embeddings |
| Pydantic | 2.13.5 | Strict schema validation |
| Docker engine | 28.3.3 | Live DB and disposable tests |
| NemoClaw / NemoHermes | 0.0.137 | Installed separately; app adapter deferred |
| OpenShell | 0.0.116; sandbox `ai-assistant` Ready | App worker isolation deferred |
| Hermes Agent | 0.21.3; CLI status reports running | App integration deferred |
| NVIDIA Lightning | Configured in installed Hermes runtime | No inference calls by this app |
| NVIDIA Ultra | Previously catalog-verified, not exercised here | Deferred to phase 4 |
| Tavily / daily-life connectors | No routes enabled in this app | Deferred |

The installed Hermes status does not independently prove model inference or tools in this new app. This implementation did not invoke NVIDIA models. The existing upstream CLI dependency findings and FalkorDB persistence limitation recorded in `ops/SETUP.md` remain unresolved upstream risks; this build does not claim to fix those packages.
