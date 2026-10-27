# Local benchmark installation

The [27 October first-fixes report](first-fixes-20261027.md) documents the new
DMR conversation-scoped runner, reviewed-evidence policy, and configurable
top-10/1,800-token reader replay. The installation notes and historical score
artifacts below retain their original scope.

Installed and checked on 26 October 2026. This is an isolated CPU setup for Iron Web. The application implementation and its default `config.yaml` have not been changed.

## What is ready

| Item | Installed content / verification |
|---|---|
| Python | Separate `.local/benchmarks/.venv`; project-pinned CPU dependencies; `pip check` passes |
| LoCoMo | Official `locomo10.json`: 10 histories, 1,986 QA entries, all five categories retained |
| LongMemEval cleaned | Complete oracle, S and M files: 500 questions each; these are three conditions on the benchmark, not 1,500 independent questions |
| Embeddings | `BAAI/bge-small-en-v1.5`, 384 dimensions, real ONNX weights loaded offline |
| Reranking | `BAAI/bge-reranker-base`, real ONNX weights loaded offline; CPU execution verified |
| Iron Web integration | A two-document synthetic smoke check passed through actual hybrid retrieval with non-null cross-encoder scores |
| Input adapter | `scripts/benchmark_data.py` streams LongMemEval and exposes text-only LoCoMo histories, questions and separate gold annotations |

Downloads, model caches, pinned upstream revisions, SHA-256 hashes, package lock, generated configuration, and local reports live under `.local/benchmarks/`, which is already Git-ignored. The approximately 4.2 GB of data/model downloads are not added to Git. No private credentials are copied into this environment.

Primary sources: [LoCoMo](https://github.com/snap-research/locomo), [LongMemEval](https://github.com/xiaowu0162/LongMemEval), [cleaned dataset](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned), [BGE reranker](https://huggingface.co/BAAI/bge-reranker-base). Exact installed revisions are in `.local/benchmarks/revisions.json`; file hashes and download URLs are in `download-manifest.json`. LoCoMo's retained license is CC BY-NC 4.0; the LongMemEval code license is MIT. License notices/model cards remain with the downloaded sources.

## Checks and commands

Run PowerShell from the project root:

```powershell
# Fast adapter checks; no model, provider, or database access.
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/test_benchmark_adapter.py -v

# Validate all dataset records and load both neural models entirely offline.
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/check_benchmarks.py

# Also exercise actual Iron Web using two synthetic raw episodes.
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/check_benchmarks.py --engine-smoke

# Verify package consistency.
& '.\.local\benchmarks\.venv\Scripts\python.exe' -m pip check
```

The optional engine check needs the existing local FalkorDB listener at `127.0.0.1:6381`. It uses a fresh `test_bench_smoke_<UUID>` graph and an isolated Qdrant path under `.local/benchmarks/smoke-stores/`. It deletes only its owned graph/auxiliary keys and retains its small Qdrant directory as a diagnostic artifact. Existing application memories are not opened or changed. This is a smoke test, not a public-benchmark run or a reliability result.

`engine-config.json` enables reranking for a separate benchmark profile and points to the local model cache. Pass this configuration explicitly when building the benchmark runner; changing the application's normal configuration is unnecessary. `check_benchmarks.py` sets offline mode before model initialization and records the actual execution providers.

To rebuild the installation with the saved pins:

```powershell
# Use Python 3.12 to create this environment if it does not already exist.
python -m venv .local/benchmarks/.venv
& '.\.local\benchmarks\.venv\Scripts\python.exe' -m pip install -r requirements/benchmarks.txt
& '.\.local\benchmarks\.venv\Scripts\python.exe' -u scripts/setup_benchmarks.py
```

The setup script reuses `revisions.json` and verifies downloaded file hashes. The complete resolved package list is in `.local/benchmarks/requirements.lock.txt`. Reruns do not advance the pinned upstream revisions automatically.

## Dataset details and boundaries

- LoCoMo is adapted as text-only dialogue turns with speaker/date context. Original summaries, gold answers, evidence labels, and QA text are not ingested into document text. Images and captions are not added. Category 5 is retained separately; it must not be silently merged into ordinary answerable-question scoring.
- Nine LoCoMo QA entries have evidence annotations that do not exactly match dialogue IDs, including compound/irregular formatting and unresolved references. They are preserved verbatim and enumerated in `readiness.json`; no silent correction or exclusion was applied. Define and record an annotation-normalization/scoring policy before evidence-recall evaluation.
- Some LongMemEval histories repeat source session IDs. The adapter preserves every occurrence with a unique document ID and retains the original session ID for session-level evidence scoring. `has_answer` labels never enter document text. All three LongMemEval files have 500 parsed cases with matched answer-session references.
- LongMemEval-M is streamed to avoid loading its 2.74 GB JSON into memory. Oracle provides answer-bearing sessions and must be labelled as an oracle condition, not full-history retrieval.
- Retrieval dates remain original strings. This adapter does not infer temporal claims, parse question time into engine timestamps, or make raw ingestion equivalent to lifecycle extraction.
- These materials include data adapters and install/readiness checks, **not a completed end-to-end QA benchmark runner**. Reader generation, reader token budgets, official/category-specific scoring or judge configuration, and controlled comparison protocols still need to be connected before reporting benchmark accuracy. Upstream evaluation scripts are retained as source references; their optional provider/BERTScore stacks have not been installed or executed.
- No external inference API, paid judge, full public benchmark, GPU installation, or publication-score measurement was run. The nine-page research manuscript remains unchanged and does not acquire new benchmark claims from this setup.
