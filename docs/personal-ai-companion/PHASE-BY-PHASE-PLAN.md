# Iron Web: phase-by-phase build and manual test plan

Date: 24 October 2026. This is the proposed delivery sequence. No phase is marked passed by writing this plan, and no account connection, installation, scheduled job or external action is authorized here.

Read with the [architecture plan](PLAN.md), [decision map](.scratch/iron-web-companion/map.md) and [manual test kit](manual-test-kit/README.md). The architecture decisions stay open until reviewed; this document gives each resulting implementation a small, demonstrable finish line.

## How we will build together

Each phase ends with a working increment and a handoff for you to test. You do not need to wait for the complete assistant.

For every handoff, provide the exact start/stop commands, where to click, required permissions, test data, expected results, known limits, relevant automated checks and a way to return to the previous working version. Instructions must describe the software actually delivered; they must not assume that proposed buttons or diagnostics already exist.

You run the manual walkthrough and record **Pass**, **Fail**, **Blocked** or **Not run** in [the acceptance sheet](manual-acceptance.csv). A failed result gets its actual error and evidence; a blocked connector is not counted as passed. Fix the failure and repeat the affected checks before moving on. Your agreement on the behavior is separate from a passing automated test.

Start with synthetic data and isolated memory spaces. Every phase repeats five checks: the correct active space is visible; another space's data stays absent; rejecting/cancelling an action prevents its effect; no success is displayed without a matching receipt; and restart preserves the acknowledged state relevant to that phase.

### Phase-end handoff contract

- **What changed:** a short demonstration of the new capability.
- **How you run it:** exact tested commands and UI route, with prerequisite services and shutdown order.
- **How you test it:** case IDs below, inputs and expected observations.
- **Evidence:** workflow/request/source/approval/run IDs and redacted traces; no API keys or private prompts in public artifacts.
- **Return path:** last working release/configuration, backup requirements, feature flag and any schema rollback limitation. Never roll databases back blindly.
- **Decision:** remain in this phase until required cases pass and you accept the behavior. Keep unsupported optional integrations explicitly blocked or deferred.

## Overview

| Phase | Working increment you receive | Main thing you can test |
|---|---|---|
| 0 | Reproducible baseline and isolated test workspace | Existing memory still works and can be restored safely |
| 1 | Animal popup and local control panel | Open/close, status, active space and clear non-AI shell behavior |
| 2 | Approved memory operations through an authenticated service | Remember, retrieve, correct, forget and space separation |
| 3 | Tool catalog, vector discovery, gateway and approvals | Correct tool candidates; no effect when denied or outside scope |
| 4 | Hermes orchestrator with verified model routes | Real model responses, tool loop, disclosure and bounded failures |
| 5 | Pinned sandbox and restricted workers | Worker gets a context packet and cannot reach the main memory |
| 6 | Cited document and Tavily research workflow | Relevant sources, useful brief, saved decision and correction |
| 7 | Durable scheduling and narrow recurring grants | Next run, real output, pause, revoke, restart and missed-run behavior |
| 8 | Reviewed reusable skills | Repeat a procedure; reject, version and roll back a skill change |
| 9 | Gmail work intake | Emails become reviewable work items with source links |
| 10A | Saved local notes | Allowed-file reads and reviewed changes |
| 10B | Google Calendar | Availability and exact approved event creation |
| 10C | Notion | Selected notes/task records with explicit sync ownership |
| 11 | WhatsApp Business intake | Authorized business messages enter the common work list |
| 12A | General fitness SDK and import adapters | Identical weekly results from different provider formats |
| 12B | Real fitness API/mobile adapters | Capability discovery, sync, permission revocation and privacy |
| 13 | GitHub connector | Selected repository reads and separately approved writes |
| 14 | Integrated data controls, recovery and release rehearsal | Export/forget/restore, failures, budgets and a clean demonstration |
| 15 | Optional voice increment | Push-to-talk and spoken replies with explicit audio controls |

The first complete research-and-follow-through milestone is **Phase 7**. Reusable procedures join in Phase 8. The broader personal/work connector set follows. This is not a calendar estimate: work size and external onboarding determine elapsed time.

## Phase 0 — Establish the baseline

**Build:** inventory the current implementation and installed services; record versions and who owns each database; preserve existing records; create an isolated manual-test configuration and a verified backup/restore route. Run the current appropriate automated checks and report their actual results. Previous 204/21 pass counts are historical, not this phase's result.

**You receive:** a runbook, baseline result sheet, service/status view and test spaces. The existing workbench can be the interface until the companion arrives. Opening a backup must not require deleting the live database.

**Manual walkthrough:**

1. **P00-01:** Create spaces `cedar_manual` and `maple_manual`. Save “Project label is Cedar” in the first and “Project label is Maple” in the second, using the existing supported ingestion path. Retrieve each from a fresh conversation. Each space returns only its own value and source.
2. **P00-02:** Stop and restart through the supplied commands. The same space IDs and source IDs remain available.
3. **P00-03:** Restore the test backup into a separate runtime/graph/vector location. Confirm the saved values there and prove the original runtime was not overwritten. Close its owner cleanly before reusing the same embedded store.

**Gate:** baseline failures are resolved or explicitly block dependent work. A backup file alone is not a successful restore.

## Phase 1 — Animal popup and control panel

**Build:** a Windows animal popup that expands into a readable panel: active space, memory inspection, chat area, connections, pending approvals, jobs and status. Unimplemented areas are disabled or clearly labelled. Include minimize/dismiss, keyboard operation, pause and quit behavior appropriate to the current build.

**You receive:** a locally launchable UI backed by real service/status and space data. Chat is labelled unavailable until the model route is delivered; no simulated assistant answer is presented as real inference.

**Manual walkthrough:**

1. **P01-01:** Launch, expand, minimize and reopen the animal. The panel is usable with keyboard and mouse, and does not require clicking a tiny animal to read an approval.
2. **P01-02:** Switch between the two test spaces. The name/ID and records change together; old request details and source panels do not remain visible as the new space's data.
3. **P01-03:** Stop the backend, observe an honest disconnected state, restart it and recover the UI. Quit exits the UI. Any still-running background service is named and can be stopped using the documented control.

**Gate:** no unsolicited external calls, desktop scanning, screen capture or microphone permission. A visible UI shell is this phase's success; intelligent chat comes later.

## Phase 2 — Orchestrator-owned memory service

**Decision before implementation:** settle [Choose the orchestrator-only memory contract](.scratch/iron-web-companion/issues/04-memory-contract.md). Resolve the PDF's journal-authority suggestion against actual Iron Web storage; preserve the engine unless a tested migration is selected. Generalize travel-specific context contracts through a versioned compatibility path.

**Build:** authenticated owner/space binding; explicit read/propose/commit/correct/forget operations; source inspection; local approval of memory changes; revision-aware current/historical evidence. Use an explicit operation/structured input if natural-language interpretation is not available yet. Broad connector execution remains disabled.

**Manual walkthrough:**

1. **P02-01:** In Cedar, propose “For this project, retain source material for 30 days.” Inspect the proposed value/source, approve it, start a fresh conversation and retrieve the exact value. Source and receipt are inspectable.
2. **P02-02:** Propose the correction “Use 7 days instead of 30.” Reject once: the current value stays 30. Approve a new correction: current recall uses 7, with the older assertion preserved in the lifecycle evidence.
3. **P02-03:** Run the same question in Maple: Cedar's retention value is absent. Use the supplied denied-role/cross-space diagnostic: access is rejected before records are returned. A diagnostic must exercise a real service check, not merely print “denied.”
4. **P02-04:** Forget the synthetic retention source/claim, inspect the deletion/retention receipt, start a fresh session and query it. Active retrieval cannot return it; retained audit/backup limitations are stated accurately.
5. **P02-05:** Restart and verify approved memory persists while forgotten data remains unavailable. A failed write produces no save-success claim.

**Gate:** ownership, revision and deletion behavior are enforced in service code, not delegated to model judgment. This phase does not claim workers are sandboxed yet.

## Phase 3 — Tool discovery and trusted execution

**Decisions:** [tool routing](.scratch/iron-web-companion/issues/05-tool-routing.md), then [approval behavior](.scratch/iron-web-companion/issues/06-approvals-recurring.md). Use deterministic fake connectors and a dedicated test folder; no real mailbox/calendar is needed.

**Build:** reviewed operation metadata, separate catalog vectors/lexical search, schema validation, eligible worker tool exposure, trusted gateway, exact-payload approval receipts and persistent operation IDs. Tool credentials stay outside workers. Default denial applies if policy validation fails.

**Manual walkthrough:**

1. **P03-01:** Request “Find messages mentioning Cedar.” The selection trace identifies a permitted search/read candidate; it does not select send, delete or calendar creation just because metadata is similar.
2. **P03-02:** Preview a synthetic outbound message to the test sink. Reject: the sink records zero sends. Approve the exact payload: one matching receipt/effect appears. The test sink is explicitly labelled; it is not a real email.
3. **P03-03:** Change the recipient/body after approval or replay the same single-use approval. The changed/replayed action cannot create another send. Expired and revoked approvals are also refused.
4. **P03-04:** Ask for an unsupported operation, ambiguous account, or access to a disallowed path. The gateway stops for clarification/denial rather than substituting a stronger tool.
5. **P03-05:** Use a supplied fault switch to make the policy component unavailable. The connector call count stays zero. A middleware exception must not bypass the authoritative gateway check.

**Gate:** vector ranking never grants permission. A matching tool or model-written “approved” statement is insufficient to execute.

## Phase 4 — Hermes and real Nemotron routes

**Build:** connect the Hermes orchestrator to approved memory operations and the gateway. Add provider-specific routes, task budgets, cancellation, inference disclosure and usage traces. Preserve NVIDIA and Nebius as distinct configurations. Validate both requested Nemotron families through the intended provider's actual account-visible IDs; do not reuse model spellings across providers blindly.

**You receive:** real conversational responses and a provider/model indicator. Live requests require separately authorized credentials and a test-spend limit. If Nebius access is unavailable, mark that route Blocked; a working NVIDIA route does not pass it.

**Manual walkthrough:**

1. **P04-01:** Select Lightning, approve the disclosure preview and ask “What is the current project label?” in each test space. Receive a grounded value and source reference. Repeat with Ultra. Inspect actual routing/usage evidence.
2. **P04-02:** Ask a question with no supporting memory. The assistant shows missing/insufficient evidence rather than inventing a personal fact. Ask it to remember a new value: a concrete memory proposal still needs approval.
3. **P04-03:** Run a harmless fixed lookup through the actual model tool-call/result loop. Check the selected operation, validated arguments, gateway receipt and final result; normal text that merely describes a tool call is not a pass.
4. **P04-04:** Cancel a running request; use a small budget and a controlled provider error/timeout. The UI reports cancelled, budget-limited or failed states without false completion or unbounded retry. Auxiliary model routes obey the same egress policy.

**Gate:** real route and tool-loop evidence for each claimed provider/model. Use restricted tools only; no broad terminal or uncontrolled worker capabilities are enabled by this phase.

## Phase 5 — NemoClaw/OpenShell and worker isolation

**Build:** pin and trial a compatible managed stack and effective enforcement policy. Keep the Windows UI; use the chosen supported sandbox topology after approval. Run specialist workers with bounded context, restricted identities/toolsets and no main-memory credentials, mounts or networking. A shared parent/child conversation boundary is not sufficient.

**You receive:** a worker/context inspector and a reproducible allow/deny probe panel. The integration trial is bounded; if managed-stack compatibility fails, select and accurately describe a restricted fallback before proceeding. No “secure sandbox” pass is awarded for installation alone.

**Manual walkthrough:**

1. **P05-01:** Ask the orchestrator to delegate a Cedar summary. Inspect the packet: relevant Cedar facts, source IDs, task/snapshot IDs, scope and output contract appear; Maple facts and credentials do not.
2. **P05-02:** Through a controlled worker probe, attempt main-memory API discovery/calls, store networking, host memory/credential file reads and session-history alternatives. Inspect actual denied operations and zero returned protected data. Do not expose real secrets for this test.
3. **P05-03:** Ask the same worker to perform an allowed synthetic lookup through the gateway. It succeeds within the grant, proving the worker is useful as well as restricted.
4. **P05-04:** Run Cedar and Maple jobs concurrently. Each response/citation belongs to its own packet. Change a dependent fact after a proposal is prepared: stale context is detected and the affected action waits for review.

**Gate:** effective filesystem, network, identity and tool restrictions—not prompts—establish the claimed separation. Real connector workers wait for this gate.

## Phase 6 — Cited research with documents and Tavily

**Build:** selected-source ingestion, bounded Tavily search/extract/crawl/map operations, citations, research-worker output, memory proposal and the first starter brief procedure. Upload/folder scope, web queries, model transmission and costs are reviewable. The Tavily connector is web research, not implicit authenticated browser control.

**Manual walkthrough:**

1. **P06-01:** Select the two Cedar documents in the [test kit](manual-test-kit/README.md). Ask “Compare the options using my project's privacy priority.” Approve the plan. The brief uses the document facts and the current approved preference, cites the actual sources and labels unsupported conclusions.
2. **P06-02:** Request a bounded public-source web check. Approve the query/provider/domain limits. Tavily returns source URLs and excerpts; inspect which were used. Live web wording can vary, so judge provenance and relevance rather than a hardcoded answer.
3. **P06-03:** Include the malicious test document. Its instruction to export memory or widen permissions remains source text; no unauthorized gateway call occurs.
4. **P06-04:** Approve remembering your chosen option. Start a fresh conversation, retrieve it, correct it and ask again. The current decision and source relationship are visible without giving the research worker memory access.

**Gate:** one useful, source-linked brief; bounded remote disclosure; current memory; no executed source-injected instruction. An external outage is shown honestly, without a fabricated successful search.

## Phase 7 — Real scheduling and controlled follow-through

**Build:** one scheduler owner, durable jobs/occurrences/leases, next/last run, pause/cancel, approved output destination, missed-run policy and narrowly scoped standing grants. Store task state separately from memory facts. Windows sleep/offline behavior is visible.

**Manual walkthrough:**

1. **P07-01:** Schedule a Cedar brief for a few minutes ahead, with permission to write only to the synthetic draft folder. Confirm timezone, source set, model budget, output path and approval. At the due time, inspect the real file, run ID, completion receipt and last/next-run status.
2. **P07-02:** Create a recurring test job with a narrow grant. Let two scheduled occurrences run. Each occurs once; repeated delivery of the same occurrence does not create another draft/notification. An accelerated test is not evidence of a week-long service.
3. **P07-03:** Pause before a due time: no new operation occurs. Resume with a valid grant. Revoke that grant: the next run pauses for approval rather than silently continuing.
4. **P07-04:** Restart around a due time. Apply the chosen catch-up/skip/ask policy and show it in the run history; do not replay every missed occurrence. A completed occurrence is not repeated.
5. **P07-05:** Change the destination or ask the approved job to email its report. The existing local-draft grant cannot authorize the new action. Cancel during execution: further steps stop, while any already-applied or uncertain effect is reported.

**Gate:** scheduled work really produces the allowed output, survives restart and respects grant changes. This completes the first research-and-follow-through milestone.

## Phase 8 — Reviewed reusable skills

**Build:** reviewed manifests/procedures for paper review, project brief and commitment check; capability requirements, version/digest, tests, publication approval and rollback. Worker-created improvements remain proposals.

**Manual walkthrough:**

1. **P08-01:** Run the brief skill on two different synthetic document sets. The procedure/output contract is reused while source facts and memory spaces remain distinct.
2. **P08-02:** Propose a skill improvement, inspect its diff and reject it. The active version stays unchanged. Approve a separate valid proposal and inspect the new version; roll back and rerun.
3. **P08-03:** Try a skill revision that requests an ungranted send operation or attempts to install a new tool. Loading the skill does not expand capability grants; the attempted action is denied or explicitly sent for separate review.

**Gate:** useful repetition without hidden personal-data copying, unreviewed code installation or privilege growth.

## Phase 9 — Official work intake from Gmail

**Build:** one explicitly connected test mailbox, bounded read-only synchronization, account/source IDs and a common work list. Display extracted obligations, assignee, date/time, ambiguity and source evidence. Reading, mailbox mutation, draft management and sending remain separate capabilities.

**Manual walkthrough:**

1. **P09-01:** In a permitted test mailbox, receive one message with an explicit date and one with an ambiguous “next Friday.” Approve the read/sync scope. The first becomes a reviewable work-item proposal with a source link; the second shows the uncertainty instead of confidently scheduling a guess.
2. **P09-02:** Reject one proposal and approve the other. Only the approved item enters the tracked list. No calendar event, reply or mailbox change happens automatically.
3. **P09-03:** Re-sync the same message, edit a source where supported and revoke mailbox access. Deduplicate intake, preserve provenance, and show a reconnection/blocked state without claiming a new successful sync.

**Gate:** real authorized read evidence and accurate task proposals. Public-distribution/provider review prerequisites are documented separately from a development-account pass.

## Phase 10 — General tasks, notes and calendar

These are **three separate handoffs**. Test each before adding the next connector. Settle task/source-of-truth ownership first; do not silently overwrite edits across applications.

### Phase 10A — Saved local notes

**Build:** a user-selected notes folder, saved text/Markdown reading, note-linked work items, and reviewed write diffs. Unsaved Notepad UI content remains outside the file adapter.

1. **P10A-01:** Select only the test-kit notes folder. Read a note and create a proposed work item with its source. A path outside the allowlist is denied.
2. **P10A-02:** Preview an append/overwrite and reject it: file bytes remain unchanged. Approve a valid change: a receipt and exact diff appear. Modify the file externally after preview: the stale proposal waits for renewed review.

**Gate:** useful saved-file integration, exact reviewed writes and no arbitrary desktop/file scanning.

### Phase 10B — Google Calendar

**Build:** permitted availability reads and reviewed events on a chosen test/app calendar. Show timezone, start/end, recurrence, attendees and notification behavior before action approval.

1. **P10B-01:** Ask to schedule an approved work item, inspect the proposed event and reject it. No event exists. Approve a fresh proposal and verify exactly one matching event in Google Calendar.
2. **P10B-02:** Replay the operation or simulate a timeout after commit. Reconcile the existing event/receipt before retry; do not create a duplicate. Change the calendar or attendees after preview: reapproval is required.
3. **P10B-03:** Change or cancel the event externally. Synchronization follows the agreed ownership/conflict rule and displays the change; it does not silently reinstate a cancelled event.

**Gate:** actual calendar verification, not just an assistant saying “scheduled.”

### Phase 10C — Notion

**Build:** selected shared pages/data sources, note/task reads and separately approved inserts/updates. Keep explicit links between the work item, source note and optional calendar event.

1. **P10C-01:** Read an explicitly shared test page; an unshared page is inaccessible. Create a task-page proposal and approve it: one actual linked record appears in Notion.
2. **P10C-02:** Change a field from Notion and a conflicting field locally. The chosen conflict/ownership behavior is visible and preserves both evidence and your ability to choose.
3. **P10C-03:** Replay synchronization and a controlled uncertain write. There is no duplicate page/block/task, and the UI reports unresolved outcomes until reconciled.

**Gate:** a usable tasks/notes/calendar loop without pretending all three systems are interchangeable sources of truth.

## Phase 11 — WhatsApp Business work intake

**Prerequisite:** approved, eligible Business API onboarding and an explicit inbound-receiver design. Do not promise access to arbitrary personal WhatsApp history. No silent public exposure of the Windows memory service.

**Build:** signature/account-validated business events, provider message IDs and proposed obligations in the same work list as Gmail. Start with intake; outbound business messaging is a separate approved capability subject to provider restrictions.

**Manual walkthrough:**

1. **P11-01:** Send an ordinary synthetic task message to the authorized business test number using the provider-supported test path. Inspect the received event/source ID and proposed work item; approve it to track it.
2. **P11-02:** Replay the event: one work item remains. Submit a wrong-account or invalid-signature fixture: it is rejected without exposing another account's data.
3. **P11-03:** Try to have message text authorize sending or reading unrelated memory. No permission is granted. Any outbound test requires its own valid recipient/content approval and provider allowance.

**Gate:** test-account events actually arrive and deduplicate. If eligibility/receiver prerequisites cannot be met, label this connector Blocked and keep the remaining app functional.

## Phase 12 — General fitness support

### Phase 12A — Adapter SDK and imports

**Build:** provider-neutral record types, capability discovery, source/revision IDs, unit/timezone normalization, coverage flags, read/import policies and deterministic aggregation. Demonstrate two different synthetic provider formats before claiming extensibility. A universal credential scraper is not part of the design.

1. **P12A-01:** Import `fitness-provider-a.csv`; separately import the equivalent provider-B JSON in another space/profile. Each adapter produces **30,000 recorded steps across 5 covered days**, **60 workout minutes** and **2 days without step coverage** for the stated test week. Missing days are not presented as zero activity.
2. **P12A-02:** Import provider A again: totals stay the same. Apply its revision-2 update: total steps becomes **31,000**, not 39,000, because an existing record was replaced by a newer revision.
3. **P12A-03:** Combine overlapping providers. The report identifies the overlap and applies an explicit source-selection policy; it does not blindly add both 30,000-step series. Ask a work-email worker for the fitness details: they remain outside its packet.
4. **P12A-04:** Approve a weekly summary/goal as memory, then forget the imported test dataset. Inspect the affected summaries, derived data and jobs; active retrieval cannot resurrect the removed records.

**Gate:** deterministic arithmetic, provenance, coverage and repeatable adapters independent of a model's prose.

### Phase 12B — Real provider and mobile bridges

**Build:** add adapters using available official cloud APIs, authorized phone bridges or supported exports. Each advertises its actual metric/history/background-sync capabilities. A provider is supported only after its conformance/onboarding checks pass; the SDK remains general even when an app exposes no usable API.

1. **P12B-01:** Connect one authorized source through its supported method. The capability screen matches the metrics actually available. Compare a bounded imported period against the source application's records.
2. **P12B-02:** Revoke source permission and run another sync. Stop reading, show the lost permission, preserve the selected retention policy and never report the failed sync as complete.
3. **P12B-03:** Add a second adapter or export format through the same contract. The UI and weekly worker need no provider-specific rewrite. Unsupported metrics/apps show an honest unavailable/import path.
4. **P12B-04:** Create a narrow weekly-summary grant. Verify a real report and its data period, sources, coverage and permitted destination. Sharing health/fitness output elsewhere requires separately approved scope.

**Gate:** usable summaries across validated adapter paths; no promise of seamless access to every private fitness application.

## Phase 13 — GitHub

**Build:** selected-repository access; read/summarize first; issue/comment/branch/PR operations exposed separately. Merge, Actions/workflow dispatch and administration remain unavailable unless deliberately added with their own gates.

**Manual walkthrough:**

1. **P13-01:** Summarize an authorized synthetic/test repository and cite actual files/issues. Query a repository outside the grant: access is denied before data is returned.
2. **P13-02:** Propose an issue with a precise repository/title/body. Reject: nothing is created. Approve a fresh proposal: verify one actual issue and its receipt in GitHub. Replay cannot create another issue.
3. **P13-03:** Ask a repository document or skill to merge a PR or run Actions without permission. It cannot expand the grant. If code execution is added later, it receives a separate sandbox review and manual test gate.

**Gate:** useful repository workflows with exact operation/repository boundaries, not a blanket “GitHub access” pass.

## Phase 14 — Integrated controls, recovery and release rehearsal

**Build:** complete export/forget/retention/backup controls, visible model/connector egress, OS-backed secret handling, operational status, stop-all, budget accounting and a clean-start runbook. Individual phases already enforce approvals and relevant deletion/privacy rules; this phase tests their interactions.

**Manual walkthrough:**

1. **P14-01:** Export a selected synthetic space and inspect the contents. Other spaces and credentials are absent. Forget a source and inspect affected vectors/claims/summaries/cache state using the supported diagnostics.
2. **P14-02:** Restore an older test backup into a separate runtime and reapply the authoritative deletion ledger/tombstones before queries. The corrected value remains current and the forgotten value is not served. Disclose remaining backup-retention limits.
3. **P14-03:** Disconnect a provider, exhaust a tiny test budget, stop a required service and restart during a queued workflow. Pending/failed/unknown states are distinguishable; no unauthorized external operation or false save/schedule success occurs.
4. **P14-04:** Use stop-all during a controlled job. New operations are blocked; in-flight completed/uncertain effects are recorded. Demonstrate recovery using the runbook, without automatic replay of uncertain writes.
5. **P14-05:** On a clean test environment, follow the documented setup and run the Phase-7 demonstration with synthetic data. Show actual provider/model routing, citations, a correction, scheduled output and a rejected action. Historical/accelerated recordings are labelled as such.

**Gate:** required automated and manual checks pass on the claimed topology; report failed/blocked/unsupported cases and actual model-evaluation sample sizes. For hackathon delivery, prepare the licensed source, setup, synthetic demo and required submission artifacts without publishing personal data.

## Phase 15 — Optional voice, after the core works

**Build:** push-to-talk input and spoken replies, with clear microphone state, stop/mute controls and an explicitly chosen local or remote speech route. Voice is not needed to pass the text-first milestone. No always-on listening or desktop capture is implied.

**Manual walkthrough:**

1. **P15-01:** Press to talk, say a synthetic request, inspect the transcript and stop recording. Nothing is captured while the control is inactive.
2. **P15-02:** Speak an action request with a deliberately misrecognized name/date. Correct the transcript/proposal before approval; voice input cannot bypass the same action gate used by text.
3. **P15-03:** Mute/stop a spoken response and deny microphone permission. Text chat stays usable. Any remote audio transmission is disclosed and restricted by the selected policy.

**Gate:** accessible voice control with equivalent approvals, accurate capture state and a working text fallback.

## What we will not silently add

Online multi-user deployment, cross-device synchronization, broader browser control and additional connectors get their own later scope and acceptance gates. Desktop scanning/screen capture remains excluded. A new provider, skill or model does not automatically acquire existing permissions.

## Your feedback after each handoff

Use this short format, with the acceptance sheet for details:

```text
Phase and build version:
Test case IDs run:
What I expected:
What actually happened:
Pass / Fail / Blocked / Not run:
Relevant source/request/workflow/approval/run IDs:
Error text or redacted evidence:
Behavior I want changed before moving on:
```

Application tests, accounts and actual execution remain future work in this delivery plan. The accompanying files provide repeatable inputs and expected observations; they do not certify that the corresponding product features already exist.
