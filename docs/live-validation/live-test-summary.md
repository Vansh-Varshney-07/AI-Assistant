# Is the memory system working?

**The core memory engine works. The automatic NVIDIA extraction path is not reliable enough to call the whole system validated.**

These were live tests against the running workbench using real cached BGE embeddings, FalkorDB and embedded Qdrant. NVIDIA authentication and inference succeeded with the existing key and configured `meta/llama-3.2-11b-vision-instruct` model. No key is included in these files.

| Test | What was actually verified | Result |
| --- | --- | --- |
| Creation | Submitted original project prompts; read exact source IDs back from both stores | Pass |
| Across interactions | New session per request, no chat history; original source ID retrieved | Pass |
| Preference | Stored the preference sentence, recovered its actual ID on a fresh query | Pass for text retrieval |
| Restart persistence | Stopped and restarted the actual server; recovered same ID and copper-orchid-731 | Pass |
| Precision | Stored blue, green and orange facts; orange source ranked first | Pass; Top K also returned irrelevant records |
| Structured correction | Alpha source retained with corrected claim; only Beta current | Pass |
| Structured conflict | Both North/South assertions retained; engine returned disputed and a warning | Pass |
| Structured supersession | Old date claim superseded; current evidence says 22 November 2026 | Pass |
| Raw-text correction/conflict/rescheduling | These are not interpreted when default extraction is disabled | Unsupported |
| NVIDIA automatic ingestion | Five of eight extraction calls failed JSON parsing; field names varied between related claims | Fail |
| NVIDIA answers from verified evidence | All five meanings correct; two missed exact-memory-ID citation requirement | Three full passes, two citation failures |
| Architecture regression | Existing suite plus workbench checks | 164 passed; 3 optional tests deselected |

There are 24 labelled live checks: 11 Pass, 10 Fail and 3 Unsupported. Several failures share the same upstream extraction problem, so this is not an independent statistical success rate.

Semantic search-call timings in this run: 61.5–470.5 ms, median 66.6 ms. Adapter overhead and NVIDIA generation are separate. The five NVIDIA answer calls took about 1.0–12.5 seconds. These are observed local test samples, not a performance benchmark.

## Inspect the actual results

Open http://127.0.0.1:3352. Test namespaces:

- `live_1023_121339_raw`: original free-text tests and persistence phrase.
- `live_1023_121339_precision`: the three notebook facts.
- `live_1023_121339_typed`: corrections, conflicts and supersession.
- `live_1023_121339_nvidia`: successful NVIDIA-extracted records; rejected calls are in evidence JSON.

The dashboard has been left showing the structured project-label test. Search `project_label` to inspect the Alpha and Beta source records. Alpha: `wb_27f85909f65148a5a00fb5ac1d15d871`; Beta: `wb_8dd2240d92e242eb92db16860e698ef6`. Source contents remain immutable; their claim states carry the correction.

Twenty-one labelled test records were retained for inspection. Existing records were not deleted. The test runner used NVIDIA for synthetic prompts and evidence only; it did not silently enable NVIDIA in the workbench's default configuration.

## Reproduce

With the workbench running:

```powershell
Set-Location 'D:\Opencode_\memory_system'
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_workbench_live.py --output .\docs\live-validation-next
```

Each run creates new labelled namespaces, retains records and cleanly restarts the server once. Use `--skip-nvidia` for local-only tests. To repeat the additional capture/grounded-answer diagnosis on the default saved run, execute `scripts/diagnose_nvidia_validation.py` from the same virtual environment; this appends checks and makes additional NVIDIA calls.

The full report, CSV, request/response evidence, stored-record snapshots, raw parser diagnosis and both runnable test scripts accompany this summary. The memory/extraction/retrieval algorithms were not changed during testing.
