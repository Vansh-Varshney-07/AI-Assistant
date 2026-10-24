# Nemotron validation after repairs

Run: `nm_1023_124524`. Real API calls through the local workbench. Real BGE embeddings, FalkorDB and embedded Qdrant.

| Model | Test | Result |
|---|---|---|
| nvidia/nemotron-3.5-lightning-30b-a3b | 1 Creation | Pass |
| nvidia/nemotron-3.5-lightning-30b-a3b | Write replay | Pass |
| nvidia/nemotron-3.5-lightning-30b-a3b | 2 Cross-session retrieval | Fail |
| nvidia/nemotron-3.5-lightning-30b-a3b | 3 Preference | Fail |
| nvidia/nemotron-3.5-lightning-30b-a3b | 4 Automatic correction | Fail |
| nvidia/nemotron-3.5-lightning-30b-a3b | 5 Conflict | Pass |
| nvidia/nemotron-3.5-lightning-30b-a3b | 6 Restart persistence | Pass |
| nvidia/nemotron-3.5-lightning-30b-a3b | 7 Stale memory | Fail |
| nvidia/nemotron-3.5-lightning-30b-a3b | 8 Precision | Fail |
| nvidia/nemotron-3-ultra-550b-a55b | 1 Creation | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | Write replay | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 2 Cross-session retrieval | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 3 Preference | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 4 Automatic correction | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 5 Conflict | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 6 Restart persistence | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 7 Stale memory | Pass |
| nvidia/nemotron-3-ultra-550b-a55b | 8 Precision | Pass |

13 passed; 5 failed. 25 retained test records.

Every query uses a new session UUID and no history. Writes pass user text to the selected Nemotron interpreter; tests do not provide claims or hardcode responses. Field names are read from the actual scoped graph. Structured answers cite only returned memory IDs. Semantic candidate lists are preserved separately from routed field recall used for generation. Both actual server processes were cleanly restarted during persistence checks, using the same stores and NVIDIA settings.

Full prompts, validated extraction attempts, routing, generated answers, IDs, claim states and timings are in nemotron-evidence.json. Full retained records are in nemotron-records.json. Prior runs were not wiped.

## nvidia/nemotron-3.5-lightning-30b-a3b: 1 Creation — Pass

Namespace: `nm_1023_124524_light_base`

Checks: `{"writes_ok": true, "both_stores": true, "semantic_claims": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: Write replay — Pass

Namespace: `nm_1023_124524_light_base`

Checks: `{"succeeded": true, "no_duplicate": true, "no_second_inference": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 2 Cross-session retrieval — Fail

Namespace: `nm_1023_124524_light_base`

Checks: `{"ok": false, "expected_stored_evidence": true, "grounded_answer": false, "citations": false}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 3 Preference — Fail

Namespace: `nm_1023_124524_light_base`

Checks: `{"stored": true, "preference_kind": false, "retrieved_actual_id": true, "answer": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 4 Automatic correction — Fail

Namespace: `nm_1023_124524_light_label`

Checks: `{"writes_ok": false, "old_claim_corrected": false, "current_beta": false, "old_id_excluded": true, "grounded_answer": false, "citations": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 5 Conflict — Pass

Namespace: `nm_1023_124524_light_conflict`

Checks: `{"writes_ok": true, "same_field": true, "disputed": true, "answer_disputed": true, "both_sides_cited": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 6 Restart persistence — Pass

Namespace: `nm_1023_124524_light_persist`

Checks: `{"restarted": true, "same_source": true, "same_id_retrieved": true, "exact_phrase": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 7 Stale memory — Fail

Namespace: `nm_1023_124524_light_review`

Checks: `{"writes_ok": true, "prior_superseded": false, "old_id_excluded": true, "current_date": true, "answer": true}`

## nvidia/nemotron-3.5-lightning-30b-a3b: 8 Precision — Fail

Namespace: `nm_1023_124524_light_precision`

Checks: `{"ok": false, "correct_semantic_rank": true, "actual_orange_evidence": true, "answer": false, "orange_source_cited": false}`

## nvidia/nemotron-3-ultra-550b-a55b: 1 Creation — Pass

Namespace: `nm_1023_124524_ultra_base`

Checks: `{"writes_ok": true, "both_stores": true, "semantic_claims": true}`

## nvidia/nemotron-3-ultra-550b-a55b: Write replay — Pass

Namespace: `nm_1023_124524_ultra_base`

Checks: `{"succeeded": true, "no_duplicate": true, "no_second_inference": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 2 Cross-session retrieval — Pass

Namespace: `nm_1023_124524_ultra_base`

Checks: `{"ok": true, "expected_stored_evidence": true, "grounded_answer": true, "citations": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 3 Preference — Pass

Namespace: `nm_1023_124524_ultra_base`

Checks: `{"stored": true, "preference_kind": true, "retrieved_actual_id": true, "answer": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 4 Automatic correction — Pass

Namespace: `nm_1023_124524_ultra_label`

Checks: `{"writes_ok": true, "old_claim_corrected": true, "current_beta": true, "old_id_excluded": true, "grounded_answer": true, "citations": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 5 Conflict — Pass

Namespace: `nm_1023_124524_ultra_conflict`

Checks: `{"writes_ok": true, "same_field": true, "disputed": true, "answer_disputed": true, "both_sides_cited": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 6 Restart persistence — Pass

Namespace: `nm_1023_124524_ultra_persist`

Checks: `{"restarted": true, "same_source": true, "same_id_retrieved": true, "exact_phrase": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 7 Stale memory — Pass

Namespace: `nm_1023_124524_ultra_review`

Checks: `{"writes_ok": true, "prior_superseded": true, "old_id_excluded": true, "current_date": true, "answer": true}`

## nvidia/nemotron-3-ultra-550b-a55b: 8 Precision — Pass

Namespace: `nm_1023_124524_ultra_precision`

Checks: `{"ok": true, "correct_semantic_rank": true, "actual_orange_evidence": true, "answer": true, "orange_source_cited": true}`

## Reproduce

```powershell
Set-Location 'D:\Opencode_\memory_system'
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_nemotron.py
```

This runner expects the workbench started with --nvidia and the existing key available through --key-file or NVIDIA_API_KEY. It makes real NVIDIA requests and retains explicitly labelled test records.