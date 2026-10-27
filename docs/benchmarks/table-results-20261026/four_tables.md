# Four-table evidence report

Generated locally from retained artifacts and paper extracts. Historical reanalysis, external reported values, and fresh CUDA diagnostics are separate evidence categories. No external inference or judge calls were made. N/A is unavailable, not zero.

**Key corrections:** the historical retrieval cohorts contain DMR 100, LoCoMo 397 (395 evidence-scored), and LongMemEval 100 queries. These are retained 20% question cohorts with complete history corpora, not the full public datasets. Their answer generator is `first_context_line`, not gpt-oss-20b. The pasted 60.0%, 35.1%, 30.8% and their paired p-values have no verified case-level source here and are not promoted to measured results.

Recall is macro evidence-ID coverage; MRR is truncated at 10. MemPalace's separately quoted hit-any@5 has a different definition. Published QA/judge results use different readers and protocols and cannot establish a ranking. No accuracy is derived from retrieval recall or copied placeholder answers.

## Table 1. Retrieval evidence

| Benchmark | System | Total n | Scored n | Macro Recall@5 | MRR@10 | Macro Recall@10 | Reported hit-any@5 | Source |
|---|---|---|---|---|---|---|---|---|
| DMR | Iron Web (historical hybrid + reranking) | 100 | 100 | 0.09 | 0.0315833 | 0.14 | N/A | S001 |
| DMR | Zep | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| DMR | Mem0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| DMR | MemPalace | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| LoCoMo | Iron Web (historical hybrid + reranking) | 397 | 395 | 0.787215 | 0.717436 | 0.89616 | N/A | S004 |
| LoCoMo | Zep | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| LoCoMo | Mem0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| LoCoMo | MemPalace | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| LongMemEval | Iron Web (historical hybrid + reranking) | 100 | 100 | 0.851333 | 0.756234 | 0.9455 | N/A | S005 |
| LongMemEval | Zep | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| LongMemEval | Mem0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| LongMemEval | MemPalace | N/A | N/A | N/A | N/A | N/A | 0.966 | S006 |

## Table 2. End-to-end QA evidence and published context

| Benchmark | System | Reader | QA / judge score (%) | Local paired n | Delta (pp) | Scoring | Source |
|---|---|---|---|---|---|---|---|
| DMR | Iron Web | N/A | N/A | N/A | N/A | N/A | N/A |
| LoCoMo | Iron Web | N/A | N/A | N/A | N/A | N/A | N/A |
| LongMemEval | Iron Web | N/A | N/A | N/A | N/A | N/A | N/A |
| DMR | Zep | gpt-4-turbo | 94.8 | N/A | 0.4 | paper-reported QA; original protocol | S007 |
| DMR | Zep | gpt-4o-mini | 98.2 | N/A | 0.2 | paper-reported QA; original protocol | S007 |
| LongMemEval | Zep | gpt-4o-mini | 63.8 | N/A | 8.4 | paper-reported QA; original protocol | S007 |
| LongMemEval | Zep | gpt-4o | 71.2 | N/A | 11 | paper-reported QA; original protocol | S007 |
| LoCoMo | Zep | gpt-4o-mini | 65.99 | N/A | -6.91 | paper-reported LLM-as-a-Judge score; four categories | S008 |
| LoCoMo | Mem0 | gpt-4o-mini | 66.88 | N/A | -6.02 | paper-reported LLM-as-a-Judge score; four categories | S008 |
| LoCoMo | Mem0g | gpt-4o-mini | 68.44 | N/A | -4.46 | paper-reported LLM-as-a-Judge score; four categories | S008 |
| LongMemEval | MemPalace | N/A | 67.2 | N/A | N/A | approximate QA value quoted by a critical analysis | S006 |

## Table 3. Paired QA statistical evidence

| Benchmark | Paired n | Iron Web (%) | Baseline (%) | Delta (pp) | Exact p | Holm p | Status |
|---|---|---|---|---|---|---|---|
| DMR | N/A | N/A | N/A | N/A | N/A | N/A | Unavailable; marginal percentages do not identify discordant pairs |
| LoCoMo | N/A | N/A | N/A | N/A | N/A | N/A | Unavailable; marginal percentages do not identify discordant pairs |
| LongMemEval | N/A | N/A | N/A | N/A | N/A | N/A | Unavailable; marginal percentages do not identify discordant pairs |

## Table 4. Separately labelled timing and ingestion evidence

| Benchmark | System | Backend | Profile | Timing boundary | Query n | Mean ms | p50 ms | p95 ms | Cold ingest s | Failed ingest elapsed s | Ingest status | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DMR | Iron Web historical | kuzu | vector | retrieval incl. graph/vector/scoring | 100 | 11.4561 | 10.7239 | 15.3082 | 26.8439 | N/A | complete | S010;S009;S011 |
| DMR | Iron Web historical | kuzu | default_hybrid | retrieval incl. graph/vector/scoring | 100 | 39.8358 | 39.4894 | 46.9644 | 26.8439 | N/A | complete | S012;S009;S011 |
| DMR | Iron Web historical | kuzu | reranked_hybrid | retrieval incl. graph/vector/scoring | 100 | 1730.61 | 1740.94 | 1768.2 | 26.8439 | N/A | complete | S013;S009;S011 |
| DMR | Iron Web historical | falkordb_before | vector | retrieval incl. graph/vector/scoring | 100 | 14.1318 | 13.7217 | 16.5516 | N/A | 27.2886 | failed | S014;S009;S015 |
| DMR | Iron Web historical | falkordb_before | default_hybrid | retrieval incl. graph/vector/scoring | 100 | 54.2688 | 52.6853 | 56.9198 | N/A | 27.2886 | failed | S016;S009;S015 |
| DMR | Iron Web historical | falkordb_before | reranked_hybrid | retrieval incl. graph/vector/scoring | 100 | 1943.89 | 1779.84 | 2454.36 | N/A | 27.2886 | failed | S017;S009;S015 |
| DMR | Iron Web historical | falkordb_after | vector | retrieval incl. graph/vector/scoring | 100 | 14.5881 | 14.3426 | 16.8482 | 85.6747 | N/A | complete | S018;S009;S019 |
| DMR | Iron Web historical | falkordb_after | default_hybrid | retrieval incl. graph/vector/scoring | 100 | 27.9549 | 27.7995 | 30.4898 | 85.6747 | N/A | complete | S020;S009;S019 |
| DMR | Iron Web historical | falkordb_after | reranked_hybrid | retrieval incl. graph/vector/scoring | 100 | 2356.74 | 2366.53 | 2399.26 | 85.6747 | N/A | complete | S001;S009;S019 |
| LoCoMo | Iron Web historical | kuzu | vector | retrieval incl. graph/vector/scoring | 397 | 9.10912 | 8.8423 | 12.0161 | 4.51668 | N/A | complete | S021;S009;S022 |
| LoCoMo | Iron Web historical | kuzu | default_hybrid | retrieval incl. graph/vector/scoring | 397 | 27.5049 | 27.1815 | 35.4005 | 4.51668 | N/A | complete | S023;S009;S022 |
| LoCoMo | Iron Web historical | kuzu | reranked_hybrid | retrieval incl. graph/vector/scoring | 397 | 414.973 | 356.556 | 605.729 | 4.51668 | N/A | complete | S024;S009;S022 |
| LoCoMo | Iron Web historical | falkordb_before | vector | retrieval incl. graph/vector/scoring | 397 | 15.4688 | 15.1263 | 19.9569 | N/A | 7.03606 | failed | S025;S009;S026 |
| LoCoMo | Iron Web historical | falkordb_before | default_hybrid | retrieval incl. graph/vector/scoring | 397 | 33.0319 | 32.7679 | 37.1174 | N/A | 7.03606 | failed | S027;S009;S026 |
| LoCoMo | Iron Web historical | falkordb_before | reranked_hybrid | retrieval incl. graph/vector/scoring | 397 | 432.507 | 375.328 | 633.539 | N/A | 7.03606 | failed | S028;S009;S026 |
| LoCoMo | Iron Web historical | falkordb_after | vector | retrieval incl. graph/vector/scoring | 397 | 14.8657 | 14.5944 | 18.3661 | 9.43023 | N/A | complete | S029;S009;S030 |
| LoCoMo | Iron Web historical | falkordb_after | default_hybrid | retrieval incl. graph/vector/scoring | 397 | 20.7229 | 20.1663 | 24.8328 | 9.43023 | N/A | complete | S031;S009;S030 |
| LoCoMo | Iron Web historical | falkordb_after | reranked_hybrid | retrieval incl. graph/vector/scoring | 397 | 415.732 | 357.548 | 601.108 | 9.43023 | N/A | complete | S004;S009;S030 |
| LongMemEval | Iron Web historical | kuzu | vector | retrieval incl. graph/vector/scoring | 100 | 101.114 | 82.1615 | 203.66 | 340.413 | N/A | complete | S032;S009;S033 |
| LongMemEval | Iron Web historical | kuzu | default_hybrid | retrieval incl. graph/vector/scoring | 100 | 177.705 | 173.804 | 211.4 | 340.413 | N/A | complete | S034;S009;S033 |
| LongMemEval | Iron Web historical | kuzu | reranked_hybrid | retrieval incl. graph/vector/scoring | 100 | 1152.98 | 1133.91 | 1324.79 | 340.413 | N/A | complete | S035;S009;S033 |
| LongMemEval | Iron Web historical | falkordb_before | vector | retrieval incl. graph/vector/scoring | 100 | 118.988 | 115.289 | 135.652 | N/A | 11.158 | failed | S036;S009;S037 |
| LongMemEval | Iron Web historical | falkordb_before | default_hybrid | retrieval incl. graph/vector/scoring | 100 | 337.721 | 319.348 | 419.787 | N/A | 11.158 | failed | S038;S009;S037 |
| LongMemEval | Iron Web historical | falkordb_before | reranked_hybrid | retrieval incl. graph/vector/scoring | 100 | 1480.72 | 1372.14 | 2130.28 | N/A | 11.158 | failed | S039;S009;S037 |
| LongMemEval | Iron Web historical | falkordb_after | vector | retrieval incl. graph/vector/scoring | 100 | 114.713 | 118.951 | 138.635 | 4868.14 | N/A | complete | S040;S009;S041 |
| LongMemEval | Iron Web historical | falkordb_after | default_hybrid | retrieval incl. graph/vector/scoring | 100 | 121.899 | 119.568 | 140.881 | 4868.14 | N/A | complete | S042;S009;S041 |
| LongMemEval | Iron Web historical | falkordb_after | reranked_hybrid | retrieval incl. graph/vector/scoring | 100 | 2212.27 | 2166.21 | 2899.54 | 4868.14 | N/A | complete | S005;S009;S041 |
| LoCoMo | Zep | published service | external published study | search only | N/A | N/A | 513 | 778 | N/A | N/A | N/A | S008 |
| LoCoMo | Mem0 | published service | external published study | search only | N/A | N/A | 148 | 200 | N/A | N/A | N/A | S008 |
| LoCoMo | Mem0g | published service | external published study | search only | N/A | N/A | 476 | 657 | N/A | N/A | N/A | S008 |
| DMR | Iron Web current reranker component | not exercised | CUDA FP32, batch 2, 512-token pair limit | cross-encoder only; not end-to-end retrieval | 3 | 1222.37 | 1224.07 | N/A | N/A | N/A | N/A | gpu_replay_per_case.jsonl |
| LoCoMo | Iron Web current reranker component | not exercised | CUDA FP32, batch 2, 512-token pair limit | cross-encoder only; not end-to-end retrieval | 3 | 474.99 | 541.527 | N/A | N/A | N/A | N/A | gpu_replay_per_case.jsonl |
| LongMemEval | Iron Web current reranker component | not exercised | CUDA FP32, batch 2, 512-token pair limit | cross-encoder only; not end-to-end retrieval | 3 | 1172.84 | 1155.61 | N/A | N/A | N/A | N/A | gpu_replay_per_case.jsonl |

## Timing and statistics boundaries

All historical latency values are recomputed from per-query durations. Cold-ingestion completion times are taken from the retained summary and linked to per-add logs, whose counts are checked; preparation overhead prevents recovering complete ingest time by summing add latencies. Failed ingestion remains partial and is never called a completed-corpus time. A query on a prepared snapshot can complete even when a separate cold-ingestion trial failed.

The original slash-separated latency values identify DMR / LoCoMo / LongMemEval means for **hybrid without reranking**. They must not be described as reranked latency. Table 4 includes vector, no-rerank hybrid, and reranked profiles separately. It repeats each backend's one ingestion measurement across profiles for context; these are not independent ingestion trials.

Fresh GPU timings are only cross-encoder replay on retained complete candidate pools, batch 2 and the model's existing 512-token pair limit. They exclude retrieval, ingestion, reader generation, and model warmup. Nine sampled checks are not a full public benchmark or a stable p95 estimate. No speedup is inferred across these different boundaries.

Table 3 requires actual matched per-question correctness labels. Exact two-sided McNemar tests use discordant pairs; Holm uses the three-benchmark planned family (missing tests treated as p=1 for the correction only). Dependence between questions sharing a history is not resolved by this test. A statistically significant result would still need an appropriate dependence analysis.

An optional `--qa-pairs PATH` file can supply real paired labels and their declared reader/grading protocol. This collector computes the resulting tables and tests; it does not invent labels or execute provider-based judges. The files here do not constitute new gpt-oss-20b QA evaluation.

## Sources

- S001: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_reranked_hybrid_falkordb_after.jsonl`; SHA-256 `2cea29a0b42a2548e4b74be14ece156663b5ae462f17ebcf81e1be09f6f81dca` (retained artifact).
- S002: `D:\Opencode_\reserchpaper\report\reranker_diagnosis_20261014\full_summary.json`; SHA-256 `172e15297b191590eb6f2822f8c53c0c2d628ebfa0069fe2a76ba0281db3e319` (retained artifact).
- S003: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\report.md`; SHA-256 `1cb0886cec71e3ffc1b69c548032ddc5dfe6d5686392e4b890b82ca821ef7acd` (historical run protocol report).
- S004: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_reranked_hybrid_falkordb_after.jsonl`; SHA-256 `a293bc2675114a3a2191b828b29a12d9d02ea5d290f4bb08745f5b9f8be728cb` (retained artifact).
- S005: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_reranked_hybrid_falkordb_after.jsonl`; SHA-256 `b8479b65ad64831ff0aa351ff9c5746414db175108c8fc6a3cbf9ebf39227d58` (retained artifact).
- S006: `D:\Opencode_\AI assistant\docs\research\iron-web-paper\extracted\2604.21284v1.txt`; SHA-256 `02abc20c952504340b2932a27aeeaeb814626b4307001329b1c298993363b005` (published-paper extract).
- S007: `D:\Opencode_\AI assistant\docs\research\iron-web-paper\extracted\2501.13956v1.txt`; SHA-256 `e4c4a282b6ec87115f8e84941704e57075647964a0f7e508ecf6f45939e02ae0` (published-paper extract).
- S008: `D:\Opencode_\AI assistant\docs\research\iron-web-paper\extracted\2504.19413v1.txt`; SHA-256 `f3cff8c134b68167f4ab004bc5cfe151b7ff50368a550054a655498529200f98` (published-paper extract).
- S009: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\verified_summary.json`; SHA-256 `c75ee9aa493f4690aa7fba2b98774dd5fe8030e9b07cc496f2780b206684b5ca` (retained artifact).
- S010: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_vector_kuzu.jsonl`; SHA-256 `5e68fd2da40c1968b0cb8d70c48d5def040114e883258b8d4bb615e039520f0b` (retained artifact).
- S011: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\dmr_kuzu.jsonl`; SHA-256 `3a4f056962af9193a1d838c178c571b603fb0d7a8869c8f6bf6d5f6b6a449a6d` (retained artifact).
- S012: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_default_hybrid_kuzu.jsonl`; SHA-256 `a2389074292e26544741fe46c8f92af7accc2003f10ec2007b5fba7fcdb66977` (retained artifact).
- S013: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_reranked_hybrid_kuzu.jsonl`; SHA-256 `2fbc1fb19cebd695e1f57be23a3eb2a82ff5f822a81230ab60f236ed52fdf7ce` (retained artifact).
- S014: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_vector_falkordb_before.jsonl`; SHA-256 `07d8a9b28ba1b5b5f3bbe6747457f9fc9e886f0dfbffa96997cacac436bcb46f` (retained artifact).
- S015: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\dmr_falkordb_before.jsonl`; SHA-256 `81d3756ad226be49125657a6070c632384a0b386b86142e17519aa7903db43a5` (retained artifact).
- S016: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_default_hybrid_falkordb_before.jsonl`; SHA-256 `011705fa5dff7ab1a8679dd6da0bf34a3ff0850ab76090b33e5cf544c9ad69bc` (retained artifact).
- S017: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_reranked_hybrid_falkordb_before.jsonl`; SHA-256 `0c1f2296134ba7f17d206bc763a99a21093d2abea2fc20d45eab4d864e84390f` (retained artifact).
- S018: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_vector_falkordb_after.jsonl`; SHA-256 `8c0e4d586d4498a3ed67b67856e6bffc5a4022f10a6017119686c7c10ce1d703` (retained artifact).
- S019: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\dmr_falkordb_after.jsonl`; SHA-256 `dddaf3c1d8f28a634d9fc4ef495d1762fb524c9a349554eeab30187ae122e431` (retained artifact).
- S020: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_default_hybrid_falkordb_after.jsonl`; SHA-256 `e2cbff83619ea924adba4ee52eaa661cc5a051e6a00475ccde17787597bee3a9` (retained artifact).
- S021: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_vector_kuzu.jsonl`; SHA-256 `915f72c52c1a87229eaab2ab5c1e344ea830b77bbac2d5f37aada639561e2b60` (retained artifact).
- S022: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\locomo_kuzu.jsonl`; SHA-256 `96a64655b1709f82559ac6c950b7a0b2c344b6ab063058263343ccca47b46ad8` (retained artifact).
- S023: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_default_hybrid_kuzu.jsonl`; SHA-256 `0f32093081784679920f0c44d47a9fdf6ceb1e8eb4e75c53e7856df33553fdc3` (retained artifact).
- S024: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_reranked_hybrid_kuzu.jsonl`; SHA-256 `2a755f5dbfd9f085e6c197f94e6769d618abaef3c830580dbd9d8cfd5fe822b1` (retained artifact).
- S025: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_vector_falkordb_before.jsonl`; SHA-256 `90d9656ab4f65aba54a81abaaab60d66daf707a50fae7e47bcb1acc0e89fa037` (retained artifact).
- S026: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\locomo_falkordb_before.jsonl`; SHA-256 `77ac5ad0f9dbdb292ca8f56150747ed823c939ed55918e38ab4a12d2b806f338` (retained artifact).
- S027: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_default_hybrid_falkordb_before.jsonl`; SHA-256 `7c52a0af652ae69165bda330ba64b4eae564f7be678cda00068eb96ff9527adb` (retained artifact).
- S028: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_reranked_hybrid_falkordb_before.jsonl`; SHA-256 `37c33574da18aa5d6add38c9dd234861aedb0fd990250268f06eabb578994340` (retained artifact).
- S029: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_vector_falkordb_after.jsonl`; SHA-256 `30e8cb04417832bd4406612cd54f2ac475f45b8703276f6d036c195ecb42716b` (retained artifact).
- S030: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\locomo_falkordb_after.jsonl`; SHA-256 `6c980cad71fdd9a4ccf351dfb30b5d8145afbea6768f6066383242f6acbb5c95` (retained artifact).
- S031: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_default_hybrid_falkordb_after.jsonl`; SHA-256 `84d76717eb0da3f4f9f494ab5292adacfb7e55a5798ee986c2db90d3b07d5c65` (retained artifact).
- S032: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_vector_kuzu.jsonl`; SHA-256 `1ffe5a33ead0fdd385387ae5323d58fa88546b9ff4c34f28f3cbada83edaeee2` (retained artifact).
- S033: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\longmemeval_kuzu.jsonl`; SHA-256 `5fb66265d78dc5f959eaaf38f23f7bfd50fa209ee47946f1aec367a3918ae4f7` (retained artifact).
- S034: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_default_hybrid_kuzu.jsonl`; SHA-256 `5e8349e9540b0b44dfd2e6e145e1a1bdc5b672073e1eed9aa427ee311f03b68d` (retained artifact).
- S035: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_reranked_hybrid_kuzu.jsonl`; SHA-256 `74b9ea5a71fd166b2afcad2d18ed561aeaa36122da5588ee82dbdb78cc8d1e5d` (retained artifact).
- S036: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_vector_falkordb_before.jsonl`; SHA-256 `844e9095b79fe52e0b6b385634339e72c44e65c4379c12f88a62400b6757fff5` (retained artifact).
- S037: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\longmemeval_falkordb_before.jsonl`; SHA-256 `0fbf4d2837118fdd3c05160f0882f6017d836434ad08e04fbb615297ec6fbcca` (retained artifact).
- S038: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_default_hybrid_falkordb_before.jsonl`; SHA-256 `daa5b4815db78e89c736381f52d819c258823ce670ad95f5d4fdd99ae725b82b` (retained artifact).
- S039: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_reranked_hybrid_falkordb_before.jsonl`; SHA-256 `d35a97baca680ce8a3765b2e7d2cd6f2ef68c8fafc01c9b303508313add6845f` (retained artifact).
- S040: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_vector_falkordb_after.jsonl`; SHA-256 `7ecb4a2bd88710d369fa41e5313ed9f823b82dc6ffe2286a18e92ad02a115919` (retained artifact).
- S041: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\longmemeval_falkordb_after.jsonl`; SHA-256 `ccb26a78c591272deac7fe52e1a1738b788dc5036ffe3d718b36ee604b8cdf9a` (retained artifact).
- S042: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_default_hybrid_falkordb_after.jsonl`; SHA-256 `5a2ab666a7396f6600b6959516331606cd0327f0d245a61df754f0a791d73b1f` (retained artifact).
- S043: `D:\Opencode_\AI assistant\memory\ranking\reranker.py`; SHA-256 `f9d76638b0b52cbaa2c17c70e6d007a20c44269668d2a180614833dd60ed6018` (current reranker implementation).
- S044: `D:\Opencode_\AI assistant\memory\device.py`; SHA-256 `5070c0e8b7a726b15bbceec6117e82a5c00060000228491f7d024551993ba104` (current CUDA DLL/provider support).
- S045: `D:\Opencode_\AI assistant\.local\benchmarks\revisions.json`; SHA-256 `85e2cb0dc698d78864ea1079b41f497c9d3fab79f6b3d54e2f5ebbca16867535` (retained artifact).
- S046: `D:\Opencode_\AI assistant\.local\benchmarks\models\models--BAAI--bge-reranker-base\snapshots\2cfc18c9415c912f9d8155881c133215df768a70\onnx\model.onnx`; SHA-256 `15b9a8c3da82eddf263df571281166e00e9308fe19d077084b642ebfcaf06d2b` (actual pinned ONNX model weights).
- S047: `D:\Opencode_\reserchpaper\report\reranker_diagnosis_20261014\full_baseline.jsonl`; SHA-256 `d2828fddfb76531512e838dced0d66886f09d460eac62a52f1be2f746f6417df` (retained artifact).
- S048: `D:\Opencode_\reserchpaper\data\graph_full_analysis\full20_graph_20261013\inputs\dmr\dmr.json`; SHA-256 `ac0c4de54e5917633c372cc95f473ff15487a7afaa27dca68a62a0eb8630d4a8` (frozen full-history cohort input).
- S049: `D:\Opencode_\reserchpaper\data\graph_full_analysis\full20_graph_20261013\inputs\locomo\locomo.json`; SHA-256 `1f50288c1836a838489be56fad719e0b14edc3dfe4dd0d9d5dd6075af044b813` (frozen full-history cohort input).
- S050: `D:\Opencode_\reserchpaper\data\graph_full_analysis\full20_graph_20261013\inputs\longmemeval\longmemeval.json`; SHA-256 `82ee438f29b1c808b9633d86ca569e728e9bef22ecaa1300096ed7359d4c0fdd` (frozen full-history cohort input).

## Warnings
