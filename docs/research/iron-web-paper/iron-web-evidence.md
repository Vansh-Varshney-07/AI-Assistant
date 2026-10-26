# Iron Web implementation evidence

Read-only inspection on 24 October 2026. Application behavior was not newly tested in this task. Paths below refer to this repository snapshot, and should be pinned to a commit/content hash when preparing a reproducible submission.

## Architecture found in code

| Capability | Evidence | Qualification for the paper |
|---|---|---|
| Dual graph/vector memory | `memory/engine.py`, `memory/graph/falkordb_store.py`, `memory/vector_store/qdrant_store.py`, `README.md` | FalkorDB and embedded Qdrant are the stores; SQLite supplies receipts/replay, not a complete factual authority |
| Raw memory text plus structured claims | `MemoryRecord` in `memory/models.py`; `SourceInput` and `ClaimInput` in `memory/lifecycle/models.py` | Preserved text and claims are distinct representations; corpus fidelity still depends on ingestion |
| Explicit authority | `SourceInput.authority()` and `support_group()` | User confirmation is restricted to a declared user-origin source; the local API trusts the caller's provenance |
| Claim operations | `ClaimInput`, `memory/lifecycle/service.py` | Assert, confirm, correct, supersede, alias and retract have explicit contracts; not arbitrary semantic truth verification |
| Temporal/history handling | `MemoryLifecycle.active`, `views`, `recall`; `memory/temporal/filter.py` | Validity and known-time fields exist; natural-language temporal interpretation remains an extraction concern |
| Dispute-aware exact recall | `MemoryLifecycle.recall()` | Returns supported, disputed, unconfirmed, missing and historical states; semantic similarity alone does not establish an answer |
| Retrieval pipeline | `memory/retrieval/hybrid.py` | Vector candidates, bounded graph expansion, temporal filtering, lifecycle reconciliation, optional reranking and scoring |
| Ranking formula | `memory/ranking/scorer.py` | Weighted semantic/reranker score, graph signal, recency, importance, entity overlap, historical signal, contradiction penalty and reliability adjustment |
| Fuzzy memory score | `memory/lifecycle/fuzzy.py` | Zero-order Sugeno controller for freshness, source quality, support and agreement; explicitly not a calibrated probability |
| Context tiers | `memory/context/runtime.py`, `memory/context/contracts.py`, `memory/cache/` | Bounded hot context and selected cards over durable evidence; depends on the consuming tokenizer and policy |
| Dependent-work checks | `register_work`, `complete_work`, `invalidate_work`, `handoff` in `memory/lifecycle/service.py` | Checks evidence eligibility and changed dependencies; requires workflow-level evaluation |
| Cross-store operations | `memory/storage.py`, `memory/shared/journal.py` | Coordinated graph operations, vector snapshots/compensation and receipts; no single crash-atomic transaction across the stores |
| Isolation and API | `memory/spaces.py`, `memory/shared/service.py`, `docs/api.md` | Local space IDs are scopes; do not equate them with authentication |

## Effective default configuration inspected

`config.yaml` selects CPU operation, no hosted extraction, `BAAI/bge-small-en-v1.5` embeddings, 384-dimensional vectors, up to 100 vector candidates, two graph hops, a maximum of 50 graph nodes and disabled reranking. `BAAI/bge-reranker-base` is configured but not enabled by that default. The scoring weights are 1.0 semantic, 0.5 graph, 0.3 recency, 0.2 importance, 0.4 entity, 0.2 historical and 0.5 contradiction penalty.

These are inspected settings, not tuned scientific findings. Service factories and environment overrides can change effective settings; save resolved settings for every experiment. Source quality and independent-group values are inputs to a heuristic, not measured truth probabilities.

The context schema still requires `trip_id` and supports flight/hotel/itinerary task types. It needs an explicit domain contract or adapter for general conversational benchmarks. The cache stores context payloads and retrieval representations; this is not a generative model's KV cache. Future companion/orchestrator plans must be separated from the implemented core.

## Earlier validation records available

| Record | What it reports | What it does not establish |
|---|---|---|
| `docs/validation.md` | 154 passing focused tests, two deselections; CRUD, lifecycle, rollback, replay, snapshot/restore | Neural relevance quality or public benchmark QA; embeddings were deterministic fixtures |
| `docs/nemotron-validation/nemotron-summary.md` | 187 automated tests and 18/18 small live checks across two named models; nine checks per model | A representative population accuracy or comparison with Mem0/Zep |
| `docs/memory-spaces-test-report.md` | 204 automated tests, three deselections, 21/21 live space checks | A current test run or production security certification |

These counts describe successive historical runs and must not be added together as independent benchmark questions. The live scenarios include deliberately chosen storage/retrieval, correction, conflict, restart, supersession and replay behaviors. Their small denominators and repair history matter. Existing failed/pre-repair artifacts are also retained elsewhere in `docs/`.

The Nemotron report records median extraction times of 1,709 ms and 4,776 ms, median answer generation of 908 ms and 6,544 ms, and median query totals of 2,130 ms and 9,601 ms for Lightning and Ultra respectively. These are component observations from a small historical run, not general latency estimates and not directly comparable with a literature p95.

## Evidence missing before a results section can be written

- A frozen benchmark adapter that ingests the public dataset without answer-derived annotations.
- LoCoMo and LongMemEval QA and retrieval runs for Iron Web, with per-question artifacts.
- Pinned baseline implementations, equivalent answer models and matched context budgets.
- An evaluated contribution beyond established graph/vector and temporal memory patterns.
- Ablations showing the value of lifecycle, source grouping, graph expansion, fuzzy scoring and context caching.
- Measured end-to-end cost, latency, failure rates and uncertainty.

No new result is implied by this inventory. It identifies what can be described in an implementation section and what remains experimental work.
