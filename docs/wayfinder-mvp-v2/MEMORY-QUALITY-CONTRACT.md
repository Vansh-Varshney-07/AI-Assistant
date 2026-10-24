# Iron Web memory-quality contract for Wayfinder MVP v2

Status: proposed release criteria, not a new test result or a guarantee of perfect model behavior.

The user makes memory the highest-priority subsystem. Translate that into observable invariants, a reproducible quality evaluation and refusal/degraded behavior when evidence or storage is insufficient.

## Hard invariants

| Area | Required behavior | Negative check |
|---|---|---|
| Ownership | Authenticated identity selects authorized spaces before retrieval | Guessed/foreign ID returns no data |
| Worker boundary | Only the orchestrator accesses Iron Web | Worker cannot discover/call memory or reach its files/stores/session-history alternatives |
| Durable save | A save-success response has the promised durable receipt/state | Storage failure/outage never produces a false saved message |
| Idempotency | Same valid operation replays without duplicate sources | Changed immutable input under the same identity is rejected; same request ID in different spaces stays separate |
| Current truth | Correction/retraction/supersession affects current recall | A superseded value cannot be selected as current evidence |
| Historical truth | A dated query identifies its evidence/time basis | Current and historical answers cannot be silently conflated |
| Conflict | Equally current conflicting claims remain visible as disputed | No model-confidence shortcut silently chooses a fact |
| Provenance | Retained claims and answer citations resolve to authorized source records | Invented source IDs and worker assertions cannot become trusted user facts |
| Consent | Retention/promotion follows explicit policy/approval | A webpage/tool result cannot grant retention consent or modify a user rule |
| Context revision | Packets/caches/pending actions bind relevant revisions | Mid-task corrections/deletions invalidate affected output or force recomputation/review |
| Deletion | Active sources/claims/vectors/derived data obey forget policy | Reindex, delayed events or restore cannot resurrect forgotten evidence before tombstones are applied |
| Concurrency | Scope, receipts and evidence remain correct under overlapping runs | One worker completion cannot modify another space's response/context |
| Wire correctness | IDs, timestamps and large integer boundaries remain exact | JavaScript number rounding cannot alter source/version/validity data |
| Degraded mode | Missing stores/indexes/models produce an honest typed state | No synthesized personalization based on incomplete evidence disguised as full retrieval |

These are system properties to test in the selected topology. Passing a finite test set is evidence, not proof against every possible failure.

## Authority and storage decision

Inventory the current Iron Web engine, shared service, source receipts, graph/vector claims, context compiler and restore behavior before changing schema. Reuse the working stores and lifecycle. The foundation PDF proposed an authoritative journal with graph/vector projections, while the existing architecture uses the dual-store engine and a separate receipt/work journal. Choose retention of this design or a versioned migration explicitly; never quietly turn old receipts into a purported complete factual event log.

If indexes are rebuilt, define the authoritative reconstructible dataset, checkpoint and incomplete/degraded behavior first. A graph-only/vector-only source must retain its attributable ownership and not disappear silently from inspection. Automated repair never guesses facts or joins unrelated spaces.

## Record and context contract

Required conceptual fields include immutable source/claim identity, owner-bound space, subject, predicate/value/type, source location and authority, observed/valid/recorded times where available, consent/sensitivity, lifecycle/revision and deletion/retention state. A model-generated hypothesis, user preference, external claim, task and executed action remain different concepts.

Context packets carry task-relevant selected evidence, scope, source/claim IDs, revision proof, conflicts/unknowns, restrictions, expiry and expected output. They contain neither credentials nor a searchable copy of every user memory. Apply the selected model's disclosure policy before transmission; high-confidence retrieval is not permission to disclose sensitive facts.

Keep transcripts, workflow scratch and durable facts distinct. The UI shows which statements were retained and why. Forgetting a fact must also address affected live/cached/transcript-derived context or clearly require a fresh conversation; deletion cannot be represented as complete while an active response still relies on the deleted material.

## Proposed evaluation

Create versioned synthetic and representative cases with exact expected supported facts, sources, time scopes, required abstentions and forbidden actions. Include straightforward facts, paraphrases, multiple projects, recurring corrections, ambiguous names, missing answers, disputes and concurrent changes. Keep development cases separate from a held-out set; declare target thresholds before inspecting final results.

Proposed initial held-out suite: 40 answer cases, split into 20 straightforward, 10 paraphrased/context-selection and 10 missing/disputed/historical cases, plus dedicated failure-injection and access-boundary checks. These sizes and targets require explicit acceptance before release evaluation; they are not existing results.

Report:

- Correct current/historical value and source-citation rates.
- Retrieval precision/coverage at the chosen context budget; unnecessary personal-data inclusion.
- Wrong-current/stale-fact rate; appropriate conflict/missing states; incorrect abstentions on supported questions.
- Unauthorized disclosure/action count, fabricated accepted sources and false durable-save confirmations.
- Duplicate writes, mixed-space outputs, forgotten-data resurrection and incomplete-recovery incidents.
- p50/p95 latency, tokens/tool calls, provider cost and performance during overlap/restart/outage.

Suggested minimum answer target: at least 95% case-level correctness on the declared small held-out suite, with abstentions scored against each case's expected outcome. All mandatory deterministic invariants pass; no observed cross-space/worker leakage, unauthorized mutation, false save or forgotten-data resurrection is accepted. This is a proposed release threshold, not a promise of 95% reliability for every real-world request.

Model-written explanations are supplementary. Trusted checks compare expected values/IDs and inspect real store/action state. Run Lightning and Ultra with the same evidence/scope; a larger model cannot override a failing policy check or unavailable evidence.

## Manual acceptance sequence

1. Create Cedar and Maple spaces; store different project labels and verify fresh-session separation.
2. Remember a 30-day retention preference with approval; inspect its provenance.
3. Reject a proposed correction: the current value stays unchanged. Approve 7 days: current recall changes and historical evidence remains understandable.
4. Add an equally current contradictory assertion: display dispute rather than quietly overwriting it.
5. Ask a question with no supporting record: report missing evidence.
6. Use the quick window and main app on the same conversation; verify identical request/source identity without duplicated writes.
7. Delegate a bounded worker and exercise real denied-role/file/network probes. No protected record appears.
8. Change/forget a dependent claim while a worker result/action waits: detect the stale packet and request recomputation/review.
9. Restart after acknowledged saves and around a retry: stable records/IDs, no duplicate promotion.
10. Forget synthetic data, rebuild/reindex as supported and restore into a separate test runtime with the deletion ledger applied: no active resurrection; backup limits remain visible.

The build handoff supplies actual commands/UI steps and inspectable receipts. Mark Pass/Fail/Blocked/Not run truthfully. Stop connector expansion if the corresponding memory/privacy boundary fails.
