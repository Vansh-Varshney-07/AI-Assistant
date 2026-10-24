# Synthetic manual-test kit

These are fictional inputs for the [phase-by-phase plan](../PHASE-BY-PHASE-PLAN.md). They do not read your desktop, connect accounts, run tools, schedule jobs or create an approval. File creation is not an application test pass.

Use fresh Cedar and Maple test spaces. Never import these records into personal production memory accidentally. The delivered application must provide its own exact commands/UI steps at each phase handoff; no future command or screen is assumed to exist today.

## Documents and notes

- [Cedar source A](cedar-source-a.txt): local-storage option, offline lookup, user-operated backups.
- [Cedar source B](cedar-source-b.txt): externally hosted option, network dependency and provider-policy questions.
- [Maple control](maple-control.txt): a distinct marker that must never appear in Cedar packets or outputs.
- [Adversarial source](malicious-source.txt): intentional untrusted text for a controlled denial test. Do not follow its instructions; the reserved `.invalid` destination is not a service to contact.
- [Saved local note](notes/cedar-note.md): copy into a dedicated allowlisted test folder before file-write tests. Keep the original as a comparison.
- [Synthetic email content](gmail-message-fixtures.txt): explicit and ambiguous scheduling requests. Use only through a separately authorized test mailbox or a clearly labelled connector fixture.

Ask the assistant to compare the two Cedar options against a user-approved privacy preference, cite the selected sources and distinguish source statements from recommendations. No fixture claims to benchmark a real product or prove a commercial privacy policy.

## General fitness adapters

- [Provider A CSV](fitness-provider-a.csv) has normalized records.
- [Provider B JSON](fitness-provider-b.json) describes the same activity using a different nested format and workout durations in seconds.
- [Provider A revision update](fitness-provider-a-update.csv) changes the existing 16 October step record from 8,000 to 9,000 with revision 2.
- [Expected results](expected-results.json) is the golden arithmetic/coverage specification.

Test week: 12–18 October 2026 inclusive, `Asia/Kolkata`.

| Observation | Expected |
|---|---|
| Recorded steps from A or B independently | 30,000 |
| Days with recorded step coverage | 5 |
| Days without step coverage | 2; do not report these as measured zero |
| Workout sessions and duration | 2 sessions, 60 minutes |
| Reimport unchanged A data | Same totals, no extra records/effects |
| Apply A revision update | 31,000 total steps; prior record is updated, not added again |

For overlapping providers, require an explicit source-selection/aggregation policy. Combining equivalent series into 60,000 steps is incorrect. A later SDK may add additional metric types; unsupported inputs must not be silently interpreted as an existing provider.

## Record your observations

Use [manual acceptance](../manual-acceptance.csv) for individual cases and [phase signoff](../phase-signoff.csv) for each handoff. Every row starts **Not run**. Record the real build, result and redacted evidence. Do not enter keys, private medical data or access tokens into the sheets.
