# Updated tables with published competitor evidence

Completed 26 October 2026. Open **[four_tables.md](four_tables.md)** for the four main tables and their source links. CSV exports are `table1_retrieval.csv`, `table2_qa.csv`, `table3_paired_statistics.csv`, and `table4_costs.csv`. `results.json` retains full-precision measurements and provenance.

## What changed

- Zep, Mem0/Mem0g, and MemPalace values now come from the cited papers or pinned official project documentation/result artifacts. They are not new local competitor runs. Graphiti is not substituted for Zep.
- The table layout lists supported metric rows rather than inventing numbers for a rectangular matrix. Coverage notes explicitly identify the requested combinations that the reviewed sources do not report. Mem0/Zep QA percentages are never relabelled as Recall or MRR.
- MemPalace's official guide supplies expected LongMemEval hit-any@5 = 0.966 and hit-any@10 = 0.982, and LoCoMo session-retrieval average recall = 0.603. These remain project-reported expected outputs, with the metric definitions checked against published code. They are not independent local replications or macro-recall equivalents.
- Official Mem0 managed-v3 public JSON files enable independent recomputation of question-level outcomes. The same revision's README gives different headline counts. Both snapshots are retained in `external_snapshot_discrepancies.json`; the main artifact-derived rows use identifiable per-question labels rather than choosing the larger number.

## New local Iron Web reader measurements

Actual local generation filled the QA and statistical results. The run generated **1,056 answers for 528 matched question pairs**: DMR 100, LoCoMo 328, LongMemEval 100. Generation took **195.92 seconds**, excluding installation, context preparation and source verification. There were **zero generation errors** and **zero external inference calls**. The local model generated 10,202 output tokens; local computation is not described as zero-token computation.

The reader is **Qwen2.5-1.5B-Instruct Q4_K_M**, with llama.cpp `b11889`, greedy decoding, seed 20261026, five retrieved sources, a 768-token evidence budget, and a maximum of 48 output tokens. Its actual CUDA process, model SHA-256/revision, and runtime configuration are recorded in `reader_runtime_proof.json`. The private reader was stopped after measurement.

This is **new reader replay of historical retrieval outputs**, not a fresh run of the current memory engine or the full public benchmarks. Baseline uses archived vector-mode rankings; treatment uses archived hybrid-plus-reranking rankings. The original generation placeholder is not used as an LLM answer. The former user-pasted gpt-oss-20b percentages/p-values remain unsupported and were not relabelled as these new observations.

Strict normalized exact-match outcomes are:

- DMR: 7/100 treatment, 6/100 baseline.
- LoCoMo: 10/328 treatment, 10/328 baseline.
- LongMemEval: 8/100 treatment, 10/100 baseline.

These are deliberately conservative answer-string scores from a small reader and short context. Table 2 also includes mean token F1. They are **not directly comparable** with GPT-4/GPT-5 semantic-judge scores. Exact paired p-values are 1, 1, and 0.625; Holm-adjusted values are all 1. Questions share histories, so independence and generalizability remain limited.

The 69 missing-gold LoCoMo cases are explicitly listed as exclusions in `local_qa_protocol.json`, identically for both QA conditions. They are not converted into automatically correct abstentions. Retrieval analysis still processes 397 LoCoMo cases, with 395 having gold evidence annotations. No source gold answers or grading labels enter reader prompts.

## Recompute the tables without new inference

From the project root:

```powershell
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/collect_paper_tables.py --skip-gpu
```

The script automatically uses the completed local paired-answer file in this output directory. It recomputes retained metrics, public-artifact scores, exact statistics and tables without paid APIs or new generation.

Checks for paired statistics and unavailable-value handling:

```powershell
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/collect_paper_tables.py --self-test
```

To regenerate/resume the same local QA protocol explicitly:

```powershell
& '.\.local\benchmarks\.venv\Scripts\python.exe' scripts/collect_paper_tables.py --run-local-qa --skip-gpu
```

That flag can start a private localhost reader from the installed, verified binaries and stops only the process it starts. Cached answers are reused only under matching reader/source/token-budget/seed settings. Use a new `--output` folder when deliberately changing protocols; `--qa-limit 0` selects all eligible frozen-cohort questions.

## Evidence files

- `local_qa_predictions.jsonl`: actual source excerpts, questions, generated responses, token counts, timing, finish reasons, and exact-match/token-F1 scores for all 1,056 responses.
- `local_qa_pairs.jsonl`: all 528 matched correctness pairs and their gold answers, predictions and grading definition.
- `local_qa_protocol.json`, `local_qa_summary.json`, `reader_runtime_proof.json`: conditions, exclusions, elapsed generation time and GPU/runtime evidence.
- `retrieval_per_case.jsonl`: all 597 historical query identities, including the two unscored evidence cases.
- `external_snapshot_discrepancies.json`: the four differing Mem0 README/result-file pairs.
- `../external-sources/20261026/`: pinned official documentation, metric-definition source text, public per-question Mem0 result files and upstream commit lock.
- `results.json`: source hashes/links, collector hash, full precision calculations, raw analysis rows and final reported table rows.
- `detailed_analysis_audit.md`: intermediate wide analysis and its explicit missingness; this is not the final presentation table.

Existing memory stores, application configuration, implementation and nine-page manuscript were not edited. Mem0/MemPalace packages were prepared in a separate environment while local comparisons were being considered, but no competitor SDK measurement is claimed after the scope changed to online published evidence.
