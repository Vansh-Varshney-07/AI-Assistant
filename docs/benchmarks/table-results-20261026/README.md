# Run the four-table collector

The single entry point is `scripts/collect_paper_tables.py`. It was executed successfully on 26 October 2026 in **16.1 seconds** after preparation, with **zero external inference calls/tokens**. This elapsed time is the collector run, not the time spent locating and checking the source artifacts.

From `D:\Opencode_\AI assistant`, use the existing CUDA environment:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -u scripts/collect_paper_tables.py
```

This uses the **current project's** reranker code and model cache; the older environment supplies the already installed CUDA dependencies. No global package changes or application-memory writes occur. All 597 retained retrieval cases are read; 595 have evidence annotations suitable for the macro retrieval metric. Nine fresh reranker-only checks use the actual RTX 4050 CUDA session. The default batch size is 2, using the model's existing 512-token pair limit; candidate pools are not reduced to make this check appear faster.

For CPU-only artifact aggregation (no model inference at all):

```powershell
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/collect_paper_tables.py --skip-gpu
```

Collector validation, including exact paired statistics and unavailable-value handling:

```powershell
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/collect_paper_tables.py --self-test
```

## Outputs

- `four_tables.md`: all four tables, evidence boundaries, caveats and source hashes.
- `table1_retrieval.csv`: recomputed historical retrieval evidence and clearly separate published context.
- `table2_qa.csv`: verified published QA/judge context; Iron Web's missing generated-answer scores remain unavailable.
- `table3_paired_statistics.csv`: requires actual per-question QA pairs; p-values are not reconstructed from marginal percentages.
- `table4_costs.csv`: labelled historical retrieval/ingestion values, failed cold-ingestion attempts, external reported search latencies, and separately labelled fresh GPU component checks.
- `retrieval_per_case.jsonl`: all 597 case identities, including the two explicitly unscored cases.
- `gpu_replay_per_case.jsonl`: the nine fresh local checks with complete retained candidate counts and observed timings.
- `results.json`: full-precision measurements, source paths/hashes, model revision, execution-provider/hardware information, elapsed time and missingness.

The old slash-separated latency values refer to DMR, LoCoMo and LongMemEval **without reranking**. The collector recovers actual metric/profile labels and also includes reranked latency, which is substantially different. The historical source revision is not the current Iron Web revision.

## What this run cannot fill

This is a fast evidence collector plus a small current-device component check, **not a fresh full public-benchmark run or an end-to-end local-reader evaluation**. The retained answer generator is `first_context_line`. No verified per-question source was found for the pasted Iron Web gpt-oss-20b accuracies or paired p-values. Those cells remain N/A rather than accepting the pasted numbers as measured facts. The current local QA reader/scoring pipeline has not been installed or run by this collector. Competitor systems are not run locally; their rows are published context with differing protocols.

Once real matched QA outputs have been generated and graded, pass `--qa-pairs PATH`. Each JSONL row must provide `benchmark` (`dmr`, `locomo`, or `longmemeval`), a unique `example_id`, `reader_model`, `grading_protocol`, and actual boolean `ironweb_correct` / `baseline_correct`. Supply every attempted case under a recorded inclusion policy, rather than selecting only successful cases. The script computes the percentages, paired discordance counts, exact McNemar p-values, and Holm adjustment for the predeclared three-benchmark family. These statistics do not by themselves address dependence between questions from shared histories.

No manuscript claims or existing research-paper files were updated automatically.
