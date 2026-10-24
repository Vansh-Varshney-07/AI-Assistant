# Standalone inspection — 23 October 2026

Inspection completed before implementation. Target: `D:\Opencode_\memory_system`, the standalone copy requested in this chat. The parent `reserchpaper` application is not the target and has unrelated local changes.

## Actual execution paths

- `memory/__init__.py` exports `MemoryEngine`; `memory/engine.py` aliases it to `LegacyMemoryEngine`, the current dual-store implementation. `add()` validates input, computes the configured embedding, optionally extracts entities, and writes Qdrant payload/vector plus FalkorDB observations/entities/relations inside `storage.coordinated_write`. Graph staging/publication and vector compensation are used; this is not a crash-atomic cross-database transaction.
- Without explicit claims, extraction policy `none` preserves text as a source record; it does not interpret arbitrary natural-language corrections. With `claims` and `source_info`, `lifecycle.prepare/ingest` stores immutable MemorySource and MemoryClaim evidence. Accepted corrections/supersession/retraction require a confirmed user source and a reason. Single-valued contradictory assertions can remain disputed. Versioned source records cannot be overwritten with `update()`.
- `search()` defaults to hybrid retrieval: embedding, Qdrant candidates, bounded graph expansion, time filtering, lifecycle reconciliation, optional reranking, weighted scoring. Results contain stable IDs and `retrieval_trace`, including stage timings and lifecycle decisions. `recall()` returns structured field evidence and an answer status (supported, disputed, missing, etc.); it requires a subject and usually an explicit predicate for this domain. It does not generate prose answers.
- `shared_server.py` is an authenticated JSON service built on Python's standard HTTP server. `/v1/events` journals receipts in SQLite, then workers ingest through the same engine; `/v1/search`, `/v1/recall`, history and context are available. Its factory uses validated defaults and environment overrides, rather than loading all of `config.yaml`. Optional interpreters include travel-specific parsing and hosted extraction, neither configured in this copy. The three-tier context API requires profiles and the consuming model's tokenizer and retains travel-specific task contracts. No generic chat agent or generation model exists here.

## Configured versus observed

| Component | Configuration / observed local state |
| --- | --- |
| FalkorDB | `127.0.0.1:6381`, graph `memory_core`; Compose image `falkordb/falkordb:v4.20.7`, volume `memory_system_falkordb_data`. Initially not running. Existing unrelated container is on 6380; do not reuse it. Image is already cached locally. |
| Qdrant | Embedded, 384-dimensional cosine collection `semantic_memory`, absolute resolution of `./data/qdrant` relative to standalone config. No standalone data directory existed at inspection; this copy did not contain original databases. |
| SQLite | Shared service receipt/notification journal only; not an alternative semantic memory backend. No shared-service runtime/config exists in the standalone copy. Embedded Qdrant also has its own implementation files. |
| Embeddings | `BAAI/bge-small-en-v1.5`, CPU by default, lazy FastEmbed/ONNX initialization. Cached BGE model directory exists in the user's temporary FastEmbed cache; actual inference still requires verification. |
| Reranker | Model name exists in YAML, but `retrieval.reranker_enabled: false`; not active. |
| Extraction | `extraction_policy: none`; no automatic general-domain claim extraction. NIM settings exist but are dormant. |
| Runtime | Existing Python 3.12 virtual environment at `D:\Opencode_\reserchpaper\.venv` has pytest, FastEmbed, Qdrant, FalkorDB, PyYAML and Pydantic. Reuse it. |
| Overrides | No relevant `FALKORDB_*`, `USE_GPU`, `HF_HOME`, `FASTEMBED_CACHE_PATH`, or `HF_HUB_OFFLINE` overrides observed in the inspected shell. Credentials are not copied or displayed. |

## Existing startup and safest inspection

From `D:\Opencode_\memory_system`, run `docker compose up -d --pull never falkordb`, then use the existing Python virtual environment. Direct engine startup is `MemoryEngine(config='config.yaml')`. The shared API additionally needs a private service configuration/tokenizer setup described in README and docs/api.md; it is unnecessary for this direct-engine workbench.

Use `vector_store.scroll(with_vectors=False)`, public `get()`, `inspect_claim()` and fixed parameterized graph queries under the same engine locks. Keep inventory separate from `search()` results. Include graph-only source IDs in inventory and identify missing copies. Claim status is computed by the existing lifecycle view from stored evidence; it is not a source-record status column. Memory-level last-updated timestamps are absent. The workbench must display these distinctions and Unavailable values. Do not expose arbitrary Cypher, database edits, filesystem access or shell execution.

## Gaps and smallest appropriate implementation

No HTML UI, general prompt orchestration, generative assistant, automatic general-domain claim extraction, or inventory endpoint exists. Add a local stdlib HTTP workbench over the public engine, a read-only inventory adapter, and explicit manual store/search/structured-claim controls. Return genuine engine evidence/receipts; label conversational response generation unsupported. Do not add a model, prompt parser, or correction algorithm to force the eight scenarios to pass.

Use a named test namespace in source metadata and typed claim scope, retaining the configured persistent stores. Only submitted manual prompts may create records; startup and browsing add no sample memories. Namespace isolation is a testing convention, not tenant security. Conversation history stays in the browser and is never fed into retrieval. Offline model loading and loopback-only storage/server checks keep this workbench local.

## Validation plan

Run the existing suite against its own temporary Qdrant paths and owned `test_` graphs, first as a baseline and again after changes. Add adapter/API tests for truthful traces, namespace boundaries, partial failures, immutable claims, cross-origin rejection and restart persistence. Keep fixture-model checks separate from a real cached-model smoke check. Leave all user scenarios unrun/inconclusive until manually submitted; no expected answer alone constitutes a pass.
