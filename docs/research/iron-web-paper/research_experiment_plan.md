# Iron Web research questions and prioritized experiment plan

Prepared 24 October 2026, after the read-only implementation and retained-evidence audit. **No experiment below has been executed or approved for execution by this document.** The existing Word paper remains unchanged. This plan is the concrete review point requested in the supplied reconstruction specification.

## Research question and scope

**Central question:** Can explicit source-grounded temporal claim management improve memory reliability when information changes, conflicts or becomes invalid, and what retrieval, ingestion, context and storage costs accompany any improvement?

- **RQ1 — Reliability under changing information:** Does claim lifecycle management reduce wrong current/historical answers and invalid source attribution compared with a simpler event-based memory policy?
- **RQ2 — Architectural contribution:** Does graph candidate expansion improve valid-evidence selection beyond vector retrieval with the same lifecycle processing and candidate/context budgets?
- **RQ3 — Operational cost:** What incremental latency, storage, ingestion and context overhead accompanies each useful mechanism?

“Acceptable cost” requires a deployment target that has not yet been specified. Report an accuracy/latency/context trade-off until a threshold is agreed and fixed before final evaluation. Do not infer acceptability merely because a local demonstration feels responsive.

The initial condition is **a memory engine receiving explicit structured source/claim events**. It excludes the quality of natural-language extraction. A later conversation condition must freeze and evaluate an automated extractor. A hand-supplied or answer-derived claim condition is an oracle diagnostic, never a substitute for an end-to-end conversational result.

## Hypotheses and possible conclusions

| ID | Prospective hypothesis | What would disconfirm or limit it |
|---|---|---|
| H1 | Explicit lifecycle handling improves current/historical state correctness over a simple scoped event-log resolver | No consistent paired benefit, worse correctness, or a simpler temporal policy achieves the same reliability |
| H2 | Graph candidate expansion improves complete valid-evidence selection for selected relational questions | No improvement at matched budgets, improvement explained by extra candidates/tokens, or additional failures/latency |
| H3 | Context/work revalidation reduces unsafe stale acceptance while preserving valid work | No reduction, bypassed paths, or excessive false rejection of valid/unrelated work |
| H4 | Source-group distinctions reduce support/score inflation from repeated non-independent assertions | Grouping does not change relevant decisions, suppresses legitimate support, or simpler deduplication suffices |

H4 concerns support/scoring unless a specific decision rule actually consumes that support. Do not attribute hard source-authority protections to a fuzzy score or count a changed score as improved factual accuracy. The code's probability interpretation is explicitly unsupported.

All hypotheses remain open. Useful outcomes include limited benefits, no benefits, regressions, or insufficient evidence. A non-significant difference is not proof of equivalence; simplifying a component requires a predeclared practical margin and enough precision, or a clearly bounded engineering decision.

## Candidate contribution statement

The defensible present contribution is an implemented integration of source/claim contracts with temporal retrieval and guarded context/work use, plus a traceable evaluation design. Its empirical value is unestablished. The stronger prospective contribution would be evidence identifying **which lifecycle decisions improve reliability, which retrieval components are unnecessary, and their measured costs**.

Do not claim that graph/vector storage, retained episodes, temporal records or memory tiers are individually novel. Zep already retains episodes and temporal relationships; Mem0 describes updates and a graph variant; linked/episodic memory and bounded-context ideas have further prior art. A mechanism absent from a paper's evaluation is not thereby absent from its implementation.

## What the minimum decisive study must distinguish

1. Correct state reconstruction versus merely finding a similar passage.
2. Lifecycle-policy benefit versus better retrieval or privileged extraction annotations.
3. Graph candidate expansion versus a larger candidate pool or reader context.
4. Revalidation versus an always-abstain/always-block policy.
5. Real inference/retrieval cost versus replay, empty-store short circuits and unrelated provider latency.

The minimum **mechanism** study is E1 plus E2, with E3 using their same queries for cost and graph attribution. Public E4 is needed before generalizing to conversational QA. None should be selected because the old synthetic examples happened to pass.

## Prioritized experiment matrix

Numbers below are proposed starting allocations, not a power calculation or estimated accuracy. An independently reviewed development pilot must determine whether larger held-out samples are needed. Final entities/templates/histories must be separated from development before error inspection.

| Priority / ID | Specific question and hypothesis | Components and existing evidence | Missing evidence and baseline | Primary / secondary metrics | Confounds | Workload and cost estimate | Decision / paper placement |
|---|---|---|---|---|---|---|---|
| 0 / E0 | Can the actual executed conditions be identified and isolated? | Existing runners, configs, source index, 4 retained event sets; audit exposes mode confounds | Freeze a new source snapshot, evaluator and resolved config; verify adapters and disposal boundaries | Manifest completeness and condition equivalence / runtime availability | Old source backups are partial; current package names do not establish active providers | Offline protocol/harness preparation; zero API calls. Duration cannot be responsibly fixed before implementation | Blocks all causal claims. Methods/artifact statement; not an accuracy result |
| 1 / E1 | Do lifecycle rules improve changing-state reliability? H1/H4 | Source/claim engine, exact recall, known-time logic, typed regression cases and limited live checks | Predetermined held-out timelines; strong simple event-log policy versus Iron Web exact structured recall. Retrieval-mode comparisons belong in E3 | Exact state correctness / stale acceptance, source attribution, abstention, ingestion/retrieval cost | Representation privilege, target-ID annotations, wall-clock leakage, dependent probes, role/scope mismatch | Starting proposal: 12 families × 8 histories × 4 probes = 384 probes per state condition. Two conditions = 768 state probes. CPU-only initial stage; zero reader/judge API calls | Establish a narrow engine-contract finding or show a simpler policy suffices. Main mechanism results if valid |
| 2 / E2 | Does evidence revalidation reject stale use without unnecessary blocking? H3 | `ContextAccess`, shared client post-generation validation, lifecycle work graph, targeted regressions | Held-out scheduled changes and negative controls; revalidation on/off in isolated harness; always-block reference | Unsafe stale acceptance / false blocking, successful valid completions, rebuilds and added time | Workbench bypass, race scheduling, hidden dependency registration, different scopes | Proposal: 6 change families × 8 histories × 2 intervention schedules = 96 interventions, plus 32 valid controls per condition; 256 on/off attempts, plus an analytically labelled always-block reference. Deterministic callbacks; zero API calls | Retain guard, narrow guarantee, or redesign bypasses. Main results if this remains a contribution |
| 3 / E3 | Does graph expansion earn its incremental cost? H2/RQ3 | Existing bounded expansion and vector/hybrid code, no controlled ablation | Matched candidate pool and context with identical lifecycle and reranker; relational and single-fact cases; compare a simple score if relevant | Complete valid-evidence success / state correctness, p50/p95, graph visits, cache/ingest/storage costs | “No graph” still uses graph claims; defaults gather unequal candidates; warm caches | Reuse E1 probes. Optional scale pilot: 100/1,000/10,000 records, 30 queries × 4 warm repeats × 2 modes × 3 sizes = 720 retrieval probes, plus declared cold/warm-up observations. CPU; no generative API | Retain expansion for useful query classes, simplify it, or report inconclusive precision. Main ablation and cost analysis |
| 4 / E4 | Does an advantage survive conversation ingestion and a fixed reader? | Benchmark papers/docs; no local public adapter/output | Frozen automated extraction, raw dense and structured variants, fixed reader/judge, official scoring and no test-set tuning | Dataset QA correctness / retrieval coverage, stale answers, abstention, total pipeline tokens/cost | Extractor errors, judge bias, data revision, role/timestamp loss, evidence routing, different budgets | Full LongMemEval S: 500 questions × 3 conditions gives up to 1,500 answer calls and 1,500 judge calls if each is separately judged, plus extraction/repair. Financial and wall-time cost unknown until models/token estimates are approved | Needed for broad conversational conclusions. Main public results only after valid execution |
| 5 / E5 | Do retained operational paths recover under declared faults? | Compensation/replay tests; historical database incident and repair records | Isolated fault matrix with before/after integrity checks, replay/recovery times and source revision | State/integrity restoration / duplicates, downtime, recovery cost | Persistence-disabled disposable tests do not establish AOF replay safety | No live faults permitted. Separate temporary databases and bounded fault matrix; cost not estimated without a pilot | Appendix or separate systems study; not required to inflate the main memory argument |

No time or dollar amount is invented from the earlier 7-query medians or regression duration. An initial **development-only** calibration can have an agreed time/call budget; that budget is a stop condition, not a predicted runtime. Report partial completion honestly if it is reached.

## Baselines and ablation contract

### E1 engine comparisons

Use identical structured events, role/source metadata, scope, timestamps, explicit update targets and query inputs. The query must not reveal an answer unavailable to a comparator. Avoid a deliberately weak baseline that ignores all provided change markers.

- **Simple event-log resolver:** a compact append-only event representation with a documented scoped latest-eligible-value policy, validity/recorded-time handling, explicit retraction markers and stated conflict behavior. It is a serious competitor to graph complexity, not an undocumented “take newest text” strawman. Freeze precisely what it does for correction and conflict.
- **Iron Web vector retrieval with lifecycle:** name this condition accurately; it still consults structured claims. Keep ingestion and source policy identical to the full condition.
- **Iron Web hybrid with lifecycle:** change candidate expansion alone for the graph-attribution comparison. Hold candidate count, final reader/evidence budget, ranker settings and extraction constant.
- **Raw dense evidence retrieval:** use the same embedding checkpoint and raw source text/timestamps. Compare evidence-selection metrics. Do not assign it a state-answer accuracy if it has no defined state resolver or reader; use a fixed reader only in E4.

E1 compares the simple resolver with Iron Web's exact `recall` API. Vector and hybrid modes are E3 evidence-selection conditions; calling exact recall in both would bypass the component being ablated. E3 includes only probes expressible by `search` and its declared time semantics. In particular, past-belief queries requiring `known_at` cannot silently be treated as supported search tasks. Prespecify this task subset and its denominator before seeing results.

If a clean lifecycle-off condition is added, document the exact removed behavior and keep inputs/extraction fixed. Existing mode names do not implement that experiment automatically. A claims-only representation and an automatically extracted conversation condition are separate studies, not interchangeable ablations.

For provenance, isolate source grouping from actor authority and from source quality. For temporal handling, distinguish ordinary vector validity filters, managed-claim eligibility and `known_at` semantics. For graph retrieval, distinguish candidate expansion from graph-backed lifecycle lookups. For reranking, ensure the full condition actually enables the neural reranker, and verify identical candidate sets before it runs.

Consider fuzzy scoring only after a simple monotone score using the same inputs is defined. If two conditions are functionally equivalent or differ only in labels, do not run or report them as independent ablations.

## E1 dataset design and scoring unit

The proposed twelve families are correction of a mistaken assertion, genuine change over time, retraction, unresolved conflict, repeated agent assertions, independently sourced support, expiry, future validity, past belief after later correction, scope collisions, missing evidence, and late-arriving evidence. Generate varied entities, values, paraphrases and distractors. All comparisons receive the same structured meaning; this stage does not test language extraction.

For each held-out history, define four meaningful probes in advance. Record query time, known time, subject/scope, expected status, allowed value set and supporting source/event IDs. Include both current and historical probes where applicable. A correction of an earlier error must not turn that error into a historical truth. If evidence is legitimately disputed, a confident arbitrary value is incorrect. Gold labels require independent review or adjudication before any final outputs are inspected.

The independent unit is the history. Four probes sharing it are correlated. Eight histories per family is a pilot-sized starting proposal, not evidence of adequate power for small differences. Prespecify an expansion rule based on development variability and a practical effect/margin; do not expand only until a favorable p-value appears.

## E2 intervention design

Exercise the shared context/work path, not the direct workbench. Six intervention families should cover correction, genuine supersession, a new required rule, expiry, a disputed/retracted requirement and a changed prerequisite. Add 16 valid/no-change and 16 unrelated-scope controls per condition to detect overblocking. The stale-attempt denominator follows the predetermined expected state, not the total number of operations.

Register the claims and dependencies that a task actually uses. Intervene at controlled boundaries: after context construction and after deterministic generation but before result acceptance/completion. Record proof identity, evidence versions, event readiness, lease status, rejection reason and callback/rebuild count. The callback must only compute a synthetic response; it must not send messages, make purchases or repeat external side effects.

Compare on/off revalidation in a separate experimental harness. An always-block reference has zero unsafe acceptance but no useful availability; report it as a policy reference so a trivial fail-closed implementation cannot appear reliable merely by refusing everything. Separate known-time semantics from current-time completion safety.

## Metrics and denominators

Freeze scoring code, normalizations, averaging and failure policy before final execution. Retain per-case values rather than only a success total.

| Metric | Definition and denominator |
|---|---|
| Current-state correctness | Correct status **and** allowed current value set for each current-state probe; incorrect, missing, invalid and timed-out outputs count as failures. Report successes / all scheduled eligible current probes |
| Historical-state correctness | Exact expected status/value for the declared event time and known time; report past-truth and past-belief probes separately |
| Correction/retraction success | Correct required post-operation state and source linkage / all scheduled correction or retraction probes, including failed ingestion |
| Conflict handling | Correct dispute state and required competing evidence, without an arbitrary confident answer / all conflict probes; report false-dispute rate on compatible controls |
| Stale-answer or unsafe-acceptance rate | Accepted answers/work that use invalid/superseded evidence / all scheduled stale-evidence attempts; separately report available useful completions |
| False-block rate | Valid unchanged/unrelated-control attempts incorrectly rejected / all scheduled valid-control attempts |
| Scope violation rate | Outputs exposing an unauthorized-scope unit / all isolation probes; count severity and affected source IDs separately |
| Source attribution | Correct source alignment for emitted factual claims / all emitted factual claims, plus supported-answer coverage. Valid ID membership alone is a weaker metric. No emitted claims gives an undefined precision, not a perfect score |
| Appropriate uncertainty | Correct missing/disputed/abstention state / probes prespecified as requiring uncertainty; report false abstention on answerable probes separately |
| Hit@k | At least one gold relevant evidence unit in the deduplicated top-k / answerable queries with gold locations |
| Evidence Recall@k | Relevant retrieved gold units / gold units, averaged over eligible queries; map claims/chunks to the same source granularity |
| All-evidence success@k | Every required gold unit retrieved / eligible multi-evidence queries; finding one session does not satisfy it |
| Precision@k | Relevant retrieved units / actual deduplicated retrieved units; publish a separate fixed-k denominator if used. Empty retrieval is scored explicitly, not silently discarded |
| MRR@k / NDCG@k | Reciprocal first-relevant rank, zero if absent; or discounted ranking under declared relevance labels. Omit graded NDCG claims if trustworthy labels are unavailable |
| QA correctness / EM / F1 | Use the selected dataset's official protocol and normalization; keep binary judge correctness, exact match and token F1 separate |
| Latency | Stage-specific and complete-request wall times. p50 is the median; p95 uses a declared quantile rule, sample count and warm/cold state. Retain unsuccessful attempt durations |
| Tokens and cost | Actual embedding/extractor/repair/routing/reader/judge usage separately; reader input/output and chat framing included. Cached/replayed traces are distinct from paid calls |
| Storage/resources | Bytes and counts before/after indexing, raw text, vectors, graph, receipts and caches separately; peak process RAM where measurable. Cache payload quota is not process RSS |

A retrieval query without gold evidence locations has no Recall@k denominator; retain it in the relevant end-to-end abstention task. LongMemEval's official V1 retrieval documentation excludes its abstention examples, whereas QA evaluation retains them. Count the selected artifact's categories rather than assuming a copied question count.

For scientific comparison, report paired absolute differences and confidence intervals. Bootstrap at the history/conversation level and show both micro question scores and a prespecified family/category summary. With LoCoMo's small number of conversations, acknowledge weak cluster-level precision. Judge-run variability is not dataset uncertainty. Label exploratory subgroup/ablation analyses and account for multiple confirmatory tests if making significance claims.

## E3 operational controls

Use the same machine, database version, concurrency, embedding model, candidate count and evidence/token budget. Time embedding, vector search, graph traversal, lifecycle reconciliation, reranking, assembly and generation separately. Preserve a common retrieval-start and end-to-end boundary; do not compare a literature median with a local p95.

Test bounded claim groups as total corpus grows; otherwise a configured claim-count rejection can be mistaken for a search failure. If bounds are reached, report the rejection rather than silently increasing them. Maintain fixed distractor-generation and cache/warm-up policies. A 10,000 × 384 × 4-byte vector payload is about 15.36 MB before indexes, text, graph and runtime overhead; it is not a total RAM estimate.

Initial execution can use the cached small BGE model on CPU. The user-reported 6 GB GPU does not require fitting large readers locally. Historical NVIDIA models may be considered later under an explicit call/cost budget, but their current quota and provider behavior have not been checked. Do not load multiple large readers or download new models without including that work in the reviewed plan.

## Public benchmark adaptation and literature argument

The [inventory](benchmark_inventory.md) records the primary-source license checks and benchmark suitability. Prefer cleaned LongMemEval S as the public complement for updates/time/abstention. LoCoMo is a useful generalization check; it does not replace the direct lifecycle intervention experiment. Defer DMR saturation checks, LongMemEval M and multimodal V2 unless they resolve a remaining question.

Preserve chronology, both speaker roles, session evidence IDs and timestamp interpretation. Natural-language extraction must be frozen and answer-blind. Reuse the same extracted claims across structured mechanism conditions, while charging extraction to the appropriate end-to-end pipeline. Log whether generation uses semantic retrieval, exact field recall or a union. Supply the same reader and prompt with matched budgets.

Do not tune on a public pilot and then call those same questions held-out. Use separate synthetic development histories for schema/cost pilots. If any public cases are inspected during development, retain their IDs and declare the resulting nonstandard subset; never claim the original full-set protocol unchanged.

The related-work comparison should analyze these questions rather than list systems:

| Source | Relevant documented mechanism | What the cited evaluation establishes or leaves open |
|---|---|---|
| Mem0 2025 supplied v1, pp.3–6 and Tables 1–2 | Incremental extraction/update; graph variant and relationship invalidation | LoCoMo quality/cost under its protocol; not a direct test of Iron Web's exact authority or dependent-work contract |
| Zep supplied v1, pp.2–5 and Tables 1–3 | Retained episodes, temporal facts, provenance links and hybrid retrieval | DMR/LongMemEval results; its episode-source traversal is described but explicitly not directly examined in those experiments |
| MemPalace analysis supplied v1, pp.9–10 and disclosure | Raw-text baseline argument, code decomposition and recall metrics | Useful motivation for representation controls; its heterogeneous cross-system table cannot prove a uniform ranking |
| A-MEM, AriGraph and MemGPT | Linked/evolving memory, episodic-semantic representations and tiers | Prior art against broad novelty claims; full claim-level comparison requires the relevant original methods and experiments |
| Hindsight | Evidence, experience and belief distinctions in its primary abstract | Relevant conceptual overlap; do not infer unsupported feature absence from abstract screening |

The three seed identities were checked against primary records during this audit; their supplied PDFs and result pages are retained in the earlier dossier. The original 20-entry manuscript bibliography still needs a manuscript-wide version/venue/claim recheck before reconstruction. Earlier metadata screening is not full-text experimental verification. Use “not documented in this source” and “not evaluated here” where appropriate.

## Inclusion policy and artifact release

The same relevance, validity, comparability and interpretability filters apply regardless of outcome. Prospective freezing of this policy does not make the old runs preregistered. Keep a visible exclusion table with run ID, reason and recoverable observations. Exclude stale copied summaries, incomplete runs represented as complete, mismatched metrics, unequal reader conditions and annotation-privileged comparisons from the primary analysis; preserve their records.

For every approved run retain an experiment ID; code/content revision; resolved configuration; source/dataset/evaluator hashes; model/tokenizer identifiers; prompts; seeds; declared split; environment/provider information; per-case inputs/retrieval ranks/state/evidence outputs; timing/usage; failures; and aggregation script. Save withheld gold separately from ingestion. Include timestamps and explicit completion status. Provide sanitized shareable artifacts without credentials, unrelated private memories or machine-specific personal paths.

New runs must use fresh isolated runtime paths and a disposable database instance, not the existing persistent memory volume. Use the newer disposal-safe launcher pattern only after reviewing the actual harness. Do not reset, repair, restart or mutate production databases during a study. Recovery/fault work requires a separate approved plan.

## Proposed reconstructed paper outline

1. **Introduction:** changing evidence as the problem; RQ1–RQ3; bounded, evidence-supported contribution statement.
2. **Related Work:** update semantics, temporal/source handling, retrieval and cost; identify what each evaluation actually tests.
3. **System Architecture:** implemented event/claim contract, storage, eligibility, retrieval and guarded context/work paths; mark proposed adapters.
4. **Methodology:** condition definitions, histories/datasets, controls, metrics, uncertainty and artifact policy.
5. **Results:** only eligible completed experiments. Separate mechanism, public QA and engineering observations. If none are eligible, explicitly present only a limited engineering evidence audit.
6. **Discussion:** supported and unsupported hypotheses, failures, alternative explanations, costs and simplification decisions.
7. **Limitations and Threats to Validity:** structured-input boundary, synthetic distribution, annotation/judge uncertainty, few conversations, versions, providers, hardware and missing artifacts.
8. **Conclusion and Future Work:** what was established, what could be removed, and what remains unresolved.
9. **References:** only relevant sources, verified versions and accurate claim support; no target count imposed merely for appearance.

Keep an approximately 200-word abstract and three keywords if the requested editing format is retained. The expanded nine-page draft is an editing target, not a reason to pad missing results, repeat headings, enlarge claims or invent numbers. Rebuild the Word file as a separate revision only after this audit/plan has been reviewed; retain the original until final claim-to-evidence review.

## Review gates and immediate next step

The three initial artifacts now establish the accessible evidence, its failures and the experimental gaps. Before any implementation or execution, review: (1) the structured-input versus end-to-end claim boundary, (2) E1/E2 gold/denominator design, (3) exact matched baseline/ablation contracts, (4) isolated storage and maximum runtime/API budget, and (5) which missing historical artifacts can be recovered.

No positive performance conclusion is supported yet. If experiments remain unavailable, reconstruct an explicitly limited architecture/methodology manuscript. If an economical baseline matches the desired behavior, report that and simplify the architecture. If results are inconclusive, preserve that conclusion rather than recasting the component as a future success.
