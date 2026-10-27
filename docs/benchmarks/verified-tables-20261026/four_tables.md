# Four verified evidence tables

Every displayed numerical row is recomputed from retained/local records or taken from an identified published source. Rows have different protocols: they are evidence summaries, not a controlled system ranking. Unreported combinations are listed in the coverage notes; no metric is imputed from a different metric.

## Table 1. Retrieval measurements

| Benchmark | System | Metric | Value | Scope / n | Source |
|---|---|---|---|---|---|
| DMR | Iron Web historical hybrid + reranking | macro evidence Recall@5 | 0.09 | 100 | S001 |
| DMR | Iron Web historical hybrid + reranking | MRR@10 | 0.0315833 | 100 | S001 |
| DMR | Iron Web historical hybrid + reranking | macro evidence Recall@10 | 0.14 | 100 | S001 |
| LoCoMo | Iron Web historical hybrid + reranking | macro evidence Recall@5 | 0.787215 | 395 | S004 |
| LoCoMo | Iron Web historical hybrid + reranking | MRR@10 | 0.717436 | 395 | S004 |
| LoCoMo | Iron Web historical hybrid + reranking | macro evidence Recall@10 | 0.89616 | 395 | S004 |
| LongMemEval | Iron Web historical hybrid + reranking | macro evidence Recall@5 | 0.851333 | 100 | S005 |
| LongMemEval | Iron Web historical hybrid + reranking | MRR@10 | 0.756234 | 100 | S005 |
| LongMemEval | Iron Web historical hybrid + reranking | macro evidence Recall@10 | 0.9455 | 100 | S005 |
| LongMemEval | MemPalace raw | hit-any@5 | 0.966 | 500 | S016 |
| LongMemEval | MemPalace raw | hit-any@10 | 0.982 | 500 | S016 |
| LoCoMo | MemPalace raw, session granularity | reported average evidence recall@10 | 0.603 | full 10-conversation project report | S016 |

Iron Web uses macro coverage of gold evidence IDs; MemPalace LongMemEval uses hit-any recall. MemPalace values are the official project reproduction guide’s **expected outputs**, not raw runs independently reproduced here. Its LoCoMo session-granularity result is a different cohort/protocol. Mem0 and Zep source documents reviewed here do not supply compatible Recall@5/MRR/Recall@10 triplets for these datasets.

## Table 2. QA measurements and published context

| Benchmark | System | Metric | Score (%) | Reader | n / scope | Source |
|---|---|---|---|---|---|---|
| DMR | Iron Web ranking + local reader replay | normalized answer exact-match (%) | 7 | Qwen2.5-1.5B-Instruct Q4_K_M | 100 | S007 |
| DMR | Iron Web ranking + local reader replay | mean answer token-F1 (%) | 15.8024 | Qwen2.5-1.5B-Instruct Q4_K_M | 100 | S007 |
| LoCoMo | Iron Web ranking + local reader replay | normalized answer exact-match (%) | 3.04878 | Qwen2.5-1.5B-Instruct Q4_K_M | 328 | S007 |
| LoCoMo | Iron Web ranking + local reader replay | mean answer token-F1 (%) | 13.1171 | Qwen2.5-1.5B-Instruct Q4_K_M | 328 | S007 |
| LongMemEval | Iron Web ranking + local reader replay | normalized answer exact-match (%) | 8 | Qwen2.5-1.5B-Instruct Q4_K_M | 100 | S007 |
| LongMemEval | Iron Web ranking + local reader replay | mean answer token-F1 (%) | 9.89818 | Qwen2.5-1.5B-Instruct Q4_K_M | 100 | S007 |
| DMR | Zep | published QA/judge score (%) | 94.8 | gpt-4-turbo | see cited paper protocol | S008 |
| DMR | Zep | published QA/judge score (%) | 98.2 | gpt-4o-mini | see cited paper protocol | S008 |
| LongMemEval | Zep | published QA/judge score (%) | 63.8 | gpt-4o-mini | see cited paper protocol | S008 |
| LongMemEval | Zep | published QA/judge score (%) | 71.2 | gpt-4o | see cited paper protocol | S008 |
| LoCoMo | Zep | published QA/judge score (%) | 65.99 | gpt-4o-mini | see cited paper protocol | S009 |
| LoCoMo | Mem0 | published QA/judge score (%) | 66.88 | gpt-4o-mini | see cited paper protocol | S009 |
| LoCoMo | Mem0g | published QA/judge score (%) | 68.44 | gpt-4o-mini | see cited paper protocol | S009 |
| LongMemEval | Mem0 managed v3 (top_200 artifact) | published QA/judge score (%) | 93.4 | gpt-5 | 500 | S011 |
| LongMemEval | Mem0 managed v3 (top_50 artifact) | published QA/judge score (%) | 90.4 | gpt-5 | 500 | S013 |
| LoCoMo | Mem0 managed v3 (top_200 artifact) | published QA/judge score (%) | 91.5584 | gpt-5 | 1540 | S014 |
| LoCoMo | Mem0 managed v3 (top_50 artifact) | published QA/judge score (%) | 82.6623 | gpt-5 | 1540 | S015 |

Local rows use the newly installed Qwen2.5-1.5B Q4_K_M reader, top five archived retrieval results, a 768-token evidence budget, and at most 48 generated tokens. Exact match is strict and token F1 is a separate overlap metric. These values are not the earlier unverified gpt-oss-20b percentages and are not comparable to GPT-4/GPT-5 semantic-judge scores. LoCoMo has 328 answerable frozen-cohort cases; 69 missing-gold cases are explicitly excluded from both paired conditions. Retrieval still has 397 total cases, 395 evidence-scored.

Mem0 managed-v3 rows are recomputed from its public per-question PASS/CORRECT labels, with errors retained in the denominator. These public snapshots differ from the same revision’s README headline scores; see the discrepancy table below. They are separate from Mem0’s 2025 paper and from self-hosted SDK results.

## Table 3. Actual paired local QA statistics

| Benchmark | Paired n | Iron Web EM (%) | Vector-mode EM (%) | Delta (pp) | Exact p | Holm p |
|---|---|---|---|---|---|---|
| DMR | 100 | 7 | 6 | 1 | 1 | 1 |
| LoCoMo | 328 | 3.04878 | 3.04878 | 0 | 1 | 1 |
| LongMemEval | 100 | 8 | 10 | -2 | 0.625 | 1 |

Baseline is the same historical engine in vector mode, not a guaranteed untreated dense baseline. Both rankings use the same local reader, prompt, token budget, gold answers, and paired question IDs. Exact two-sided McNemar tests and Holm adjustment over three benchmarks use observed discordant pairs. Shared conversation histories limit independence and generalizability. These p-values compare Iron Web’s two retrieval conditions; they do not test Iron Web against an external published system.

## Table 4. Explicitly labelled performance measurements

| Benchmark | System | Metric boundary | Value | Unit | Scope | Source |
|---|---|---|---|---|---|---|
| DMR | Iron Web historical / kuzu | completed fresh-corpus ingestion | 26.8439 | s | 500/500 documents; complete | S020;S019;S021 |
| DMR | Iron Web historical / kuzu | default_hybrid mean retrieval | 39.8358 | ms | 100 archived queries; graph/vector/scoring included | S022;S019;S021 |
| DMR | Iron Web historical / kuzu | reranked_hybrid mean retrieval | 1730.61 | ms | 100 archived queries; graph/vector/scoring included | S023;S019;S021 |
| DMR | Iron Web historical / falkordb_before | FAILED cold ingestion: elapsed until failure | 27.2886 | s | 218/500 documents; failed | S024;S019;S025 |
| DMR | Iron Web historical / falkordb_after | completed fresh-corpus ingestion | 85.6747 | s | 500/500 documents; complete | S028;S019;S029 |
| DMR | Iron Web historical / falkordb_after | default_hybrid mean retrieval | 27.9549 | ms | 100 archived queries; graph/vector/scoring included | S030;S019;S029 |
| DMR | Iron Web historical / falkordb_after | reranked_hybrid mean retrieval | 2356.74 | ms | 100 archived queries; graph/vector/scoring included | S001;S019;S029 |
| LoCoMo | Iron Web historical / kuzu | completed fresh-corpus ingestion | 4.51668 | s | 70/70 documents; complete | S031;S019;S032 |
| LoCoMo | Iron Web historical / kuzu | default_hybrid mean retrieval | 27.5049 | ms | 397 archived queries; graph/vector/scoring included | S033;S019;S032 |
| LoCoMo | Iron Web historical / kuzu | reranked_hybrid mean retrieval | 414.973 | ms | 397 archived queries; graph/vector/scoring included | S034;S019;S032 |
| LoCoMo | Iron Web historical / falkordb_before | FAILED cold ingestion: elapsed until failure | 7.03606 | s | 60/70 documents; failed | S035;S019;S036 |
| LoCoMo | Iron Web historical / falkordb_after | completed fresh-corpus ingestion | 9.43023 | s | 70/70 documents; complete | S039;S019;S040 |
| LoCoMo | Iron Web historical / falkordb_after | default_hybrid mean retrieval | 20.7229 | ms | 397 archived queries; graph/vector/scoring included | S041;S019;S040 |
| LoCoMo | Iron Web historical / falkordb_after | reranked_hybrid mean retrieval | 415.732 | ms | 397 archived queries; graph/vector/scoring included | S004;S019;S040 |
| LongMemEval | Iron Web historical / kuzu | completed fresh-corpus ingestion | 340.413 | s | 4612/4612 documents; complete | S042;S019;S043 |
| LongMemEval | Iron Web historical / kuzu | default_hybrid mean retrieval | 177.705 | ms | 100 archived queries; graph/vector/scoring included | S044;S019;S043 |
| LongMemEval | Iron Web historical / kuzu | reranked_hybrid mean retrieval | 1152.98 | ms | 100 archived queries; graph/vector/scoring included | S045;S019;S043 |
| LongMemEval | Iron Web historical / falkordb_before | FAILED cold ingestion: elapsed until failure | 11.158 | s | 56/4612 documents; failed | S046;S019;S047 |
| LongMemEval | Iron Web historical / falkordb_after | completed fresh-corpus ingestion | 4868.14 | s | 4612/4612 documents; complete | S050;S019;S051 |
| LongMemEval | Iron Web historical / falkordb_after | default_hybrid mean retrieval | 121.899 | ms | 100 archived queries; graph/vector/scoring included | S052;S019;S051 |
| LongMemEval | Iron Web historical / falkordb_after | reranked_hybrid mean retrieval | 2212.27 | ms | 100 archived queries; graph/vector/scoring included | S005;S019;S051 |
| LoCoMo | Mem0 managed v3 (top_200 artifact) | search p50 | 3055.2 | ms | public per-question search latency; public snapshot; hosted environment differs from local Iron Web | S014 |
| LoCoMo | Mem0 managed v3 (top_200 artifact) | search p95 | 6001.99 | ms | public per-question search latency; public snapshot; hosted environment differs from local Iron Web | S014 |
| LoCoMo | Mem0 managed v3 (top_50 artifact) | search p50 | 915.85 | ms | public per-question search latency; public snapshot; hosted environment differs from local Iron Web | S015 |
| LoCoMo | Mem0 managed v3 (top_50 artifact) | search p95 | 1210.72 | ms | public per-question search latency; public snapshot; hosted environment differs from local Iron Web | S015 |
| LoCoMo | Zep | search p50 | 513 | ms | search only; external reported latency; different protocol and environment | S009 |
| LoCoMo | Zep | search p95 | 778 | ms | search only; external reported latency; different protocol and environment | S009 |
| LoCoMo | Mem0 | search p50 | 148 | ms | search only; external reported latency; different protocol and environment | S009 |
| LoCoMo | Mem0 | search p95 | 200 | ms | search only; external reported latency; different protocol and environment | S009 |
| LoCoMo | Mem0g | search p50 | 476 | ms | search only; external reported latency; different protocol and environment | S009 |
| LoCoMo | Mem0g | search p95 | 657 | ms | search only; external reported latency; different protocol and environment | S009 |
| LongMemEval | MemPalace raw | project-expected COMPLETE benchmark wall time (approx.) | 300 | s | 500-question run; Apple Silicon estimate, not per-query latency or isolated ingestion | S016 |
| LoCoMo | MemPalace raw | project-expected COMPLETE benchmark wall time (approx.) | 120 | s | full 10-conversation run; Apple Silicon estimate, not per-query latency or isolated ingestion | S016 |
| DMR | Local Qwen reader / ironweb ranking | median reader request wall time | 249.736 | ms | 100 local responses; includes queueing, excludes retrieval; two concurrent slots | S056 |
| DMR | Local Qwen reader / baseline ranking | median reader request wall time | 243.014 | ms | 100 local responses; includes queueing, excludes retrieval; two concurrent slots | S056 |
| LoCoMo | Local Qwen reader / ironweb ranking | median reader request wall time | 318.108 | ms | 328 local responses; includes queueing, excludes retrieval; two concurrent slots | S056 |
| LoCoMo | Local Qwen reader / baseline ranking | median reader request wall time | 337.674 | ms | 328 local responses; includes queueing, excludes retrieval; two concurrent slots | S056 |
| LongMemEval | Local Qwen reader / ironweb ranking | median reader request wall time | 208.677 | ms | 100 local responses; includes queueing, excludes retrieval; two concurrent slots | S056 |
| LongMemEval | Local Qwen reader / baseline ranking | median reader request wall time | 272.982 | ms | 100 local responses; includes queueing, excludes retrieval; two concurrent slots | S056 |

Timing boundaries and environments differ. A complete benchmark runtime estimate is neither query latency nor isolated ingestion time. The failed FalkorDB-before cold builds remain visible even though retrieval used prepared complete snapshots. The historical slash-separated query values described hybrid **without** reranking; reranked timings are shown separately.

## Published-snapshot discrepancies

| Benchmark | Condition | README headline (%) | Case-level artifact (%) | Artifact correct / n |
|---|---|---|---|---|
| LongMemEval | top_200 | 94.400 | 93.400 | 467/500 |
| LongMemEval | top_50 | 94.800 | 90.400 | 452/500 |
| LoCoMo | top_200 | 92.500 | 91.558 | 1410/1540 |
| LoCoMo | top_50 | 91.800 | 82.662 | 1273/1540 |

This discrepancy does not prove which release is superior or that an author is wrong: the README and dumps may describe different run snapshots. The main table uses the identifiable case-level artifact; the README claims are preserved here rather than silently selected.

## Coverage and evidence limits

- Zep is included through published QA and search-latency evidence only. Per your instruction, Graphiti is not substituted and Zep is not called remotely.
- Reviewed Zep/Mem0 sources do not report the requested retrieval triplets for each DMR/LoCoMo/LongMemEval combination. Those cells cannot be filled with valid numbers by copying QA accuracy.
- Reviewed primary sources do not establish Mem0 DMR QA or MemPalace DMR/LoCoMo QA under the requested protocols. The approximately 67.2% MemPalace QA quote in the critical analysis lacks an identified primary project run/reader and is excluded from the numeric QA comparison.
- Source families differ in dataset release, subset size, evidence unit, context budget, reader/judge, top-k, and hosted/local execution. No cross-study superiority claim follows.
- Mem0/MemPalace competitor packages were installed while local testing was being considered, but were not benchmarked after you chose online published results. No SDK score is claimed.
- The local reader experiment replays archived rankings. It does not demonstrate present-day end-to-end Iron Web lifecycle correctness or a full public-benchmark run.

## Sources

- **S001**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_reranked_hybrid_falkordb_after.jsonl` — retained artifact; local SHA-256 `2cea29a0b42a2548e4b74be14ece156663b5ae462f17ebcf81e1be09f6f81dca`.
- **S002**: `D:\Opencode_\reserchpaper\report\reranker_diagnosis_20261014\full_summary.json` — retained artifact; local SHA-256 `172e15297b191590eb6f2822f8c53c0c2d628ebfa0069fe2a76ba0281db3e319`.
- **S003**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\report.md` — historical run protocol report; local SHA-256 `1cb0886cec71e3ffc1b69c548032ddc5dfe6d5686392e4b890b82ca821ef7acd`.
- **S004**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_reranked_hybrid_falkordb_after.jsonl` — retained artifact; local SHA-256 `a293bc2675114a3a2191b828b29a12d9d02ea5d290f4bb08745f5b9f8be728cb`.
- **S005**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_reranked_hybrid_falkordb_after.jsonl` — retained artifact; local SHA-256 `b8479b65ad64831ff0aa351ff9c5746414db175108c8fc6a3cbf9ebf39227d58`.
- **S006**: [published source](https://arxiv.org/abs/2604.21284v1) — published-paper extract; local SHA-256 `02abc20c952504340b2932a27aeeaeb814626b4307001329b1c298993363b005`.
- **S007**: `D:\Opencode_\AI assistant\docs\benchmarks\verified-tables-20261026\local_qa_pairs.jsonl` — paired per-question QA correctness labels; local SHA-256 `bca92537cd4bba3cc0f8935be76189a849c03b9b1f4fbe2e2cbe48529d434c79`.
- **S008**: [published source](https://arxiv.org/abs/2501.13956v1) — published-paper extract; local SHA-256 `e4c4a282b6ec87115f8e84941704e57075647964a0f7e508ecf6f45939e02ae0`.
- **S009**: [published source](https://arxiv.org/abs/2504.19413v1) — published-paper extract; local SHA-256 `f3cff8c134b68167f4ab004bc5cfe151b7ff50368a550054a655498529200f98`.
- **S010**: `D:\Opencode_\AI assistant\docs\benchmarks\external-sources\20261026\source-lock.json` — retained artifact; local SHA-256 `627058c1924747ebd712f4f265b66a8846cff0b3e074f07398fc52d7b653efb7`.
- **S011**: [published source](https://github.com/mem0ai/memory-benchmarks/blob/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/results/platform/longmemeval_results.json) — official public per-question result file; local SHA-256 `58bd6d8934a54d8cd568ef481bbd3e37270c2c74a5d59713b661d4c3ddb332a1`.
- **S012**: `D:\Opencode_\AI assistant\docs\benchmarks\external-sources\20261026\mem0_memory_benchmarks_README.md` — official benchmark README; local SHA-256 `ed4ee055be417ca6896aab00b2ad62d4b3c67205ed32f496544803492faffae2`.
- **S013**: [published source](https://github.com/mem0ai/memory-benchmarks/blob/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/results/platform/longmemeval_top50_results.json) — official public per-question result file; local SHA-256 `8bbf06e4205dce1df9c2dff9a9ddf99074865ca40019e1c5a10f0d3a37b4275c`.
- **S014**: [published source](https://github.com/mem0ai/memory-benchmarks/blob/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/results/platform/locomo_results.json) — official public per-question result file; local SHA-256 `36338fa6c1ca38bcf9e3fc33a5cbc3b6e53bdc4bafaeeaee0947cf13b5527911`.
- **S015**: [published source](https://github.com/mem0ai/memory-benchmarks/blob/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/results/platform/locomo_top50_results.json) — official public per-question result file; local SHA-256 `b4bc12d41b9864aaac747a9b58d8609ba3a0d7780ea39857d5b87a83ef3dc45a`.
- **S016**: [published source](https://github.com/MemPalace/mempalace/blob/84582fb055a6429261f9c779da86c0561ec80adc/benchmarks/README.md) — official benchmark reproduction guide; expected output; local SHA-256 `11428e897c907da518d0f1bf5d52c8141868ed0acb833cd84ab4767d01528009`.
- **S017**: `D:\Opencode_\AI assistant\docs\benchmarks\external-sources\20261026\mempalace_longmemeval_bench.py.txt` — published metric definition; not executed; local SHA-256 `c4b4ba3da9e2d7e0e3f27bc93918877fe5f46e202be9ff98b1e90c7e0124628d`.
- **S018**: `D:\Opencode_\AI assistant\docs\benchmarks\external-sources\20261026\mempalace_locomo_bench.py.txt` — published metric definition; not executed; local SHA-256 `d22636e72d5cff747ef8f8267908f61d42c004e9103d1270981ea3aabf1c3a88`.
- **S019**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\verified_summary.json` — retained artifact; local SHA-256 `c75ee9aa493f4690aa7fba2b98774dd5fe8030e9b07cc496f2780b206684b5ca`.
- **S020**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_vector_kuzu.jsonl` — retained artifact; local SHA-256 `5e68fd2da40c1968b0cb8d70c48d5def040114e883258b8d4bb615e039520f0b`.
- **S021**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\dmr_kuzu.jsonl` — retained artifact; local SHA-256 `3a4f056962af9193a1d838c178c571b603fb0d7a8869c8f6bf6d5f6b6a449a6d`.
- **S022**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_default_hybrid_kuzu.jsonl` — retained artifact; local SHA-256 `a2389074292e26544741fe46c8f92af7accc2003f10ec2007b5fba7fcdb66977`.
- **S023**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_reranked_hybrid_kuzu.jsonl` — retained artifact; local SHA-256 `2fbc1fb19cebd695e1f57be23a3eb2a82ff5f822a81230ab60f236ed52fdf7ce`.
- **S024**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_vector_falkordb_before.jsonl` — retained artifact; local SHA-256 `07d8a9b28ba1b5b5f3bbe6747457f9fc9e886f0dfbffa96997cacac436bcb46f`.
- **S025**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\dmr_falkordb_before.jsonl` — retained artifact; local SHA-256 `81d3756ad226be49125657a6070c632384a0b386b86142e17519aa7903db43a5`.
- **S026**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_default_hybrid_falkordb_before.jsonl` — retained artifact; local SHA-256 `011705fa5dff7ab1a8679dd6da0bf34a3ff0850ab76090b33e5cf544c9ad69bc`.
- **S027**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_reranked_hybrid_falkordb_before.jsonl` — retained artifact; local SHA-256 `0c1f2296134ba7f17d206bc763a99a21093d2abea2fc20d45eab4d864e84390f`.
- **S028**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_vector_falkordb_after.jsonl` — retained artifact; local SHA-256 `8c0e4d586d4498a3ed67b67856e6bffc5a4022f10a6017119686c7c10ce1d703`.
- **S029**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\dmr_falkordb_after.jsonl` — retained artifact; local SHA-256 `dddaf3c1d8f28a634d9fc4ef495d1762fb524c9a349554eeab30187ae122e431`.
- **S030**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\dmr_default_hybrid_falkordb_after.jsonl` — retained artifact; local SHA-256 `e2cbff83619ea924adba4ee52eaa661cc5a051e6a00475ccde17787597bee3a9`.
- **S031**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_vector_kuzu.jsonl` — retained artifact; local SHA-256 `915f72c52c1a87229eaab2ab5c1e344ea830b77bbac2d5f37aada639561e2b60`.
- **S032**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\locomo_kuzu.jsonl` — retained artifact; local SHA-256 `96a64655b1709f82559ac6c950b7a0b2c344b6ab063058263343ccca47b46ad8`.
- **S033**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_default_hybrid_kuzu.jsonl` — retained artifact; local SHA-256 `0f32093081784679920f0c44d47a9fdf6ceb1e8eb4e75c53e7856df33553fdc3`.
- **S034**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_reranked_hybrid_kuzu.jsonl` — retained artifact; local SHA-256 `2a755f5dbfd9f085e6c197f94e6769d618abaef3c830580dbd9d8cfd5fe822b1`.
- **S035**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_vector_falkordb_before.jsonl` — retained artifact; local SHA-256 `90d9656ab4f65aba54a81abaaab60d66daf707a50fae7e47bcb1acc0e89fa037`.
- **S036**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\locomo_falkordb_before.jsonl` — retained artifact; local SHA-256 `77ac5ad0f9dbdb292ca8f56150747ed823c939ed55918e38ab4a12d2b806f338`.
- **S037**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_default_hybrid_falkordb_before.jsonl` — retained artifact; local SHA-256 `7c52a0af652ae69165bda330ba64b4eae564f7be678cda00068eb96ff9527adb`.
- **S038**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_reranked_hybrid_falkordb_before.jsonl` — retained artifact; local SHA-256 `37c33574da18aa5d6add38c9dd234861aedb0fd990250268f06eabb578994340`.
- **S039**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_vector_falkordb_after.jsonl` — retained artifact; local SHA-256 `30e8cb04417832bd4406612cd54f2ac475f45b8703276f6d036c195ecb42716b`.
- **S040**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\locomo_falkordb_after.jsonl` — retained artifact; local SHA-256 `6c980cad71fdd9a4ccf351dfb30b5d8145afbea6768f6066383242f6acbb5c95`.
- **S041**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\locomo_default_hybrid_falkordb_after.jsonl` — retained artifact; local SHA-256 `84d76717eb0da3f4f9f494ab5292adacfb7e55a5798ee986c2db90d3b07d5c65`.
- **S042**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_vector_kuzu.jsonl` — retained artifact; local SHA-256 `1ffe5a33ead0fdd385387ae5323d58fa88546b9ff4c34f28f3cbada83edaeee2`.
- **S043**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\longmemeval_kuzu.jsonl` — retained artifact; local SHA-256 `5fb66265d78dc5f959eaaf38f23f7bfd50fa209ee47946f1aec367a3918ae4f7`.
- **S044**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_default_hybrid_kuzu.jsonl` — retained artifact; local SHA-256 `5e8349e9540b0b44dfd2e6e145e1a1bdc5b672073e1eed9aa427ee311f03b68d`.
- **S045**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_reranked_hybrid_kuzu.jsonl` — retained artifact; local SHA-256 `74b9ea5a71fd166b2afcad2d18ed561aeaa36122da5588ee82dbdb78cc8d1e5d`.
- **S046**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_vector_falkordb_before.jsonl` — retained artifact; local SHA-256 `844e9095b79fe52e0b6b385634339e72c44e65c4379c12f88a62400b6757fff5`.
- **S047**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\longmemeval_falkordb_before.jsonl` — retained artifact; local SHA-256 `0fbf4d2837118fdd3c05160f0882f6017d836434ad08e04fbb615297ec6fbcca`.
- **S048**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_default_hybrid_falkordb_before.jsonl` — retained artifact; local SHA-256 `daa5b4815db78e89c736381f52d819c258823ce670ad95f5d4fdd99ae725b82b`.
- **S049**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_reranked_hybrid_falkordb_before.jsonl` — retained artifact; local SHA-256 `d35a97baca680ce8a3765b2e7d2cd6f2ef68c8fafc01c9b303508313add6845f`.
- **S050**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_vector_falkordb_after.jsonl` — retained artifact; local SHA-256 `7ecb4a2bd88710d369fa41e5313ed9f823b82dc6ffe2286a18e92ad02a115919`.
- **S051**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\ingestion\longmemeval_falkordb_after.jsonl` — retained artifact; local SHA-256 `ccb26a78c591272deac7fe52e1a1738b788dc5036ffe3d718b36ee604b8cdf9a`.
- **S052**: `D:\Opencode_\reserchpaper\report\full20_graph_analysis_20261013\raw\longmemeval_default_hybrid_falkordb_after.jsonl` — retained artifact; local SHA-256 `5a2ab666a7396f6600b6959516331606cd0327f0d245a61df754f0a791d73b1f`.
- **S053**: `D:\Opencode_\AI assistant\docs\benchmarks\verified-tables-20261026\local_qa_protocol.json` — new local reader protocol/runtime evidence; local SHA-256 `39fb24a75455932ef0744f57d833e07bc1ccf18fae1b7f1b450cf7c602918f9b`.
- **S054**: `D:\Opencode_\AI assistant\docs\benchmarks\verified-tables-20261026\reader_runtime_proof.json` — new local reader protocol/runtime evidence; local SHA-256 `e7d13872f6c785ef9a62d3a60911e6db94ad688947005c0cabfa6d14aed7359f`.
- **S055**: `D:\Opencode_\AI assistant\docs\benchmarks\verified-tables-20261026\local_qa_summary.json` — new local reader protocol/runtime evidence; local SHA-256 `8c7295097f548dab0ab33dba1492149be0a7936fc7ae519a0479ccef9e6d3955`.
- **S056**: `D:\Opencode_\AI assistant\docs\benchmarks\verified-tables-20261026\local_qa_predictions.jsonl` — actual locally generated answers and timings; local SHA-256 `b84a8660acc349a7c5065c4fdfa9b8e8410d9fdecf308063aaff3d598e699d84`.