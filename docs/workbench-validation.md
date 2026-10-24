# Validation record — 23 October 2026

Target: `D:\Opencode_\memory_system`. Inspected the standalone engine, configuration, graph/vector stores, ingestion adapters, retrieval/ranking/time filters, lifecycle contracts and service, shared API/journal/interpreters, context entry points and focused architecture tests. The completed Phase 1 report was saved before implementation.

## Verified results

| Check | Observed result | Scope / limitation |
| --- | --- | --- |
| Original baseline | **154 passed, 2 deselected**, 111.07 s | Existing suite; deterministic fixture embeddings and isolated real storage. |
| Final full suite | **164 passed, 3 deselected**, 119.26 s | All original selected tests plus 10 new workbench checks. Optional neural/GPU checks are excluded by default. |
| Explicit real cached-model check | **1 passed, 9 deselected**, 3.23 s | Real `BAAI/bge-small-en-v1.5`, CPUExecutionProvider, offline cache, isolated `test_` graph/temp Qdrant. Stored source read back in both backends, closed engine, opened a new engine/adapter/session, retrieved the same source ID, and recalled the exact declared value. No fixture embedder. The later added HTTP stop test was not in this earlier selection. |
| Ruff | **All checks passed** | New Python adapter/server/tests; formatted with the existing Ruff installation. |
| Browser | **Verified** | Loaded real HTML/JS/CSS, sent a retrieval-only prompt, inspected real empty-store diagnostics, switched to explicit-claim controls, refreshed inventory, checked clean shutdown, restarted server and reopened the same stores. |
| Binding | **127.0.0.1:3352 only** | Confirmed local TCP listener; FalkorDB container healthy on loopback port 6381. |
| Original architecture/configuration | **Unchanged** | SHA-256 comparison against the original copied package: all pre-existing source/config/test files match; README intentionally updated. No engine, extraction, ranking, model or schema code changes. |
| Default manual store | **0 memories, 0 entities, 0 observations after checks** | User scenarios were not auto-submitted. Isolated test graphs were cleaned by the existing test fixture; no application database was wiped. |

The empty-store browser request measured 0.036 ms for the engine search call and 10.416 ms for the adapter request. The diagnostic explicitly reports `retrieval_ran: false`: the engine short-circuited on an empty namespace. These values **are not neural retrieval latency benchmarks**. The neural check asserts genuine trace timings exist; it does not establish relevance quality or a latency target. UI/HTTP transport overhead is outside the adapter's request duration.

Focused checks cover namespace-restricted retrieval, no current-prompt leakage, source readback, correction and disputed claims, cross-namespace change rejection, confirmation requirements, immutable/idempotent source events, graph-only inventory, paginated inventory, honest failures, host/origin/session-token restrictions, no filesystem routes and clean HTTP shutdown. Deterministic embeddings only appear in isolated tests, never in the running workbench.

## Files

Created:

```text
workbench_server.py
memory/workbench.py
workbench/index.html
workbench/app.js
workbench/style.css
tests/test_workbench.py
docs/workbench-inspection.md
docs/workbench-guide.md
docs/workbench-results.csv
docs/workbench-validation.md
```

Modified: `README.md` (workbench description, startup and documentation links).

Runtime-only files created under ignored `data/`: the configured embedded Qdrant collection, workbench process metadata and console logs. The existing Compose file was used to create/start `memory-system-falkordb` and its named volume; no prior application store was imported or changed. The new standalone copy originally had no `data/` directory.

## Reproduce

Stop the running workbench with its Stop workbench button before launching another owner of its Qdrant path.

```powershell
Set-Location 'D:\Opencode_\memory_system'
docker compose up -d --pull never falkordb
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\workbench_server.py
```

Open http://127.0.0.1:3352. Use namespace `iron_web_manual`. Store source prompts with the episode operation; inspect and save evidence, start a fresh conversation, then use Retrieve only. Use explicit claims plus Recall for structured lifecycle tests, following the guide. The eight required scenarios and their exact prompts are in `workbench-guide.md` and `workbench-results.csv`.

Run checks (tests use isolated storage):

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest -q
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest tests/test_workbench.py -m neural -q
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m ruff check memory/workbench.py workbench_server.py tests/test_workbench.py
```

## Honest completion limits

Manual source ingestion, semantic retrieval, structured field recall, real-memory inspection, filtering, evidence diagnostics, fresh conversations and restart testing are available. The eight user scenarios remain **Inconclusive / not run** until manually entered and checked. No scenario is marked Pass based on expected prose.

**Conversational assistant generation and automatic general-domain claim extraction are Unsupported in this standalone package.** The workbench displays actual engine packets/receipts instead. Adding a new model or parser would exceed this validation phase. Raw natural-language corrections do not acquire authority simply by containing “correction”; the structured/manual variant exercises the existing confirmed-source contract and must be reported separately.

The direct-engine workbench does not activate the shared service's SQLite queue or three-tier context assembly. Those paths are inspected and their existing tests pass, but they are not used to fabricate a generic conversation agent. The original application's memories are not in this copy. Last-updated source timestamps and a source-level status column do not exist; UI values are labelled Unavailable, and claim statuses come from the existing lifecycle view. Inventory scanning is intended for local test volumes; large stores can be slow. Namespace isolation is a testing convention, not tenant security. No production security claim is made.
