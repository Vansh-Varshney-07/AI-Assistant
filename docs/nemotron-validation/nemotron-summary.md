# Nemotron Lightning / Ultra: repaired and tested

**Both requested models passed the final comparison: 18/18 live scenario checks, zero failures.** The complete architecture suite passed **187 tests**, with 3 optional tests deselected, in **128.07 seconds**. Ruff checks passed.

Each model completed the eight original scenarios plus source-event replay: creation, retrieval in a fresh session, preference classification/retrieval, automatic correction, conflicting claims, persistence after an actual server restart, stale-date supersession and retrieval precision. Checks inspected the real backend copies, stable IDs, claim states, replacement links, current evidence and generated citations. These were real NVIDIA calls and real cached BGE embeddings, not fixture model responses.

| Model | Live result | Median extraction call | Median answer generation | Median query request total |
| --- | --- | --- | --- | --- |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 9/9 | 1709 ms | 908 ms | 2130 ms |
| `nvidia/nemotron-3-ultra-550b-a55b` | 9/9 | 4776 ms | 6544 ms | 9601 ms |

These timings are observations from this small test run, not a general performance benchmark. Request totals include local inspection, semantic search, field routing and generation; generation alone is a separate component.

## What changed

- Schema-constrained Nemotron output with validated source quotes and bounded repair. Metadata and malformed responses cannot be accepted as source facts.
- Existing scoped field vocabulary is supplied to extraction. Corrections/supersession target actual existing claims through the original lifecycle.
- Query field routing calls the existing exact recall API so unrelated disputes do not contaminate the requested answer. Semantic candidates remain separately visible.
- Structured answer citations are restricted to actual returned memory IDs; the UI renders them as source buttons. Disputes cite both sides.
- Identical source retries reuse durable extracted claims without another model call or duplicate record.
- Scoped execution inspection avoids inspecting unrelated records. Large INT64 values retain their exact decimal representation in the browser.
- The local interface now offers both explicit model choices and identifies the model on each response.

No embedding model, reranker, storage backend, ranking formula, lifecycle algorithm or database schema was replaced. Existing records were not wiped. Earlier failed tests and their namespaces were retained for comparison. Pre-repair source copies are in `data/repair_backup_20261023/`.

## Try it

Open http://127.0.0.1:3352. Select one of the two exact model IDs. Use **Store prompt + retrieve first** for source statements, with user confirmation when asserting accepted facts; use **Retrieve only** for questions. Fresh conversation preserves long-term memory.

Final run: `nm_1023_125909`. Example namespaces:

- `nm_1023_125909_light_label` and `nm_1023_125909_ultra_label`: old Alpha retained as corrected, current Beta accepted.
- `nm_1023_125909_light_conflict` and `nm_1023_125909_ultra_conflict`: North/South remain disputed.
- `nm_1023_125909_light_review` and `nm_1023_125909_ultra_review`: old date superseded, current date 22 November 2026.

Twenty-six records were retained in the final run. Earlier test namespaces are distinct; they are not silently treated as current facts for this run.

## Startup and reproduction

Stop the delivered instance with **Stop workbench** before starting another process:

```powershell
Set-Location 'D:\Opencode_\memory_system'
docker compose up -d --pull never falkordb
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\workbench_server.py --nvidia --key-file 'D:\Opencode_\reserchpaper\.env'
```

With the workbench running:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_nemotron.py
```

This makes real NVIDIA calls, uses new labelled namespaces, retains records and restarts the server once per model. The key is read privately and never included in evidence. `nemotron-evidence.json` contains exact prompts, responses, extraction attempts, routed fields, IDs and timings. `nemotron-records.json` contains actual backend source/claim snapshots. `nemotron-results.csv` lists every check.

## Limits

The final observed scenarios pass; future provider outages, quota limits or semantic model mistakes can still occur. Validation fails safely and reports rejected output. The source quote is an audit boundary, not proof that every possible interpretation is true. The interface stays loopback-only and makes no production-security claim. Without --nvidia or with Evidence only selected, no hosted inference occurs.
