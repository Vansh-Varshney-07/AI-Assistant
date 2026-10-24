# Live memory-system validation

Actual HTTP workbench requests, real cached BGE embeddings, FalkorDB and embedded Qdrant. No fixture embeddings or hardcoded answers.

Run: `live_1023_121339`. NVIDIA model: `meta/llama-3.2-11b-vision-instruct`.

11 passed; 10 failed checks; 3 unsupported default-path capabilities. Failures are reported rather than repaired by a new algorithm.

| Test | Path | Result |
|---|---|---|
| 1 Basic creation | raw episodes | Pass |
| 2 Across interactions | raw episodes | Pass |
| 3 Preference retrieval | raw episodes | Pass |
| 4 Automatic correction | raw episodes | Unsupported |
| 5 Automatic conflict interpretation | raw episodes | Unsupported |
| 6 Process restart persistence | raw episodes | Pass |
| 7 Automatic stale-date handling | raw episodes | Unsupported |
| 8 Retrieval precision | raw episodes | Pass |
| 4 Correction contract | explicit claims | Pass |
| 5 Conflict contract | explicit claims | Pass |
| 7 Supersession contract | explicit claims | Pass |
| NVIDIA label_new | hosted extraction + engine | Fail |
| NVIDIA review_new | hosted extraction + engine | Fail |
| NVIDIA conflict extraction | hosted extraction + engine | Fail |
| NVIDIA project and preference extraction | hosted extraction + engine | Fail |
| NVIDIA project_answer | retrieval-grounded generated answer | Fail |
| NVIDIA label_answer | retrieval-grounded generated answer | Fail |
| NVIDIA review_answer | retrieval-grounded generated answer | Fail |
| NVIDIA conflict_answer | retrieval-grounded generated answer | Fail |
| Project answer from stored episodes | NVIDIA generation + verified local evidence | Pass |
| Preference answer from stored episode | NVIDIA generation + verified local evidence | Pass |
| Corrected label answer from accepted claims | NVIDIA generation + verified local evidence | Fail |
| Rescheduled date answer from accepted claims | NVIDIA generation + verified local evidence | Pass |
| Conflict-aware answer from disputed claims | NVIDIA generation + verified local evidence | Fail |

## How to inspect and reproduce

Open http://127.0.0.1:3352 and enter one of these test namespaces. Choose All configured backend records to browse all run records. Inspect claim IDs, status, sources and graph observations.

- `live_1023_121339_nvidia`
- `live_1023_121339_precision`
- `live_1023_121339_raw`
- `live_1023_121339_typed`

Each query uses a fresh session UUID and sends no conversation history. Writes use confirmed user sources only in the explicit/NVIDIA claim paths. Raw episodes preserve the exact prompts without adding semantic claims. Correction targets in NVIDIA tests are selected by exact existing subject/predicate/scope; inconsistent model fields are not normalized or repaired.

The server was stopped via /api/stop and restarted with the same config/Qdrant path; the persistence check verifies both backend copies, the same memory ID and the exact phrase. FalkorDB itself remained running.

The NVIDIA key is read privately from the existing configuration and never saved in evidence. Only synthetic prompts and the synthetic test namespace retrieval results are sent to NVIDIA. Production configuration and memory algorithms remain unchanged; NVIDIA is used by this test runner, not silently enabled for the dashboard.

This run retained 21 labelled test records. Total stored records now: 21. No existing records were deleted.

## Checks and timings

### 1 Basic creation — Pass (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"both_writes_committed": true, "dual_store_readback": true, "exactly_two_sources": true, "ids_distinct": true}`

Retrieval milliseconds: `[0.015, 70.976]`; adapter request milliseconds: `[847.926, 436.993]`.

Two distinct source events are retained; no automatic source deduplication is claimed.

### 2 Across interactions — Pass (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"query_success": true, "retrieval_ran": true, "original_source_retrieved": true, "new_session": true}`

Retrieval milliseconds: `[75.867]`; adapter request milliseconds: `[156.934]`.

Every request has a new session ID; no conversation history is passed.

### 3 Preference retrieval — Pass (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"stored": true, "source_returned": true}`

Retrieval milliseconds: `[65.696, 64.147]`; adapter request milliseconds: `[466.749, 168.105]`.

Checks retrieval of preference text; automatic preference classification is not enabled.

### 4 Automatic correction — Unsupported (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"old_claim_ended": false}`

Retrieval milliseconds: `[48.271, 82.952, 65.133]`; adapter request milliseconds: `[505.713, 632.601, 237.371]`.

Capability test: raw text is stored as episodes. A failure means automatic correction interpretation is absent, not that persistence failed.

### 5 Automatic conflict interpretation — Unsupported (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"conflict_is_represented": false}`

Retrieval milliseconds: `[51.099, 69.951, 62.286]`; adapter request milliseconds: `[621.006, 781.157, 328.514]`.

Capability test: multiple unrelated episodes do not establish a same-field contradiction.

### 6 Process restart persistence — Pass (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"clean_stop_acknowledged": true, "same_record_in_both_stores": true, "same_id_retrieved": true, "exact_phrase": true}`

Retrieval milliseconds: `[56.377, 470.539]`; adapter request milliseconds: `[806.793, 771.506]`.

Actual server process stopped and restarted; FalkorDB container remained running.

### 7 Automatic stale-date handling — Unsupported (raw episodes)

Namespace: `live_1023_121339_raw`

Checks: `{"old_date_claim_ended": false}`

Retrieval milliseconds: `[53.063, 94.954, 79.467]`; adapter request milliseconds: `[812.282, 948.111, 422.895]`.

Raw natural-language rescheduling is not extracted into lifecycle actions by the default engine.

### 8 Retrieval precision — Pass (raw episodes)

Namespace: `live_1023_121339_precision`

Checks: `{"correct_source_ranked_first": true}`

Retrieval milliseconds: `[0.016, 53.782, 63.149, 61.929]`; adapter request milliseconds: `[958.258, 1025.916, 1263.645, 523.449]`.

Top K 5 returned 3 records. Full irrelevant-hit evidence is retained.

### 4 Correction contract — Pass (explicit claims)

Namespace: `live_1023_121339_typed`

Checks: `{"current_beta": true, "old_record_retained": true, "old_claim_corrected": true, "replacement_link": true}`

Retrieval milliseconds: `[0.062, 78.035, 21.253]`; adapter request milliseconds: `[1254.255, 1466.644, 595.821]`.

Manually declared claims; not an automatic extraction test.

### 5 Conflict contract — Pass (explicit claims)

Namespace: `live_1023_121339_typed`

Checks: `{"disputed": true, "both_claims_retained": true, "explicit_warning": true}`

Retrieval milliseconds: `[74.399, 84.516, 21.348]`; adapter request milliseconds: `[1547.485, 1574.022, 645.768]`.



### 7 Supersession contract — Pass (explicit claims)

Namespace: `live_1023_121339_typed`

Checks: `{"current_new_date": true, "old_claim_superseded": true}`

Retrieval milliseconds: `[87.853, 102.092, 19.328]`; adapter request milliseconds: `[1777.143, 1687.895, 731.567]`.



### NVIDIA label_new — Fail (hosted extraction + engine)

Namespace: `live_1023_121339_nvidia`

Checks: `{"original_stored": false, "change_stored": false, "existing_claim_ended": false}`

Retrieval milliseconds: `[None, None]`; adapter request milliseconds: `[None, None]`.

No predicate renaming or repair of model JSON; inspect extracted claims to explain failures.

### NVIDIA review_new — Fail (hosted extraction + engine)

Namespace: `live_1023_121339_nvidia`

Checks: `{"original_stored": false, "change_stored": false, "existing_claim_ended": false}`

Retrieval milliseconds: `[None, None]`; adapter request milliseconds: `[None, None]`.

No predicate renaming or repair of model JSON; inspect extracted claims to explain failures.

### NVIDIA conflict extraction — Fail (hosted extraction + engine)

Namespace: `live_1023_121339_nvidia`

Checks: `{"stored_both": true, "disputed_state": false}`

Retrieval milliseconds: `[0.017, 92.318]`; adapter request milliseconds: `[2052.75, 2151.405]`.



### NVIDIA project and preference extraction — Fail (hosted extraction + engine)

Namespace: `live_1023_121339_nvidia`

Checks: `{"project_stored": false, "preference_stored": false, "actual_preference_kind": false}`

Retrieval milliseconds: `[None, None]`; adapter request milliseconds: `[None, None]`.



### NVIDIA project_answer — Fail (retrieval-grounded generated answer)

Namespace: `live_1023_121339_nvidia`

Checks: `{"retrieval_ran": true, "expected_evidence_present": false, "cites_actual_returned_id": true, "expected_text_in_answer": false}`

Retrieval milliseconds: `[94.027]`; adapter request milliseconds: `[925.157]`.

String checks accompany actual storage/retrieval evidence; see exact answer and input IDs in JSON.

### NVIDIA label_answer — Fail (retrieval-grounded generated answer)

Namespace: `live_1023_121339_nvidia`

Checks: `{"retrieval_ran": true, "expected_evidence_present": false, "cites_actual_returned_id": false, "expected_text_in_answer": false}`

Retrieval milliseconds: `[80.471]`; adapter request milliseconds: `[949.219]`.

String checks accompany actual storage/retrieval evidence; see exact answer and input IDs in JSON.

### NVIDIA review_answer — Fail (retrieval-grounded generated answer)

Namespace: `live_1023_121339_nvidia`

Checks: `{"retrieval_ran": true, "expected_evidence_present": false, "cites_actual_returned_id": false, "expected_text_in_answer": false}`

Retrieval milliseconds: `[66.573]`; adapter request milliseconds: `[872.628]`.

String checks accompany actual storage/retrieval evidence; see exact answer and input IDs in JSON.

### NVIDIA conflict_answer — Fail (retrieval-grounded generated answer)

Namespace: `live_1023_121339_nvidia`

Checks: `{"retrieval_ran": true, "expected_evidence_present": false, "cites_actual_returned_id": true, "answer_acknowledges_conflict": true}`

Retrieval milliseconds: `[66.69]`; adapter request milliseconds: `[846.028]`.

String checks accompany actual storage/retrieval evidence; see exact answer and input IDs in JSON.

### Project answer from stored episodes — Pass (NVIDIA generation + verified local evidence)

Namespace: `live_1023_121339_raw`

Checks: `{"retrieval_succeeded": true, "exact_ids_in_answer": true, "expected_value_in_stored_retrieved_evidence": true, "expected_value_in_answer": true}`

Retrieval milliseconds: `[61.451]`; adapter request milliseconds: `[879.411]`.

This proves generation against actual engine evidence; it does not repair or validate NVIDIA automatic claim extraction.

### Preference answer from stored episode — Pass (NVIDIA generation + verified local evidence)

Namespace: `live_1023_121339_raw`

Checks: `{"retrieval_succeeded": true, "exact_ids_in_answer": true, "expected_value_in_stored_retrieved_evidence": true, "expected_value_in_answer": true}`

Retrieval milliseconds: `[62.197]`; adapter request milliseconds: `[943.347]`.

This proves generation against actual engine evidence; it does not repair or validate NVIDIA automatic claim extraction.

### Corrected label answer from accepted claims — Fail (NVIDIA generation + verified local evidence)

Namespace: `live_1023_121339_typed`

Checks: `{"retrieval_succeeded": true, "exact_ids_in_answer": false, "expected_value_in_stored_retrieved_evidence": true, "expected_value_in_answer": true}`

Retrieval milliseconds: `[30.679]`; adapter request milliseconds: `[912.889]`.

This proves generation against actual engine evidence; it does not repair or validate NVIDIA automatic claim extraction.

### Rescheduled date answer from accepted claims — Pass (NVIDIA generation + verified local evidence)

Namespace: `live_1023_121339_typed`

Checks: `{"retrieval_succeeded": true, "exact_ids_in_answer": true, "expected_value_in_stored_retrieved_evidence": true, "expected_value_in_answer": true}`

Retrieval milliseconds: `[21.128]`; adapter request milliseconds: `[882.691]`.

This proves generation against actual engine evidence; it does not repair or validate NVIDIA automatic claim extraction.

### Conflict-aware answer from disputed claims — Fail (NVIDIA generation + verified local evidence)

Namespace: `live_1023_121339_typed`

Checks: `{"retrieval_succeeded": true, "exact_ids_in_answer": false, "engine_reports_disputed": true, "answer_acknowledges_conflict": true, "both_values_in_evidence": true}`

Retrieval milliseconds: `[22.892]`; adapter request milliseconds: `[915.844]`.

This proves generation against actual engine evidence; it does not repair or validate NVIDIA automatic claim extraction.

## NVIDIA answers

Which project am I working on, and what am I currently trying to validate?

I can only provide information based on the provided evidence. 

There is no direct information about the project you are working on. However, there are two pieces of evidence about your workspaces:

1. You have a workspace named "Workspace North" (memory_id: wb_abe14246e7564d30951bb15585d6fc62).
2. You have another workspace named "Workspace South" (memory_id: wb_07bb4dcd6ea74ec8bb0c6b789024a3c9).

There is no information about what you are currently trying to validate.

NVIDIA inference: 5006.871 ms.

What is the current project label?

I am unable to verify the current project label.

NVIDIA inference: 2356.618 ms.

When is the next test review?

I'm unable to find any information about a test review in the provided evidence.

NVIDIA inference: 776.021 ms.

What is the current test workspace name?

I do not have enough information to answer this question. The provided evidence only contains two claims about the test workspace name, but they are contradictory. 

One claim (claim_3441df41fd240f4c70f2e103cbb48b4e) states that the test workspace name is "Workspace North" (memory_id: wb_abe14246e7564d30951bb15585d6fc62).

The other claim (claim_8d9c913be892f43c14f19c584f277c92) states that the test workspace name is "Workspace South" (memory_id: wb_07bb4dcd6ea74ec8bb0c6b789024a3c9).

Since the claims are contradictory, I cannot determine the current test workspace name.

NVIDIA inference: 8507.401 ms.

Which project am I working on, and what am I currently trying to validate?

Based on the provided evidence, I can see that you are working on a project called "Iron Web", which is a long-term memory system for AI agents. 

According to the conversation episode with claim_id "claim_d8826fc9e67dc198ff14c74e55e482d3" (memory_id "wb_f818580682a848c380317f3e36a174ed"), you are currently trying to validate the storage and retrieval behavior of Iron Web before building further features.

NVIDIA inference: 12491.858 ms.

What is my preferred approach for testing Iron Web?

Based on the provided evidence, your preferred approach for testing Iron Web is to test one component at a time and inspect actual stored records before moving to the next phase. This is stated in the conversation episode with the claim ID "claim_de17f341d337a680691b701bb0b308c7" and memory ID "wb_1d463a25ab834be9917cf1936488e20b".

NVIDIA inference: 5441.959 ms.

What is the current project label?

The current project label is Memory Beta.

NVIDIA inference: 1042.421 ms.

When is the next test review?

According to the evidence, the next test review is scheduled for 2026-11-22. This information is supported by a claim with ID "claim_312f58b53c9082cd98e89487055f2a4a" and memory ID "wb_a243e09313354dddb562339ad0c3578a".

NVIDIA inference: 3765.585 ms.

What is the current test workspace name?

I cannot determine the current test workspace name as the evidence is disputed. There are two conflicting claims: "Workspace North" (claim_ab735ee2f93d902f24f38ce32417358d) and "Workspace South" (claim_ff50f76e1df445b0b105d311dcd00a09).

NVIDIA inference: 3420.284 ms.

## Repeat this test run

From D:\Opencode_\memory_system with the workbench running:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_workbench_live.py --output .\docs\live-validation-next
```

A new namespace is created on every run. Existing test records are retained. Use --skip-nvidia for local-only checks. The runner performs a clean server restart during persistence testing. Full prompts, extracted claims, returned IDs, statuses and inference answers are in live-test-evidence.json; actual stored payloads are in live-test-records.json.

## Confirmed defects and evaluation limits

The configured NVIDIA HostedClaimInterpreter failed to parse five of eight original extraction calls. A captured repeat returned narrative and Python code instead of the required JSON envelope. The existing NIMExtractor helper can locate an embedded JSON object, but that alone does not establish that it is faithful extracted data; this helper was used only for diagnosis, with no parser changes or ingestion retries. See nvidia-parser-diagnostic.json.

Workspace North was extracted as test_workspace_name; Workspace South as has_workspace. Exact lifecycle field grouping therefore could not detect the same-field conflict. No vocabulary normalization was added to force a pass.

The four generated-answer checks after failed NVIDIA extraction are downstream failures caused by missing or inconsistent memory evidence, rather than four independent database bugs.

Against verified local evidence, all five generated responses gave the expected meaning: project/goal, testing preference, Memory Beta, 2026-11-22, and an explicit North/South conflict. Three passed every check. The Memory Beta answer omitted citations, and the conflict answer cited the correct claim IDs instead of the exact memory IDs requested by the strict test. Those two remain Fail for the memory-ID citation contract; their factual content and engine evidence were correct.

Default raw correction/conflict/rescheduling checks are labelled Unsupported because extraction_policy is none. Their observed false checks are preserved. Explicit claim correction, conflict and supersession passed. This distinction prevents treating an absent interpreter as a database regression.

Regression suite: **164 passed, 3 deselected in 118.00 seconds**. Ruff passed for the live runner. Recorded session IDs were independently checked and all are unique. No conversation history was supplied.

UI observation: the JavaScript detail renderer rounds the INT64 unbounded-validity sentinel because JSON numbers use JavaScript Number precision. The Python evidence files retain 9223372036854775807 exactly; no stored validity value was changed. This display limitation was observed during browser inspection and was not repaired in this testing task.

