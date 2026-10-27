# Iron Web: literature and benchmark research brief

Prepared 24 October 2026. Status: pre-manuscript research. Proposed ideas below are hypotheses, not experimental findings.

## 1. Research direction

The current implementation supports a paper about **evidence-backed long-term memory with explicit claim lifecycles and bounded context assembly**. A possible working title is *Iron Web: Evidence-Backed Temporal Memory and Bounded Context for LLM Agents*. Keep this provisional until the intended contribution, experiments and venue are settled.

The useful scientific question is whether explicit source authority, corrections, unresolved disagreements and historical validity improve memory use under a fixed context budget. A graph database plus a vector database is an architectural choice, not sufficient evidence of novelty. Tiered memory, retained episodes, temporal graphs and hybrid retrieval all have substantial prior art.

The strongest potential contribution is the interaction of lifecycle decisions with retrieval, cached context and dependent work. For example, when a user corrects a deadline, does the system retain the source history, retrieve the new value, invalidate previously assembled context and prevent work from completing against the stale value? These individual mechanisms exist in related research and databases; any novelty claim must concern a precisely defined mechanism or evaluated combination.

## 2. The three supplied papers

### S1. MemPalace critical analysis

Robin Dey and Panyanon Viradecha. *Spatial Metaphors for LLM Memory: A Critical Analysis of the MemPalace Architecture*. arXiv:2604.21284v1, 2026. [Versioned paper](https://arxiv.org/abs/2604.21284v1). Supplied PDF: 20 pages.

The paper decomposes a memory-palace metaphor into metadata organization, verbatim storage, vector search and supplementary components. It attributes much of the reported retrieval performance to retained text and default ChromaDB embeddings rather than the spatial naming scheme. It argues for low-overhead ingestion and a small initial memory footprint, while distinguishing organizational ergonomics from retrieval algorithms. The disclosed code analysis concerns v3.1.0; later changes through v3.3.1 were incorporated largely through documentation/changelogs (Appendix D, p.20).

This is useful motivation for a strong raw-text baseline and component ablations. Its interpretations are not universal findings: a benchmark score cannot establish that extraction is always inferior, and a local write path still consumes computation and storage even when it has no hosted API charge.

Important issues to resolve before citing its quantitative comparisons:

- Tables 4–5 (pp.9–10) report 96.6% retrieval `recall_any@5` on LongMemEval. This measures finding at least one labelled evidence session, not generating a correct answer or retrieving every necessary session.
- Table 6 (p.10) labels a cross-system comparison as R@5 throughout. At least some entries are answer scores in their original sources: Hindsight's 91.4% is described as accuracy in its [paper](https://arxiv.org/abs/2512.12818), and Mastra's 94.87% is presented as an answer-evaluation result with GPT-5-mini in its [research report](https://mastra.ai/research/observational-memory). Do not copy Table 6 as a comparable leaderboard.
- Section 8.2 (p.16) describes LongMemEval as testing retrieval rather than end-to-end utility. The benchmark authors explicitly provide retrieval and question-answering experiments. Cite the [original benchmark](https://arxiv.org/abs/2410.10813), rather than adopting that description.
- Table 5 assigns 88.9% LoCoMo R@10 to LLM reranking. The [project benchmark record](https://github.com/MemPalace/mempalace/blob/main/benchmarks/BENCHMARKS.md) identifies a hybrid v5 configuration without an LLM for this figure. The document also contains inconsistent historical statements; freeze the actual runner and result files before reproducing anything.
- The [maintainer response in issue #29](https://github.com/MemPalace/mempalace/issues/29#issuecomment-4215697566) distinguishes raw QA 66.8%, room QA 67.2% and AAAK QA 53.2%. Treat these as historical project-reported values pending configuration and sample verification, not a new independent result. Table 5's approximate 67.2% should not be silently assigned to the raw mode.

The numerical labels in the CSV preserve these caveats. Use the original result artifacts and configuration when extending these comparisons.

### S2. Mem0 and Mem0g

Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh and Deshraj Yadav. *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory*. arXiv:2504.19413v1, 2025. [Versioned paper](https://arxiv.org/abs/2504.19413v1). Supplied PDF: 23 pages.

The base method extracts candidate memories from a new exchange with a summary and recent-message context, then uses model-selected ADD, UPDATE, DELETE or NOOP operations against similar existing memories (pp.3–5). Mem0g adds entities, relationship triplets, graph retrieval and invalidation of conflicting relationships (pp.5–6). This is direct prior art for structured updates and combined semantic/relational memory.

The evaluation uses LoCoMo's ten-conversation release and excludes adversarial questions. Quality is measured with F1, BLEU-1 and a binary LLM judge; the authors report means and standard deviations over ten runs (p.7). Retrieved-context tokens are counted with `cl100k_base`; latency is divided into search and total response time. These do not by themselves account for all ingestion, extraction, summary refresh, embedding and storage costs.

Selected Table 2 results (p.11), all from the authors' experiment:

| System | Overall judge score | Context tokens | Total p50 / p95 seconds |
|---|---:|---:|---:|
| Full context | 72.90 ± 0.19% | 26,031 | 9.870 / 17.117 |
| RAG, 256-token chunks, k=2 | 60.97 ± 0.20% | 512 nominal chunk tokens | 0.802 / 1.907 |
| A-Mem | 48.38 ± 0.15% | 2,520 | 1.410 / 4.374 |
| LangMem | 58.10 ± 0.21% | 127 | 18.53 / 60.40 |
| Zep | 65.99 ± 0.16% | 3,911 | 1.292 / 2.926 |
| ChatGPT-memory baseline | 52.90 ± 0.14% | 4,437 | 0.466 / 0.889 |
| Mem0 | 66.88 ± 0.15% | 1,764 | 0.708 / 1.440 |
| Mem0g | 68.44 ± 0.17% | 3,616 | 1.091 / 2.590 |

The reported 26% gain compares Mem0 with the ChatGPT-memory baseline, not full context. From the printed table it is approximately 26.43% relative, or 13.98 percentage points. Full context has the highest overall judge score in this table. Mem0g gains 1.56 points over Mem0, approximately 2.33% relative. Mem0's printed p95 values imply about 91.59% lower response latency than full context; its retrieved context is about 93.22% smaller. Those ratios are derived from rounded table values and are not independently measured cost savings.

Table 1 (p.9) also matters: graph augmentation improves temporal and open-domain judge scores but decreases single-hop and multi-hop judge scores versus Mem0. Therefore, do not assume that adding graph traversal improves all multi-hop questions. Evaluate which queries benefit and what overhead it introduces.

Limitations: some baseline values were taken from earlier papers, the ChatGPT baseline uses a UI-specific extraction procedure, and provider state can change. The Mem0 authors note delayed improvement in Zep results after ingestion (p.14). Record index readiness in future comparisons. The 2025 paper must also be distinguished from subsequent Mem0 algorithms.

### S3. Zep / Graphiti

Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan and Daniel Chalef. *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*. arXiv:2501.13956v1, 2025. [Versioned paper](https://arxiv.org/abs/2501.13956v1). Supplied PDF: 12 pages.

Graphiti combines raw episodes, extracted entities/facts and community summaries. It retains raw episodes and connects semantic artifacts to their sources (pp.2–3). Thus, describing all extraction-based competitors as discarding the original record would misrepresent Zep. It distinguishes event validity from transaction/ingestion time and invalidates conflicting temporal edges. Search combines vector similarity, BM25 and graph traversal; reranking and context construction are separate stages (pp.4–5).

On Deep Memory Retrieval, Table 1 (p.6) reports 94.8% for Zep and 93.4% for MemGPT with GPT-4-turbo; the MemGPT number is imported from prior work. Full-conversation GPT-4-turbo achieves 94.4%. With GPT-4o-mini, Zep scores 98.2% and full conversation 98.0%. DMR is relatively short and close to saturation in these experiments, so it is a useful secondary check rather than the strongest main benchmark.

LongMemEval_S results from Table 2 (p.7):

| Reader | Full-context accuracy | Zep accuracy | Full / Zep latency | Full / Zep context |
|---|---:|---:|---:|---:|
| GPT-4o-mini | 55.4% | 63.8% | 31.3 / 3.20 s | ~115k / ~1.6k tokens |
| GPT-4o | 60.2% | 71.2% | 28.9 / 2.58 s | ~115k / ~1.6k tokens |

These are 8.4 and 11.0 percentage-point improvements. Relative gains from the printed numbers are approximately 15.16% and 18.27%; the paper's prose says 15.2% and 18.5%. Preserve the distinction between the prose claim and arithmetic from the rounded table. Its latency column is not labelled p95, and should not be compared as p95 against Mem0's table.

The assistant-session category declines for both readers, and the mini reader also declines on knowledge updates (Table 3). The paper reports an unsuccessful MemGPT adaptation to LongMemEval; that is not a measured zero accuracy or proof that every MemGPT configuration fails. The experimental description says top-20 retrieval generally, but DMR specifically says top-10. Dataset-specific configurations must be retained.

## 3. Recovered reference map

The full supplied reference lists are preserved in `cited-reference-lists.txt`. The curated bibliography identifies these particularly relevant branches. Additional-paper status means primary abstract/metadata screening unless explicitly stated otherwise; these are not all full-text reviews.

| Branch | References and primary links | Relevance |
|---|---|---|
| Memory hierarchy | [MemGPT](https://arxiv.org/abs/2310.08560) | Prior art for tiers and management of limited context |
| Personalization and decay | [MemoryBank](https://arxiv.org/abs/2305.10250) | Long-lived memory, reinforcement and forgetting |
| Linked evolving memory | [A-MEM](https://arxiv.org/abs/2502.12110) | Structured notes, linking and updates to earlier memories |
| Summaries with source lookup | [ReadAgent](https://arxiv.org/abs/2402.09727) | Gist memory with access to original passages |
| Hierarchical retrieval | [RAPTOR](https://arxiv.org/abs/2401.18059) | Retrieval across abstraction levels |
| Graph indexing | [GraphRAG](https://arxiv.org/abs/2404.16130), [LightRAG](https://arxiv.org/abs/2410.05779) | Communities, graph/vector integration and incremental indexing |
| Episodic plus semantic graph | [AriGraph](https://arxiv.org/abs/2407.04363) | Strong prior art against a broad dual-memory novelty claim |
| Evidence versus inference | [Hindsight](https://arxiv.org/abs/2512.12818) | Retain/recall/reflect; relevant to provenance and belief separation |
| Experience-derived learning | [Reflexion](https://arxiv.org/abs/2303.11366) | Persistent feedback; distinguish agent reflections from user-confirmed facts |
| Retrieval foundation | [RAG](https://arxiv.org/abs/2005.11401) | External non-parametric memory and retrieval-conditioned generation |
| Conversation evaluation | [LoCoMo](https://aclanthology.org/2024.acl-long.747/), [LongMemEval](https://arxiv.org/abs/2410.10813) | Cite the benchmark authors directly |

GraphRAG and AriGraph author lists changed between versions; the BibTeX records state which version was checked. Bibliographic entries copied from seed papers can be stale or inconsistent, so use primary metadata for the actual version cited.

For a current October 2026 paper, two additions deserve attention. [LongMemEval-V2](https://arxiv.org/abs/2605.12493) extends evaluation to environment experience, workflows and changing state; it is distinct from conversational LongMemEval V1. The [May 2026 Mem0 report](https://mem0.ai/blog/the-token-efficient-memory-algorithm-now-has-temporal-reasoning) describes a later temporal algorithm and reports configuration-dependent results. Neither belongs in a table labelled as the supplied 2025 Mem0 version. These are source-checked additions, not references that could have appeared in the earlier supplied papers.

## 4. Candidate hypotheses for Iron Web

| Question | Hypothesis to test | Relevant comparison |
|---|---|---|
| Does lifecycle handling help after updates? | Explicit correction and temporal eligibility reduce stale answers | Same retrieval and reader with lifecycle handling disabled |
| Do source distinctions matter? | Independent-source grouping reduces false corroboration from repeated agent text | Same events with all supporting sources treated as independent |
| Does graph expansion earn its cost? | Bounded graph traversal improves selected multi-evidence queries | Vector-only versus hybrid at the same reader budget |
| Do context cards help? | Cards and invalidation retain supported requirements at lower assembly cost | Equivalent uncached assembly and matched-budget direct evidence |
| Does retaining raw text help? | Source episodes recover details missed during extraction | Raw-only, claims-only and raw-plus-claims variants |
| Does dependent-work invalidation help? | Changes to required evidence prevent stale work completion | Identical workflow with and without dependency revalidation |

These hypotheses overlap with prior art and need precise baselines. A null result is still informative. Do not promise superiority before the measurements exist.

## 5. Claims ready for use, and claims still unavailable

Safe with qualification: Iron Web implements a local graph/vector memory engine, explicit source/claim contracts, scoped lifecycle operations and a bounded context runtime, as supported by the code evidence file. Prior local reports describe small scenario and isolation checks; they are historical engineering evidence.

Unavailable: a public-dataset accuracy number for Iron Web; a reproduced comparison against the three systems; evidence of state-of-the-art performance; universal superiority of graphs, raw storage or fuzzy scoring; a production security or crash-atomicity guarantee.

The dossier supports drafting background, related work, the implemented architecture and an experimental protocol now. The results and conclusion sections must wait for actual benchmark data, and the final manuscript structure will follow the format supplied by the user.
