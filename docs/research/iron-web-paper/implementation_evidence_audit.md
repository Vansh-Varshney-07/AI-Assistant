# Iron Web implementation and evidence audit

Audit date: 24 October 2026. Scope: the accessible project, retained validation artifacts, source code and tests. No application tests, benchmarks, inference requests, database reads or database mutations were executed. The original Word draft is unchanged.

## Decision supported by this audit

Iron Web has an implemented memory engine with explicit claim lifecycle behavior and separate context/work revalidation paths. The accessible evidence supports selected synthetic engineering behaviors, including failed earlier attempts. It does **not** establish that the complete architecture improves long-term memory reliability over a simpler baseline, or that graph expansion earns its cost.

The next paper should investigate reliability when evidence changes and the cost of achieving it. It should not treat the current component inventory as an established scientific contribution. The initial experimental condition should be an explicitly labelled **memory engine receiving structured claims**. General conversation ingestion is a separate condition whose extractor and routing must be evaluated.

Companion files: [benchmark inventory](benchmark_inventory.md), [experiment plan](research_experiment_plan.md). Machine-readable support: [audit manifest](audit-artifacts/audit_manifest.json), [file hashes](audit-artifacts/artifact_hashes.csv), [symbol locations](audit-artifacts/source_index.json), and [recomputed retained-run summaries](audit-artifacts/retained_run_summary.json).

## Evidence rules and source identity

The Git base is `dc96f3550767e30059293cdc639d900331ab385a`. The working tree contains pre-existing changes and untracked Wayfinder files; the base commit alone does not identify the inspected system. The hash manifest records 202 source/configuration/report/artifact files. The symbol index gives file-relative line ranges for code and tests without importing the application.

Use these evidence categories without substitution:

1. **Controlled Iron Web experiments:** protocol, configuration and raw outputs identify a completed comparison. None suitable for the central performance claim was found.
2. **Engineering validation:** unit/integration checks and selected live scenarios establish only tested behaviors. Reading a test establishes its intended assertion, not a fresh pass.
3. **External results:** observations reported by another study, under that study's conditions.
4. **Architectural analysis:** conclusions from source inspection and design reasoning.
5. **Proposed experiments:** not executed; no empirical outcome can be assigned.

Status definitions follow the supplied specification. “Implemented and verified” must name a narrow behavior and its execution evidence, not simply an existing test. Most major features below remain **implemented but incompletely validated** because broader effectiveness, current-version execution or realistic coverage is missing. “Historically exercised” is a qualification, not an assurance that the current checkout passes.

## Execution paths that must remain separate

**Direct engine:** `MemoryEngine.add/search/recall` coordinates graph/vector stores and claim lifecycle behavior. Its default extraction policy is `none`. Raw episode ingestion does not imply general fact extraction.

**Hosted workbench:** `WorkbenchAdapter._run_hosted` invokes a selected hosted interpreter, supplies a scoped field catalog, stores validated claims, performs retrieval and may route questions to exact field recall before answer generation. The retained Nemotron runs exercise this path. The semantic candidate list and the evidence actually used for generation can differ. A correct generated answer cannot therefore be credited automatically to hybrid semantic retrieval.

**Shared context and work service:** `SharedMemoryService` adds receipts, pending-event gates, context proofs, leases and dependent-work checks. `ContextAccess`, `ContextRuntime` and `SharedMemoryClient.generate_current` are part of this path. The direct workbench explicitly reports its SQLite shared-service journal as inactive; its live results do not validate these additional components.

**Wayfinder application:** the phase 0–2 application uses the engine through its own approval/proof boundary. Its retained report describes explicit memory operations. It does not establish that the later planned general chat, workflow, connector and multi-agent features are implemented. Its proof API must not be conflated with the shared service's context-token API.

## Implementation evidence matrix

Paths and symbols are repository-relative. Test names refer to assertions inspected in source. The linked inventory identifies execution artifacts and their limitations.

| Feature | Implementation location and executing path | Verification method | Evidence artifact | Status | Known limitations |
|---|---|---|---|---|---|
| Retained text in graph/vector stores | `memory/engine.py:add/get`; graph and Qdrant store methods | Readback, close/reopen and shared-ID assertions in `tests/test_storage_persistence.py`; dual-store readbacks in retained live scenarios | `docs/live-validation/live-test-evidence.json`, `live-test-records.json`; final Nemotron snapshots | Implemented and verified **for retained synthetic examples** | No corpus-wide completeness, power-loss guarantee or general relevance result |
| Source authority contract | `memory/lifecycle/models.py:SourceInput.authority/support_group`; `MemoryToolAdapter`; shared-service principals | `test_agent_tool_cannot_forge_confirmation_protection_or_user_deletion`; hosted authority tests inspect role/scope rejection | Test source; aggregate historical suite reports | Implemented but incompletely validated | Trusted local caller supplies provenance; a field declaring `origin=user` is not independent identity verification |
| Independent evidence grouping | `SourceInput.support_group`; lifecycle `views`; `lifecycle/fuzzy.py` | `test_event_retries_do_not_duplicate_or_manufacture_independent_support`, `test_agent_repetition_does_not_refresh_or_strengthen_a_user_fact` | Test source; historical reports lack named per-case execution logs here | Implemented but incompletely validated | No independently adjudicated source-independence dataset or false-promotion rate |
| Assertion and confirmation | `MemoryLifecycle.prepare/ingest/views/recall` | Accepted/unaccepted source scenarios, source snapshots and hosted write checks | Final Nemotron evidence and records; lifecycle tests | Implemented but incompletely validated | Structured fields and extraction quality are separate; synthetic successes do not establish general acceptance accuracy |
| Correction versus actual change | `ClaimInput.action`; lifecycle `ingest`, links, temporal state views | `test_accepted_change_retains_both_and_transfers_protection`, `test_correction_history_is_not_falsely_reported_as_past_truth`; final correction/stale-memory checks | `docs/nemotron-validation/nemotron-evidence.json` and records; earlier failures retained | Implemented but incompletely validated | Natural-language interpretation failed in earlier runs; no held-out controlled comparison |
| Retraction | `ClaimInput`; lifecycle `ingest`, `views`, `recall` | `test_retraction_retains_history_without_an_invented_replacement_value` | Test source plus aggregate historical reports | Implemented but incompletely validated | No standalone retained live retraction experiment located; removal and logical retraction are different operations |
| Unresolved conflicts | Lifecycle `views/recall`; hosted answer validator preserves dispute status and citation IDs | `test_unaccepted_conflict_preserves_protected_value_and_stops_answer`; final model conflict scenario; earlier extraction/citation failures | Four retained live evidence sets | Implemented but incompletely validated | Arbitrary semantic contradiction detection is not established; exact-ID validation is not entailment verification |
| Event time and known time | `MemoryLifecycle.active`, `group`, `views`, `recall(known_at=...)` | Known-time, correction-history and alias-history tests in `tests/test_memory_lifecycle.py` | Test source; aggregate reports | Implemented but incompletely validated | Exact recall exposes `known_at`; `MemoryEngine.search` does not expose the same argument. Define the route for each historical query |
| Scoped retrieval | Qdrant document filters; lifecycle exact scope; workbench space-owned IDs; shared-service tenant binding | `tests/test_memory_spaces.py`; `test_private_user_spaces_and_source_authority`; retained boundary scenarios | Final report claims 21 live checks; its detailed JSON is not present in the accessible project | Implemented but incompletely validated | Workbench spaces are local scopes, not tenant authentication. No broad adversarial isolation/security claim |
| Dense/vector retrieval | `engine.search(retrieval_mode='vector')` → `VectorRetriever.retrieve` | Search/trace tests and real cached-model smoke described in reports | Live raw-source retrieval events; test source | Implemented and verified **for selected retrieval examples** | This route still invokes lifecycle reconciliation; it is not an unmodified raw dense baseline |
| Graph expansion | `HybridRetriever._extract_entities/_graph_expansion`; graph store neighbor methods | `test_bounded_graph_expansion` asserts a bound; graph-related retrieval tests | Test source; no comparable graph-on/off output found | Implemented but incompletely validated | Bound assertion is not evidence of useful expansion, relevance improvement or scale efficiency |
| Temporal retrieval filtering | `create_search_filter`; `filter_by_time`; lifecycle reconciliation | Temporal point-in-time and stale-vector-hit tests | Test source; selected stale-memory scenarios | Implemented but incompletely validated | `auto` is not the same as `now`; `hybrid_no_temporal` leaves lifecycle reconciliation active |
| Hybrid ranking | `HybridRetriever.retrieve` and `HybridScorer.score_batch` | Candidate, trace and ranking assertions | Test source; selected live semantic ranks | Implemented but incompletely validated | Default hybrid gathers a larger candidate pool than vector mode; defaults are a confounded ablation |
| Neural reranking | Optional engine/reranker path; configured `BAAI/bge-reranker-base` | Fixture reranker by default; optional neural/provider tests | Configuration and tests | Implemented but incompletely validated | Disabled in inspected default and first live run; no retained same-budget neural reranking ablation |
| Fuzzy reliability score | `memory/lifecycle/fuzzy.py:score_memory` | Monotonicity/direction assertions; explicit `calibrated_probability=False` | Test source | Implemented but incompletely validated | No predictive calibration or advantage over a simpler score is established; eligibility is a separate hard rule |
| Token-bounded context | `ContextRuntime.compile/assemble`; `TokenBudget.require/prompt`; `ContextPolicy` | Capacity tests use a deliberately small WordLevel tokenizer, not an actual benchmark reader tokenizer | `tests/test_context_cache.py`, `test_context_assembly.py` and configuration tests | Implemented but incompletely validated | Needs a pinned consuming tokenizer/chat template; policy token caps are not measured token savings |
| Cached-context invalidation | Shared-service invalidation → `ContextAccess.purge`; source/event/runtime stamps; proof `validate` checks expiry and stamp | `test_warm_hit_pending_change_and_accepted_replacement`, `test_external_graph_change_also_revokes_context`, future-boundary tests | Test source; no retained complete hosted context experiment | Implemented but incompletely validated | Direct workbench live runs do not exercise it. Payload-byte budget is not a bound on process RAM |
| Revalidation after generation | `SharedMemoryClient.generate_current` validates proof after callback, with bounded rebuilds | `test_http_client_discards_response_generated_during_a_change` injects an intervening update and expects a second generation | Targeted test source; aggregate historical reports | Implemented but incompletely validated | Callback is synthetic; no independently retained named execution here. Retried generation must have no external side effects |
| Dependent-work invalidation | Lifecycle `invalidate_work` traverses `USES` then `DEPENDS_ON`; marks validation stale; preserves completed record history | `test_only_affected_work_becomes_stale_and_handoff_carries_versions`, new-rule and completed-work regressions | Test source and aggregate reports | Implemented but incompletely validated | This is an executing traversal, not only a dependency field. No measured stale-work acceptance rate across held-out scenarios |
| Completion and lease fencing | Shared `complete_work` checks role, lease, readiness; lifecycle `complete_work` calls `handoff`; `handoff` rechecks requirements/prerequisites | `test_new_rule_blocks_existing_work_and_completion`, recursive expiry and concurrent-owner tests | Test source; shared-service historical suite descriptions | Implemented but incompletely validated | Validates recorded memory requirements, not arbitrary unrecorded dependencies or external action atomicity |
| Compensation and replay | `memory/storage.py:coordinated_write`; shared journal receipts and orphan repair | Lost-publication-response rollback test; killed-process replay test | Test source; historical reports; retained recovery metadata | Implemented but incompletely validated | Compensation is not a transaction spanning three stores. Historical database recovery is relevant counterevidence to a broad durability claim |
| Cold backup and restore | `memory/shared/snapshot.py`; Wayfinder backup/restore wrapper | Stopped-owner/fresh-target tests; report of deletion-aware restore | Test source; phase 0–2 report; referenced detailed smoke JSON unavailable here | Implemented but incompletely validated | No live hot-backup guarantee, no all-surfaces erasure guarantee, no encryption proof |
| Hosted extraction and citation checking | `HostedClaimInterpreter`; `ValidatedCompletion`; `HostedEvidenceAnswerer`; scoped field routing | Model-output boundary fixtures and retained successful/failed real calls | `docs/live-validation`, all three Nemotron folders | Implemented but incompletely validated | Quote-substring checks do not prove semantic entailment. Defaults and error behavior changed between historical runs |
| General conversational context adapter | Current `ContextRequest` requires `trip_id`; task types are travel-oriented | Contract source inspection | No public benchmark adapter found | Proposed but not implemented **as a general conversational benchmark integration** | Do not imply the existing travel contract directly evaluates arbitrary LoCoMo/LME questions |
| Complete autonomous companion/workflow research system | Broader planning documents; phase 0–2 UI explicitly limits available features | Compare code/report to plans | Wayfinder phase report and planning manifests | Partially implemented | Later workflows/plugins/model-chat features are not evidence for this paper's memory claims |

## Detailed dependent-work conclusion

The specific disputed claim has substantive implementation support. On claim changes, lifecycle ingestion can call `invalidate_work`; it traverses direct claim users and transitive dependents. At completion, shared-service readiness/lease checks and lifecycle `handoff` reevaluate present requirements. Separate regressions exercise new requirements, changes after completion, scope differences and prerequisite expiry. Context proofs also include a stamp that is checked after generation by the shared client.

However, the available live workbench runs bypass that shared context/work path, and named test-execution XML is not available in the accessible project. The defensible wording is: **implemented with targeted regression assertions and historical aggregate validation, but not yet established as an end-to-end reliability improvement.** It must not become “all dependent work is always safe” or “stale actions are prevented.”

## Ablation problems found in the current code

1. `MemoryEngine.search` constructs `VectorRetriever(..., lifecycle=self.lifecycle)`. The retriever can replace an old vector hit with eligible claim evidence and add reliability scoring. Label this **vector retrieval with lifecycle reconciliation**, not raw-text dense retrieval.
2. `hybrid_no_temporal` disables one retriever configuration flag. The hybrid pipeline still sends managed records through lifecycle reconciliation, and default `temporal_mode='auto'` differs from explicit current-time filtering. It is not a complete temporal-off condition.
3. Default vector retrieval requests k candidates, whereas hybrid normally requests at least 100 before expansion/filtering. Equal final k does not equal equal candidate opportunity or reader budget.
4. `hybrid_no_graph` removes candidate graph expansion, but lifecycle reconciliation still consults structured graph claims. It does not remove the graph store or all graph-dependent reasoning.
5. Hosted field routing can supply exact recall evidence independently of the displayed semantic ranking. A reader comparison must log which route actually supplied its evidence.
6. Reranking is off in the default config. Comparing default hybrid to `hybrid_no_rerank` may compare identical behavior unless the effective full condition enables reranking.

These are experiment-design constraints, not evidence that any component is beneficial or harmful. No implementation changes were made to “fix” them during this audit.

## Configuration and infrastructure boundary

The inspected default is CPU execution, extraction `none`, BGE-small embeddings with 384 dimensions, Qdrant plus FalkorDB, 100 vector candidates, two graph hops, 50 graph nodes and disabled reranking. Shared-service defaults are constructed separately from `config.yaml`; the factory passes extraction `none`. Engine overrides include the graph connection and `USE_GPU`. No retained resolved manifest ties every old run to every effective setting.

Installed package metadata in the previously used project environment includes FastEmbed 0.8.0, Qdrant client 1.18.0, FalkorDB client 1.7.1, tokenizers 0.23.3 and OpenAI client 1.60.0. Both CPU and GPU ONNX Runtime distributions are present; this does not establish which provider loaded in a historical process. Cache directory names indicate a small BGE ONNX asset and additional BGE-m3/cross-encoder assets, not independently verified complete checkpoints. No model was loaded.

The supplied feedback identifies an RTX 4050 with 6 GB VRAM. A fresh hardware query was denied, so that remains user-reported. Initial decisive tests should use CPU embeddings and no generative model. Historical NVIDIA API availability does not establish current quota or authorize a new run.

The newer test launcher creates a disposable database with AOF/snapshots disabled. Existing documentation warns against running the old default tests against the persistent instance. Retained recovery records show a prior repair applied to database volumes; neither restart counters nor passing storage checks prove freedom from persistence failures. No test launcher, database client or repair command was invoked here.

## Claims that can and cannot survive a rewrite

| Claim | Evidence-supported treatment |
|---|---|
| Explicit lifecycle/source contracts are implemented | Describe the inspected path and its trusted-caller boundary |
| Selected synthetic current-state/correction/conflict examples worked | Cite identifiable retained events; preserve earlier failures and small sample scope |
| Dependent-work revalidation is merely aspirational | Incorrect: an executing path exists; realistic effectiveness remains incomplete |
| Graph expansion improves reliability | Hypothesis; no qualifying controlled comparison found |
| Fuzzy score expresses probability of truth | Unsupported and contradicted by its own implementation description |
| Token limits establish lower token cost | Unsupported without matched reader measurements |
| All historical tests passed | False: failures and partial/mismatched artifacts are retained |
| 204 or 218 test passes measure memory accuracy | Unsupported; aggregate engineering checks are not public QA results |
| Three-store crash atomicity is guaranteed | Unsupported; code explicitly uses compensation/replay |
| Iron Web outperforms external systems | Unsupported with the current accessible evidence |

## Original manuscript check

The original DOCX hash is `a47c2819f40da69d200cfe027763785ed0487cb70972f8f252517de30ea0c33f`. It contains three tables, one embedded diagram and two occurrences of the Results & Discussion heading. The prior nine-page QA artifact exists. The feedback's missing-image assertion is not confirmed for this file: the diagram is embedded. Formatting allegations should be checked against the actual revision, not repeated automatically.

The substantive criticism stands: the draft does not establish a controlled experimental argument, and its tables interleave literature context with an unmeasured proposed method. The rewrite should separate architecture, methods, eligible results, discussion and limitations. It should not force a numerical comparison where none exists.

## Limits of this audit

The inaccessible `.local/tests-relocation-20261024` subtree and unavailable referenced XML/JSON prevent a claim of complete independent reproduction. Old backup source fragments do not identify entire executable historical revisions. No private credentials were read, no active service was queried, and raw provider responses were not republished. The literature review here checks the seed papers and benchmark identity/license boundaries; a manuscript-wide bibliographic and claim audit remains a later staged deliverable.
