# Iron Web memory spaces

Implemented in `D:\Opencode_\memory_system`. The running workbench is at http://127.0.0.1:3352/.

## Use it

1. Enter a test name and click **New isolated space**. It creates a new empty space with an automatically generated ID.
2. Select a model and run your prompts. All writes, searches, field recall, corrections, source records and model evidence use the selected space.
3. Start another test by creating another space. Use the **Active memory space** selector to return to an earlier one.
4. **Fresh conversation** starts another conversation inside the same space. It preserves that space's long-term memories.

The interface currently has **My next experiment** selected, ID `space_c41c297b8c33486696f73ad137c30a3f`. It is empty. Existing validation namespaces remain individually selectable, with their original IDs and records.

Changing models within a space deliberately shares that space's memories. Choose different spaces when you want independent model experiments.

## What each ID means

| ID | Purpose | Lifetime |
|---|---|---|
| `memory_space_id` | Independent pool of source records and claims | Persists across conversations and server restarts |
| `session_id` | Conversation identifier within a space | New conversation gets a new ID |
| `request_id` | Immutable operation identity and replay protection | Reuse only for the same original request |
| `memory_id` | Individual source record | Stable after storage |

A space determines the pool to read and write. The existing engine still stores its memories in FalkorDB and Qdrant, using their graph and semantic roles. This is logical isolation inside the configured stores.

## API contract

Create a space using the current local workbench session token from `GET /api/session`:

```http
POST /api/spaces
Content-Type: application/json
X-Workbench-Token: <current token>

{"name":"Research experiment","memory_space_id":"research_test_a"}
```

`memory_space_id` is optional on creation; the server generates one when omitted. Names may repeat; IDs may not. IDs are case-sensitive, 1–40 ASCII letters, digits, underscores or hyphens. Names contain 1–100 characters.

```http
GET /api/spaces
GET /api/memories?memory_space_id=research_test_a
```

Send prompts to `POST /api/prompt` with `memory_space_id`, `session_id`, `request_id`, `mode` and `prompt`. Use fresh UUIDs for session and request IDs, plus the existing model/claim/recall parameters as needed. Explicit space IDs must already exist. The old `namespace` spelling remains compatible with local validation scripts; it identifies the same scope. Conflicting spellings are rejected. Unscoped inventory requests are rejected.

The backend maps the space onto the existing `test_namespace` claim scope, preserving old records without rewriting them. It stores the canonical space ID in new source metadata. Request-derived memory IDs include the space, so identical request IDs in two spaces remain independent. Old receipt replay remains supported.

## Storage and startup

The new SQLite directory at `data/memory_spaces.sqlite3` holds only space IDs, names and creation times, including empty spaces. Actual memory content remains in the existing graph/vector stores. Include the directory in cold backups alongside those stores. The shared service's separate journal is unchanged.

```powershell
Set-Location 'D:\Opencode_\memory_system'
docker compose up -d --pull never falkordb
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\workbench_server.py --nvidia --key-file 'D:\Opencode_\reserchpaper\.env'
```

Stop an existing workbench cleanly before starting another process against embedded Qdrant. Without `--nvidia`, the interface works in evidence-only mode. Keys remain in the original existing environment file and are never returned by the API.

## Verification and reproduction

Final Python regression suite: **204 passed, 3 optional tests deselected**. The new memory-space module contributes **17 passing boundary tests** against real isolated FalkorDB graphs and temporary Qdrant stores, with deterministic test embeddings. Python lint and JavaScript syntax checks passed.

Live verification: **21/21 passed** using real BGE embeddings, the actual workbench HTTP API, both requested NVIDIA models and a real clean server restart. Exact prompts, IDs, responses, claims, retrieval diagnostics and check results are in `memory-spaces-live-evidence.json`. The first background launch produced connection errors; that failed attempt is retained separately in `memory-spaces-first-launch-failure.json`. The final passing run used the documented PowerShell server launch.

Run the architecture tests:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest -q
```

With the server running and Nemotron enabled, create fresh retained test spaces and run the model checks:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_memory_spaces.py
```

Then use **Stop workbench**, restart with the command above, and verify persistence of that same run:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_memory_spaces.py --verify-restart
```

This test creates separate A/B spaces for each model, writes contradictory test codes under the same subject/field, deliberately reuses a request ID across spaces, queries from new sessions, and checks source citations and exclusion of the other code. It also checks empty spaces, rejected unscoped inspection, and restart persistence. It retains all generated source records. Repeated full runs create fresh IDs; save a report before replacing it with a later run.

## Continuing toward multiple users

Concurrent request tests verify separation inside one workbench server. Storage operations still use the existing engine locks, and one process owns embedded Qdrant. This does not establish distributed scaling or independent device synchronization.

Space IDs are not credentials. Before online access, bind each space to an authenticated account, authorize every lookup/write/list operation, and map device and project membership on the server. Keep `user_id`, `device_id`, `memory_space_id` and `session_id` distinct. The local directory currently lists all local space names; it must become an authorized per-user list in an online service. Direct engine access remains administrative, and the existing shared service retains its separate tenant/authentication contract.

Changed files: `memory/spaces.py`, `memory/workbench.py`, `workbench_server.py`, `workbench/app.js`, `workbench/index.html`, the workbench tests, and the live validation runners. Core retrieval, lifecycle and storage algorithms are unchanged. Pre-change files are saved under `data/space_backup_20261023`; the reviewable diff is `memory-spaces.patch`.
