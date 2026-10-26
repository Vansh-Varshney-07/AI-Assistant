# Iron Web benchmark and validation inventory

Audit date: 24 October 2026. This inventory describes accessible retained evidence, not new executions. Application databases were not opened. See [implementation audit](implementation_evidence_audit.md) for code-path boundaries and [experiment plan](research_experiment_plan.md) for the next decisions.

## Main result of the inventory

No executed LoCoMo, LongMemEval, matched-baseline lifecycle study or component-ablation experiment was found in the accessible project. Existing evidence consists of engineering tests, small live scenarios, operational recovery records, plans and copied external-paper results. There is enough evidence to investigate specific implemented behaviors and failures; there is no defensible comparative performance conclusion yet.

The inventory is complete for the accessible records described below, not for inaccessible directories or artifacts mentioned in reports but absent from this project. In particular, `.local/tests-relocation-20261024` could not be traversed. Referenced execution XML, a real-embedding smoke JSON and detailed space-validation JSON were not found in the accessible project. They may exist in another chat's artifact archive; absence here does not prove that the executions did not occur.

## Evidence status

- **A — Completed and reproducible:** protocol, source identity, inputs and outputs allow the stated result to be regenerated.
- **B — Completed but not fully reproducible:** a completed run is reported or recorded, but essential revision/configuration/execution evidence is missing.
- **C — Completed with incomplete or questionable methodology:** outputs exist, but cannot support the intended scientific comparison.
- **D — Partial or interrupted:** available outputs do not complete the declared evaluation.
- **E — Planned but not executed:** plans or unrun cases only.
- **F — Failed or invalid:** failed execution or an invalid result artifact; distinguish valid negative findings from invalid measurements.

A run can have a valid failure observation while lacking comparative validity. Where two labels apply, the table gives the primary execution status and qualifies scientific use separately. No retained controlled performance study qualifies as A. The audit's recomputation of recorded counts and selected medians is reproducible **artifact analysis**, not a newly executed memory experiment.

## Inventory and inclusion decisions

| ID | Record or run | Date | Retained observation | Status | Defensible use |
|---|---|---|---|---|---|
| V01 | Standalone extraction validation | 23 Oct 2026 | Report: 154 passing tests, 2 deselections | B | Engineering background; no neural QA estimate |
| V02 | Workbench extension regression | 23 Oct 2026 | Report: 164 passing tests, 3 deselections; a separate earlier selected neural test reports 1 pass | B | Implementation integration; counts overlap V01 |
| V03 | `live_1023_121339` | 23 Oct 2026 per report/run label | JSON and CSV agree: 24 checks, 11 Pass, 10 Fail, 3 Unsupported; 47 events; 21 record snapshots | B; C as a comparative benchmark | Preserve successes and failures as a small engineering case study; no single “memory accuracy” percentage |
| V04 | `nm_1023_124524` before-schema folder | 23 Oct 2026 per report/run label | JSON and CSV agree: 18 checks, 13 Pass, 5 Fail; 42 events; 25 snapshots | B; C as causal pre/post evidence | Relevant negative extraction/routing/citation observations; different repairs are confounded |
| V05 | `nm_1023_125245` schema-rejected JSON | 23 Oct 2026 per run label | JSON has 8 Lightning checks: 2 Pass, 6 Fail; 18 events. No Ultra completion in this artifact | D, with recorded failures | Report partial schema/provider-path failures; never call it an 18-check completed run |
| V05-X | Schema-rejected folder's CSV/report/snapshots | Historical mixed folder | CSV has 18 rows and is byte-identical to V04 CSV; report names V04's run. Snapshots likewise concern the earlier set | F **as an attribution of V05 results** | Exclude the stale summary from numerical reporting; preserve it and document the mismatch |
| V06 | `nm_1023_125909` final Nemotron run | 23 Oct 2026 per report/run label | JSON and CSV agree: 18 checks, all Pass; 42 events; 26 snapshots; nine checks per model | B; C for general accuracy or architecture superiority | Narrow positive engineering observation; repeated selected scenarios after repair, not held-out public evaluation |
| V07 | Nemotron-era regression suite | 23 Oct 2026 | Report: 187 passes, 3 deselections, 128.07 s | B | Historical aggregate regression record; no named execution log available here |
| V08 | `spaces_1023_133934` | 23 Oct 2026 per report/run label | Report enumerates 21 passing live space checks across four model-derived records and restart checks | B | Report-only isolation/persistence evidence; detailed `memory-spaces-live-evidence.json` not found |
| V09 | Memory-space regression suite | 23 Oct 2026 | Report: 204 passes, 3 deselections, 136.66 s; 17 new boundary tests | B | Engineering context; do not sum with V07/V10 or treat as QA questions |
| V10 | Wayfinder phase 0–2 regression | 24 Oct 2026 | Report: 218 passes, 3 deselections, 154.74 s; disposable persistence-disabled database | B | Newer implementation validation; referenced XML absent here |
| V11 | Startup/memory focused rerun | 24 Oct 2026 | Report: 13 passing checks in 16.27 s following cleanup change | B | Subset/rerun, not 13 additional independent cases |
| V12 | Phase 0–2 real BGE smoke | 24 Oct 2026 | Report describes real CPU BGE retrieval and cold restore | B | Report-only integration example; detailed JSON absent here |
| V13 | Recovery `20261024-111732-2bb556` | ID plus metadata | Backup metadata for one database; `copies=[]`, `originals_modified=false` | D | Partial operational preparation; not a completed recovery evaluation |
| V14 | Recovery `20261024-111839-df443c` plus verification | Explicit applied timestamp in JSON | Metadata records two backups, copy repairs, application to two database instances and healthy restart/stability snapshots | B | Operational history and limitation; not a controlled recovery rate or measured recovery cost |
| V15 | Hermes API/tool smoke | Explicit timestamp in JSON, 24 Oct 2026 UTC | Stored HTTP/marker booleans, including unauthenticated rejection | B; irrelevant to primary memory comparison | Infrastructure appendix if needed; does not demonstrate Iron Web lifecycle correctness |
| V16 | Workbench manual checklist | Historical document | 8 cases remain Inconclusive; no actual results entered | E | Unrun plan; do not relabel using later runs without case-level linkage |
| V17 | Companion acceptance/signoff plan | Planning files | 69 cases and 19 phase rows all Not run | E | Planning material; synthetic fitness fixtures are inputs, not executions |
| V18 | Wayfinder acceptance/signoff tracker | 24 Oct working tree | 49 acceptance rows: 13 automated verified/manual pending, 36 Not run; 3 implemented phase signoffs, 9 Not run | Mixed engineering report and E | Do not imply manual acceptance or sum with regression counts |
| V19 | Public memory benchmarks and ablations | Research plans | No input dataset, adapter or Iron Web output found for LoCoMo/LME; research result CSVs transcribe other studies | E | Experimental gap; no Iron Web score |
| V20 | Small storage/latency test definition | `tests/test_maintenance.py` | Source inserts 20 records, performs 3 queries and asserts mean time <200 ms under fixture-based suite defaults | Static test definition; no separate result artifact | No scale curve, p95, neural-quality or storage-byte result can be recovered from the assertion |

The full relevant CSV/JSON hashes and automatic count reconciliation are saved in [artifact hashes](audit-artifacts/artifact_hashes.csv) and [retained run summary](audit-artifacts/retained_run_summary.json). Duplicate artifacts are not additional runs. No failure has been removed because a later run passed.

## Protocol reconstruction

### V03 original mixed-path validation

Artifacts: `docs/live-validation/live-test-{results.csv,evidence.json,records.json,report.md,summary.md}` and `nvidia-parser-diagnostic.json`. Runner: `scripts/validate_workbench_live.py`, with appended diagnostics from `scripts/diagnose_nvidia_validation.py`.

The saved initial status identifies BGE-small embeddings, disabled reranking, extraction `none`, and an inactive shared-service SQLite journal on the direct engine path. This run mixes raw episodes, explicit structured claims and optional NVIDIA extraction/answer generation. The model is recorded at the evidence root as the configured Llama 3.2 vision model. These are separate conditions, not one end-to-end memory task.

The raw-source/current-session/restart examples and structured correction/conflict examples provide useful bounded observations. Automatic ingestion suffered parsing and field-consistency problems; several downstream failures share that upstream cause. Some generated answers were plausible but failed the exact-memory-ID citation criterion. Those checks are valid engineering negatives, not independent Bernoulli trials of conversational ability. The summary's measured search samples cannot be treated as a public benchmark latency guarantee.

There is one selected scenario set, not a train/dev/test split. The older source revision, resolved environment, reader budget, independent annotation, repeat policy, full cost accounting and reader/judge calibration are missing. The run ID gives month/day/time under its naming convention, not a complete immutable manifest. The associated report supplies the date.

### V04, V05 and V06 Nemotron reconstruction

Artifacts are the corresponding `docs/nemotron-validation*` evidence/results/records/report files. The current runner `scripts/validate_nemotron.py` creates fresh session/request IDs, sends confirmed source statements, uses `top_k=5`, and grades each named check as Pass only when all its stored check values are truthy. Stored JSON grades reconcile with their check dictionaries for the Nemotron evidence sets. This validates aggregation, not semantic correctness of every grading predicate.

V04 uses both named Nemotron models: Lightning has four passing and five failing named checks; Ultra has nine passing checks. Lightning failures concern cross-session answer/citation handling, preference classification, correction, supersession and precision. V05's actual JSON is a later, partial Lightning-only attempt with 2 passes and 6 failures; its copied CSV/report must not substitute for that evidence. V06 completes the same selected nine-check sequence per model with all checks passing.

The eight substantive scenarios plus replay check reuse a small synthetic design. Seven answer queries per model are captured in V06, not nine independent reader questions. Records contain source/claim state snapshots and actual memory IDs. Historical code backups preserve some earlier files, but not a full pinned environment for each run. Current source explains schema-constrained Nemotron output, bounded repair, source quotes, field catalogs, exact recall routing and citation validation; it cannot prove that every current setting was active in each earlier process.

Models: `nvidia/nemotron-3.5-lightning-30b-a3b` and `nvidia/nemotron-3-ultra-550b-a55b`, serving as both interpreter and answerer in their respective conditions. Embeddings are reported as real cached BGE-small; full resolved retrieval/reranker/provider state is not retained for every run. The current hosted wrapper uses temperature 0, JSON/schema contracts and up to two attempts, but no historical seed/model-weight revision is pinned. No independent judge or public dataset is involved.

No same-reader alternative architecture, equal-token raw retrieval comparator, frozen held-out split, confidence interval or total token/cost measurement is available. Repairs changed multiple layers. Consequently, an 18/18 final checklist must not be described as 100% long-term memory accuracy or causal proof that a particular repair improved generalization.

### Recovered timing definitions for V06

These are medians recalculated from retained event fields, not new calls. Exclude each model's one replayed extraction trace (`replayed=true`, zero inference time). The remaining 13 extraction traces per model include the wrapper's bounded attempts. Generation and query-adapter totals have seven samples per model.

| Model | Extraction inference median, ms, n=13 | Generation inference median, ms, n=7 | Query adapter total median, ms, n=7 |
|---|---:|---:|---:|
| Lightning | 1709.398 | 907.842 | 2129.818 |
| Ultra | 4776.200 | 6543.537 | 9600.997 |

The adapter's `diagnostics.total_ms` and the runner's `http_total_ms` are separate measurements. Do not add medians of stages to infer a median total. Token usage is not retained by the current hosted trace wrapper, so API cost cannot be independently regenerated from these files. This table describes a small, repaired synthetic run with no matched architecture baseline and no stable p95 estimate. It belongs in an engineering appendix, if used at all.

### Aggregate suites, space checks and operational history

The selected pytest defaults exclude `neural`, `dataset` and `gpu`. Autouse fixtures replace embeddings/reranking with deterministic functions and use isolated real stores. Some tests pass `use_gpu=True`, but that parameter alone does not establish neural CUDA execution under these fixtures. Token-budget tests include a toy WordLevel tokenizer; they verify accounting logic rather than fidelity to a chosen reader's tokenizer/chat template.

Suite totals 154, 164, 187, 204 and 218 overlap and concern evolving checkouts. The later phase report is more recent than the 204-test count emphasized in the old draft, but still lacks accessible referenced XML. The 17 boundary and 13 startup subsets are not extra independent samples. A pass count is neither a QA denominator nor an uncertainty estimate.

V14 records historical database repair rather than an abstract failure-injection exercise. The report explicitly says originals were modified then, and later verification records stable graph-count hashes across restarts. This audit did not perform that operation. These records demonstrate an operational incident/recovery history, not semantic preservation of all records, universal restart safety or cross-store crash atomicity. Backup archive digests stated in the old report were not newly verified against every archive.

## Missing metadata across the historical runs

| Required field | What is recoverable | What remains missing |
|---|---|---|
| Experiment identity/date | Run names, folders, report dates; some explicit UTC timestamps | Full per-event execution timestamps and complete immutable manifests |
| Code revision | Current Git base, current file hashes and partial older source backups | Full executed revision for each old run |
| Dataset/version/split | Exact synthetic prompts in retained events; planned public dataset names | A public dataset artifact/hash or independently frozen held-out synthetic split |
| Counts/runs | CSV/JSON row counts, model IDs, event counts and snapshots for four sets | Independent replication units; full repeated-run policy |
| Reader/extractor/embedding/reranker | Named hosted models; BGE in reports; current configurations | Weight revisions, actual provider state and resolved per-run settings |
| Retrieval/context | `top_k=5` in current Nemotron runner and retained request bodies | Matched candidate pool and context-token budgets; full effective override capture |
| Prompts/scoring | Retained requests/responses and grade dictionaries; current scripts | Versioned evaluator for each old run, independent correctness adjudication |
| Baselines | Some raw/typed conditions in V03 | A controlled equal-evidence/equal-reader comparator |
| Failures | Failed checks and invalid/partial artifacts retained | Independent attribution of failure causes and repair effects |
| Cost/resources | Some component and HTTP timings, record counts, report environments | Total token usage, billed cost, peak RAM/VRAM, storage growth, index build cost and robust scale curves |
| Reproduction | Current runners and recorded outputs | Live provider identity stability, historical full environment, missing XML/JSON and original held-out conditions |

## Predefined inclusion and exclusion policy

Primary analysis requires all of: relevance to an RQ, defensible execution/protocol, identifiable system/input/evaluator, retained per-case outputs, appropriate comparison controls, and an interpretable conclusion. Apply this to favorable, neutral and unfavorable outcomes alike. Keep failures in denominators according to the frozen protocol; maintain a separate availability metric rather than quietly dropping invalid responses.

| Result | Primary quantitative analysis | Other treatment and reason |
|---|---|---|
| V03 mixed-condition 24 checks | Excluded as an overall accuracy estimate | Retain engineering cases and failure dependencies |
| V04 13/18 and V06 18/18 | Excluded as architecture-performance comparison | Engineering history; selected repeated scenarios and confounded changes |
| V05 partial JSON negatives | Excluded from a completed-run score | Retain actual 8-check partial failure record |
| V05-X copied 18-row CSV/report | Excluded as invalid attribution | Preserve hash evidence; do not silently repair history |
| V08 21-check and V10 218-test reports | Excluded from general QA comparison | Clearly labelled report-only engineering support; retrieve missing raw files later |
| Empty-namespace timing | Excluded from retrieval latency | `retrieval_ran=false`; it measures a short-circuit/adapter path |
| V20 three-query fixture assertion | Excluded from scale or neural performance claims | Test definition only, no retained scale measurements |
| 46 overall and 68 category rows in earlier research CSVs | Excluded from Iron Web experimental outcomes | External literature transcriptions; retain source/model/metric groups |
| Manual cases not executed | Excluded | Plans, not zero scores and not failures |
| Future valid unfavorable ablations | Included under the same criteria as favorable results | Negative findings can justify simplifying the architecture |

## Public benchmark suitability and provenance

| Candidate | Actual relevance and limitations | Adapter and comparability | Primary-source license check | Decision |
|---|---|---|---|---|
| LoCoMo ten-conversation release | Recall/temporal/multi-hop QA; does not directly measure all claim-authority, retraction or stale-work guarantees; questions share conversations | Raw chronology/speakers/evidence IDs; separate extraction from supplied-claim conditions; preserve category policy and evaluator. No adapter or data file found locally | Official repository [LICENSE.txt](https://github.com/snap-research/locomo/blob/main/LICENSE.txt): CC BY-NC 4.0. Pin the exact artifact and its applicable notices | Secondary external-validity test after adapter/pilot; no directly comparable score yet |
| LongMemEval V1 cleaned S | More directly relevant to updates, time and abstention; still not a complete work-dependency benchmark | Preserve V1 tasks, all QA cases and timestamps; retrieval uses answerable labelled-evidence subset; pin cleaned/original revision. Hosted viewer errors do not prove raw JSON unusable | Repository code [MIT](https://github.com/xiaowu0162/LongMemEval/blob/main/LICENSE); [cleaned dataset card](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned) also labels MIT | Preferred public complement to controlled lifecycle experiments |
| Original LongMemEval V1 | Relevant for historical replication, with an older history snapshot | Current original [dataset page](https://huggingface.co/datasets/xiaowu0162/longmemeval) says deprecated in favor of cleaned histories; reproducing the 2025 Zep study requires the actual older artifact | Original card labels MIT; license identity does not establish dataset equivalence | Only for an explicitly separate historical replication |
| LongMemEval M | Same conversational abilities under a larger memory load | Higher indexing/context cost; fitting full history may be infeasible | Verify license/revision of the selected file, rather than infer from a different variant | Defer until smaller protocol is sound |
| LongMemEval-V2 | Agent environment experience, changing state and workflow knowledge; multimodal task distinct from V1 conversation memory | Needs a dedicated trajectory/screenshot/evidence adapter and different evaluation. No local adapter found | [Repository](https://github.com/xiaowu0162/LongMemEval-V2/blob/main/LICENSE) and [dataset card](https://huggingface.co/datasets/xiaowu0162/longmemeval-v2/blob/main/README.md): Apache 2.0 | Defer; too broad to be the initial decisive experiment |
| DMR | Short factual history retrieval, weak test of the central changing-evidence claim | Need the precise MSC-derived subset, construction and scoring from the originating work | Original subset/artifact/license not independently recovered in this audit | Exclude from primary evaluation; optional sanity check only |
| Controlled lifecycle timelines | Directly tests changes, conflicts, invalidation and recorded-work dependencies | Predetermine expected states, versioned generator and independent review; no public leaderboard equivalence | Author-created synthetic fixtures; release their generation/evaluation specification explicitly | Primary mechanism experiment, pending approval and execution |

These are recorded license labels from primary sources, not a claim that every third-party asset or future distribution is automatically covered. No datasets were downloaded and no task was silently changed. Scope, license, evaluator and revision must be pinned before a run.

## What can currently enter the paper

An honest present manuscript can describe the implementation and report a limited engineering case study, including earlier failures and missing evidence. Published results belong in a problem-oriented related-work comparison. It cannot yet contain a main table claiming that Iron Web improves reliability, beats a public benchmark baseline, or meets an acceptable latency target.

The decisive experiment set and the criteria for retaining or simplifying components are specified in the companion plan. The original Word draft has not been overwritten.
