# Proposed evaluation protocol

Status: proposal prepared 24 October 2026. No experiments described here have been executed for this research dossier. The protocol is intended to become the Methods section after the user supplies the paper format and approves the research scope.

## 1. Benchmark suite

| Dataset or test | Role | Metrics | Important constraint |
|---|---|---|---|
| LoCoMo, pinned ten-conversation release | Conversation recall, temporal reasoning and multi-hop QA | Answer F1; fixed-prompt judged correctness; per-category scores; evidence recall | Report exact category inclusion and question counts |
| LongMemEval_S V1 | Main long-context and knowledge-update evaluation | Official answer evaluation plus separate retrieval metrics | Pin original versus cleaned histories; do not mix them |
| LongMemEval_M V1 | Optional scale stress test | Same QA and retrieval measures; indexing time, disk and RAM | Full-context baseline may exceed model capacity; record that explicitly |
| Deep Memory Retrieval | Secondary compatibility/sanity check | Judged QA correctness | Short, near-saturated task in the supplied Zep study |
| LongMemEval-V2 | Optional later evaluation for agent experience | Official QA/context-gathering protocol and resource costs | Different task and data; requires a dedicated adapter |
| Iron Web lifecycle suite | Targeted evaluation of the claimed contribution | State correctness, stale use, citation validity and dependent-work behavior | Clearly label as author-created, not a public leaderboard |

Primary sources: [LoCoMo repository](https://github.com/snap-research/locomo), [LongMemEval V1 repository](https://github.com/xiaowu0162/LongMemEval), [MemGPT](https://arxiv.org/abs/2310.08560), [LongMemEval-V2](https://arxiv.org/abs/2605.12493).

The original LoCoMo release and later ten-conversation subset differ. The original project page gives different average length statistics from the Mem0 paper's evaluated release. Count messages and tokens directly from the frozen artifact instead of adopting a convenient headline average. The V1 LongMemEval repository announces cleaned histories in September 2025. Reproducing Zep's January 2025 result requires an older data snapshot; a new result on cleaned data must be labelled separately.

LoCoMo's four-category result should be comparable to Mem0's exclusion policy. Evaluate adversarial/unanswerable cases separately if used, with an explicit rubric rather than silently including them in the same mean. For LongMemEval, include abstention in end-to-end QA; retrieval metrics need an answerable subset with available evidence labels. The official V1 retrieval documentation excludes 30 abstention instances; validate the count against the exact pinned file.

## 2. Baselines

Start with the same answer model and prompt across these internal baselines:

1. No external memory: question and normal system prompt only.
2. Full available history, whenever it fits the configured input budget.
3. BM25 on raw session/turn text.
4. Dense retrieval on retained raw text. This is the essential check against the MemPalace argument.
5. Hybrid lexical/dense retrieval on raw text, with the fusion method explicitly fixed.
6. Structured claims only.
7. Iron Web raw sources plus lifecycle-managed claims and bounded graph expansion.

Next add pinned external implementations for Mem0, its graph variant and Zep/Graphiti, with A-MEM or Hindsight if budget permits. A self-hosted Graphiti adapter is not automatically the same system as the historical hosted Zep service; name it accurately. A current Mem0 package is not automatically the supplied 2025 algorithm.

Separate two comparisons: a controlled mechanism comparison with matched backbones and budgets, and each system's recommended configuration. Do not combine them in one ranking. Published historical figures can appear in a contextual table, labelled as author-reported rather than reproduced.

Iron Web's default extraction is `none`. For end-to-end conversation evaluation, implement and record a frozen automated extraction policy or evaluate the raw-only configuration. Hand-written claims, predicates or graph edges derived from the answer key are privileged annotations. If useful for debugging the memory engine, put them in a separately labelled oracle-annotation experiment, never the main benchmark.

## 3. Data and execution controls

Freeze the dataset revision/hash, question IDs, excluded categories, tokenizer, system revision, dependency versions, embedding checkpoint, extraction and answer model IDs, judge model, prompts, sampling settings, context limits and random seeds. Keep source ingestion unaware of questions, answers and evidence labels. Evaluation code may use labels only after retrieval and answer generation.

Preserve speaker roles, timestamps, timezone interpretation, session boundaries and source IDs. Ingest chronologically. Isolate histories, subjects and scopes so unrelated benchmark instances cannot share memory. Do not reuse embeddings or summaries whose keys omit the source content, model revision or scope.

For final-state benchmarks, ingest all allowed history and then query. For online lifecycle experiments, ingest only events available at each query time. Declare index readiness and wait for asynchronous extraction/indexing according to a fixed rule, recording the wait and failures. These are different protocols and should have separate result groups.

Tune only on a development partition created before inspecting final errors. LoCoMo has only ten conversations: avoid randomly splitting questions from one conversation between tuning and test. Prefer held-out conversations and disclose the resulting small independent sample. If using the public benchmark strictly as a locked test, use separate synthetic development material. Do not claim an official train/dev/test split where one does not exist.

## 4. Retrieval and answer metrics

For a query q, let G(q) be its labelled evidence units and R_k(q) the deduplicated top-k retrieved units, mapped to the same granularity.

- **Hit@k / recall_any@k:** 1 if G intersects R_k, otherwise 0. Average over eligible queries. Label it explicitly; it is not evidence coverage.
- **Evidence Recall@k:** size of that intersection divided by size of G, averaged over eligible queries.
- **All-evidence success@k:** 1 only when every required labelled evidence unit is retrieved.
- **MRR@k:** reciprocal rank of the first relevant result, or 0 if absent. Report the cutoff.
- **NDCG@k:** discounted ranking quality under an explicitly defined relevance label; omit if reliable labels are unavailable.

Evaluate chunk-, turn-, claim- or session-level retrieval separately. A claim should map back to source evidence before scoring. Deduplicate multiple chunks from one session when computing session recall. Evidence annotations can be incomplete: a correct answer supported by an unlabelled equivalent passage needs adjudication rather than automatic dismissal.

For end-to-end QA, use the dataset's evaluation protocol, publish answer F1 where appropriate, and record judge model/prompt and generated answers. Audit a stratified subset with human reviewers, including incorrect, disputed, temporal and abstention examples; record disagreement. Judge variability is not the same uncertainty as sampling different benchmark histories.

Report per-category and overall scores. Distinguish micro-averaging across questions from macro-averaging across categories or conversations. Write both relative percentages and percentage-point differences unambiguously. Include failures and timeouts in the denominator under a declared policy.

## 5. Lifecycle experiments

Construct independent synthetic timelines with unambiguous expected states, multiple paraphrases and distractors. Separate development templates/entities from final tests. Have expected labels reviewed before execution.

| Condition | Expected behavior | Measure |
|---|---|---|
| Explicit correction | Current answer changes; erroneous earlier assertion remains traceable as corrected | Correct current state; stale-answer rate |
| Real change over time | Previous value remains valid for the earlier interval | Current and historical query accuracy |
| Unresolved equal-authority conflict | Dispute is surfaced, rather than a confident arbitrary answer | Dispute detection and false-answer rate |
| Repeated agent assertion | Repetition does not manufacture independent support | False promotion rate |
| Independent corroboration | Distinct evidence groups are retained and counted as configured | Group attribution correctness |
| Expired, retracted or missing information | It is not presented as a current supported value | State/abstention accuracy |
| Two users/spaces with the same predicate | Retrieval stays in the authorized scope | Leakage count and denominator |
| Correction after context assembly | The old proof/card is rejected or refreshed | Stale-context acceptance rate |
| Correction during dependent work | Completion checks detect invalidated requirements | Stale-completion acceptance rate |
| Source removal | Removed source and dependent projections follow the declared removal policy | Residual exposure by storage surface |
| Crash/retry | Receipts replay consistently without duplicate accepted facts | Recovery correctness and time |

Distinguish a correction of a mistaken assertion from a fact changing at a later time. "Where did the user live then?" and "What did the system believe then?" can require different answers. Any deletion guarantee must specify graph, vector, cache, journal and backup behavior; removal from a query view is not proof of complete erasure.

Scoping tests are correctness checks, not proof of secure tenant isolation. Prompt-injection resistance requires its own adversarial protocol if claimed. Source authority in the local API is supplied by trusted callers; document this boundary.

## 6. Ablations

The engine already exposes vector, graph, hybrid, no-rerank, no-graph and no-temporal retrieval modes. Verify their effective settings and code paths before experiments. The shipped configuration disables reranking, so a reranking ablation must explicitly enable it in the full comparator.

Additional useful ablations: lifecycle policy; independent-source grouping; fuzzy score versus a simple monotone score with the same inputs; raw source retention; card caching; and dependency revalidation. Change one mechanism at a time, preserving the reader budget and other settings. Safely isolate intentionally degraded variants from live user data.

## 7. Efficiency, uncertainty and artifacts

Match reader context budgets, not only top-k: five complete sessions can cost far more than five short claims. Publish accuracy versus context-token curves; suggested budget points of 1k, 2k, 4k and 8k are starting proposals, subject to the selected model. Record truncation and whether required evidence is dropped.

Measure ingestion/extraction time and tokens, embeddings, indexing, retrieval, reranking, assembly, answer generation and judge cost separately. Report retrieval and total p50/p95 latency with repeat counts, hardware, network location, warm/cold state, cache state and time to index readiness. Track peak RAM, disk growth and corpus size. Zero hosted write cost does not mean zero total cost.

Use paired confidence intervals for system differences. Bootstrap at the conversation/history level when questions share history, rather than treating all questions as independent. LoCoMo's ten conversations give limited cluster-level precision; disclose that. Repeat stochastic extraction/generation where needed, with fixed conditions and a declared run count. Model-judge run standard deviations do not replace dataset-level confidence intervals.

Each final run should retain a manifest, effective configuration, prompts, source-to-evidence mapping, retrieved ranks/scores, generated answers, per-question grades, timings, error logs and aggregate outputs. Include a revision for Iron Web and each baseline. Keep credentials and unrelated user data out of these artifacts.

The manuscript should have separate tables for reported literature, reproduced end-to-end QA, retrieval, lifecycle evaluation and efficiency. Until runs exist, Iron Web cells should say **not measured**, rather than contain predicted or borrowed values.
