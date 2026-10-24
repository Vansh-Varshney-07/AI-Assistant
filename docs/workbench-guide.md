# Memory Testing Workbench

> Updated after live-model repairs: select an explicitly enabled Nemotron model for automatic extraction and generated answers. Start with `--nvidia --key-file 'D:\Opencode_\reserchpaper\.env'`. The model choices are Lightning and Ultra. [Current startup, repairs and live test procedure](nemotron-repairs.md). The evidence-only workflow below remains available without model calls. Earlier unsupported results describe that unconfigured mode, not the enabled Nemotron path.

## Start and stop

Use PowerShell. Reuse the existing Python 3.12 virtual environment; no package installation is needed on this machine.

```powershell
Set-Location 'D:\Opencode_\memory_system'
docker compose up -d --pull never falkordb
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\workbench_server.py
```

Open **http://127.0.0.1:3352**. Stop with the **Stop workbench** button, or **Ctrl+C** in that terminal. The server waits for active requests to finish and closes Qdrant. To stop the database too, run `docker compose stop falkordb`; restart with the same commands. Never use `down -v` for persistence testing. Only one process may own this Qdrant directory; stop this workbench before using the direct engine or another service against that path. The delivered instance was started in the background for you; use its Stop workbench button before starting your own foreground instance.

The workbench uses `config.yaml` and existing `FALKORDB_*` overrides, refuses remote FalkorDB hosts, and keeps the engine's legacy extraction_policy disabled. Optional --nvidia inference is a separate explicit adapter using the selected Nemotron model. Embedding-model loading stays offline. No credentials are displayed. If storage is unavailable it fails honestly; if the cached embedding model is missing, requests report failure without substituting embeddings. Port can be changed with `--port 3353`; an alternate existing engine configuration can be selected with `--config path` at the command line. There is no file selector in the UI.

## What a response means

**Evidence-only mode** displays the existing engine's actual evidence/answer-status packet or storage receipt and retrieved records. With an explicitly selected enabled Nemotron model, store operations extract validated, source-grounded claims, and query operations return generated answers with validated memory-ID citations. The model field router calls the existing recall API; it does not replace engine retrieval or lifecycle rules. See nemotron-repairs.md for the current workflow.

- **Retrieve only** calls `MemoryEngine.search`, writes nothing, and exposes scores, IDs and complete retrieval traces.
- **Store episode + retrieve first** calls search before `MemoryEngine.add`; the typed episode preserves the raw source text. Questions should usually use Retrieve only. The source is retained as an episode, not automatically converted into a preference or accepted correction.
- **Store explicit claims + retrieve first** accepts the existing `ClaimInput` schema. You manually declare meaning; the engine performs its existing conflict/correction logic. This tests structured ingestion, not automatic extraction.
- **Recall a declared field** calls `MemoryEngine.recall` for the Subject, Predicate and test namespace. Its supported/disputed/missing status and evidence come from the graph. Explicit predicates avoid relying on the retained domain vocabulary.

Use namespace `iron_web_manual` for all eight scenarios. A second namespace makes a separate test run without erasing anything. Namespace is stored in source metadata and added to explicit claim scopes. Retrieval is constrained to that namespace's stored IDs; this is a local testing convention, not access control. Graph-wide alias actions and references are intentionally unavailable. Source records whose vector copy is missing appear under **All configured backend records**, since their namespace metadata may be unavailable.

Fresh conversation clears only this tab's history, prompt and selected retrieval evidence. It preserves all long-term records. Conversation history is never sent to the engine, so cross-interaction evidence can be checked independently. Reloading the tab also starts a new UI session. Changing the namespace changes retrieval scope, not stored data.

Inspect a record to see Qdrant payload/point ID, graph observations and links, sources, claim IDs and current lifecycle views. `timestamp` is source creation time. There is no source-level update timestamp or status column: update time is Unavailable; displayed statuses belong to claims. Related entities may have update timestamps, but these are not substituted for source timestamps. Claim fuzzy scores are not retrieval scores. Search in the inventory is a substring filter; it is separate from semantic engine retrieval.

Diagnostics report engine method calls, actual returned IDs, measured retrieval/request duration, dual-store readback, and observed claim-state changes. An empty namespace makes `search` return early; diagnostics explicitly say retrieval did not run beyond that call. Query results shown for a store operation predate the write. A failed write may include rollback status; inspect the stores before resubmitting. Evidence can be saved with **Save request evidence**; downloads contain private prompts and records, but no runtime credentials.

## Testing workflow

For every step, record the prompt, mode, namespace, returned IDs, source readback, claim state, retrieval trace and timing in `workbench-results.csv`. Use **Inspect record** after writing, save request evidence, then use **Fresh conversation** before every cross-interaction question. Do not mark Pass on the expected text alone. Unsupported refers to an absent capability; Inconclusive refers to an unrun scenario or insufficient evidence.

Run each scenario first using raw episodes and retrieval. This measures the present free-text behavior. Optional explicit claims below let you test the already-supported lifecycle contract separately. Label those results **structured/manual**, so they are never mistaken for automatic prompt interpretation. Leave the confirmation checkbox off unless you intend to attest the submitted source as a user assertion. Corrections require it.

### 1. Basic memory creation

Store as two separate episodes:

1. “My current project is Iron Web, a long-term memory system for AI agents. I want to validate its storage and retrieval behavior before building further features.”
2. “I am testing whether Iron Web can remember project information across separate interactions.”

Inspect the exact retained text, source and memory IDs. Count duplicate/redundant sources. Distinct source events are generally retained even if their claims support the same value; source retention is not automatic deduplication. Do not run destructive maintenance just to make duplicates disappear.

Optional structured/manual test: declare `project_name: "Iron Web"` and `validation_goal: "storage and retrieval behavior"`, both subject `manual-user`, kind `fact`. These are manual declarations, not extracted facts.

### 2. Retrieval across interactions

Start a fresh conversation and Retrieve only:

“Which project am I working on, and what am I currently trying to validate?”

Inspect actual IDs from Test 1 and retrieval latency, plus irrelevant hits. There is no conversation context to explain a match. In the structured/manual variant use Recall twice, with predicates `project_name` and `validation_goal`. A natural-language assistant answer is Unsupported; evidence retrieval can be assessed independently.

### 3. Preference memory

Store episode:

“When working on Iron Web, I prefer to test one component at a time and inspect actual stored records before moving to the next phase.”

Fresh conversation, Retrieve only:

“What is my preferred approach for testing Iron Web?”

Check storage, independent retrieval and duplication. For a semantic preference claim, manually declare predicate `testing_preference`, kind `preference`, value `"Test one component at a time and inspect actual stored records before moving to the next phase"`. Use Recall for that predicate. Raw text alone does not create a preference classification with extraction disabled.

### 4. Correction and supersession

1. “For this test, the active project label is Memory Alpha.”
2. “Correction: the active project label is Memory Beta. Memory Alpha is no longer the correct label.”
3. Fresh conversation: “What is the current project label?”

Raw episode mode preserves both statements; automatic correction extraction is Unsupported. Observe retrieval without assuming it establishes authority.

To validate the existing correction contract, submit prompt 1 using Store explicit claims with:

```json
[{"subject":"manual-user","predicate":"project_label","value":"Memory Alpha","kind":"fact","action":"assert"}]
```

Check the user-confirmation box if you intend it as an accepted user claim. Inspect and copy its **claim_id**. Submit prompt 2 with confirmation and this JSON, replacing the target placeholder with that actual ID:

```json
[{"subject":"manual-user","predicate":"project_label","value":"Memory Beta","kind":"fact","action":"correct","targets":["COPY_ACTUAL_CLAIM_ID"],"reason":"The user corrected the active test label."}]
```

Use Recall on prompt 3 with Subject `manual-user`, Predicate `project_label`. Check `answer_status`, value, memory ID and evidence path. The old source remains immutable; its claim should show the engine's actual `corrected` state and replacement link. For a change over time instead of a correction, use existing action `supersede` and inspect `superseded`. Do not conflate these semantics.

### 5. Conflicting information

1. “My test workspace is named Workspace North.”
2. “My test workspace is named Workspace South.”
3. Fresh conversation: “What is the current test workspace name?”

Inspect both source records and their timestamps. For structured/manual validation use two confirmed `assert` claims, predicate `workspace_name`, values `"Workspace North"` and `"Workspace South"`. Recall that predicate and check for the actual `disputed` status, both pieces of evidence and warnings. A later assertion is not automatically a confirmed supersession.

### 6. Persistence after restart

Store:

“For persistence testing, the verification phrase is copper-orchid-731.”

Inspect the source ID and both backend presence fields. Save evidence, stop with Ctrl+C, optionally stop FalkorDB with Compose `stop`, then restart with the startup commands. Choose the same namespace. With a fresh conversation Retrieve only:

“What is the verification phrase for the persistence test?”

Verify the same durable record and exact phrase, not a remembered UI message. Optional explicit predicate: `persistence_phrase`, value `"copper-orchid-731"`. Use Recall for an exact structured value. Record whether the database container was also stopped.

### 7. Stale-memory behavior

1. “The next test review is scheduled for 15 November 2026.”
2. “The test review has been rescheduled to 22 November 2026. Use the new date instead.”
3. Fresh conversation: “When is the next test review?”

Inspect both records and their states. Raw date parsing/rescheduling is Unsupported with extraction disabled. For structured/manual validation assert `next_review`, value `"2026-11-15"`, then submit a confirmed `supersede` claim, same field/scope, value `"2026-11-22"`, old claim ID in `targets`, and an explicit reason. Recall the field and compare with semantic search. The value of a review date is not itself the validity interval of the claim. Optional temporal fields `valid_from`, `valid_until`, and `effective_at` accept Unix seconds; declare them explicitly if testing validity windows rather than replacement.

### 8. Retrieval precision

Store three episodes separately:

- “The memory backend test uses a blue notebook.”
- “The interface test uses a green notebook.”
- “The retrieval test uses an orange notebook.”

Fresh conversation, Retrieve only:

“Which notebook is used for the retrieval test?”

Inspect rank, actual source IDs and irrelevant hits. Compare Top K 1 and 5. Do not interpret Top K as a relevance threshold: the existing algorithm may return unrelated candidates. Record whether the orange source ranks first. A generative answer remains Unsupported. Optional structured predicates `backend_notebook`, `interface_notebook`, `retrieval_notebook` test declared-field precision separately.

## Results and limits

The eight user scenarios are intentionally not auto-submitted into the configured manual store. The CSV starts Inconclusive/unrun; use actual saved IDs and evidence when filling it. Automatic extraction, natural-language conversation and end-to-end generated answers are Unsupported in this package. Structured lifecycle tests and storage tests can still pass on their own evidence.

`workbench-validation.md` records automated checks, runtime smoke evidence and their limits. Automated fixtures use their own `test_` graphs and temporary Qdrant paths. They are not proof of neural relevance. A separately selected neural test uses the real cached BGE model and isolated storage. No extraction, ranking, database schema, embedding model or existing orchestration code is changed.

Inventory is a full scan intended for local validation; large stores can be slow. It includes attributable graph-only sources and reports unowned observation IDs, but does not turn arbitrary entities into fabricated memories. The direct-engine path has no SQLite receipt/replay queue, matching the existing direct API. Use the existing shared service for its queue semantics; this workbench does not claim to validate that deployment path. Source copies are read back, not guaranteed crash-atomic. Namespace boundaries are not tenant authentication. The workbench is local-only and makes no production security claim.

## Revert

Stop the workbench, then remove only the newly added `workbench_server.py`, `memory/workbench.py`, `workbench/`, `tests/test_workbench.py`, and `docs/workbench-*` files plus the appended workbench README section. Keep `data/`, `config.yaml`, the Docker volume and existing source files. This reverts the interface without erasing test records. No deletion or maintenance route is exposed by the UI.
