# Wayfinder MVP v2 — phased build and manual acceptance

This is the new minimal-app delivery sequence. It replaces the animal-first sequence for future MVP work. It authorizes no implementation, account access or spending by itself. All checks start **Not run**.

Use [the master plan](PLAN.md) and [memory-quality contract](MEMORY-QUALITY-CONTRACT.md). Each phase ends with an actual runnable build, exact start/stop instructions, a UI walkthrough, real redacted receipts, automated results, known limits and a safe return path. You test and accept the behavior before advancement. A future proposed button or test is not an implemented feature.

## Phase 0 — Baseline, reuse and return path

Audit current source/services, memory contracts, storage ownership, existing UI and installed Hermes/NemoClaw/OpenShell versions. Preserve unrelated work. Decide how the app calls Iron Web and what configuration is reusable; do not replace the engine to match a document diagram. Verify backup/restore in an isolated runtime and record the rollback limits.

**You receive:** inventory, tested startup/shutdown, baseline report and safe isolated test spaces. Previous test counts remain historical until rerun.

1. **V00-01:** Save different Cedar/Maple labels in separate spaces and query from fresh conversations. Only the matching source/value is returned.
2. **V00-02:** Cleanly restart and verify stable source/space IDs. Restore the test backup into separate storage and confirm the live store was not overwritten.
3. **V00-03:** Inspect reuse-versus-build and the effective runtime/version list. Missing/failed dependencies are visible and do not appear as working integrations.

**Gate:** a recoverable baseline and explicit memory-authority/compatibility decision; no new UI or framework needs to hide an existing failure.

## Phase 1 — Minimal main app and quick-window shell

Build the main desktop shell with Chat, Plugins, Workflows, Memory, Skills, Runs/Approvals and Settings. Include a plain quick-chat window, tray/hotkey controls and active conversation/space identity. Wire existing real status/space data; label not-yet-connected AI/tool features honestly. No animal, capture or microphone component.

1. **V01-01:** Open every main area, create/select a test space, resize the main app and open/hide/reopen quick chat. Unavailable capabilities are disabled/labelled rather than simulated.
2. **V01-02:** Open the same conversation in both views. A space switch clears/rebinds displayed evidence correctly; it does not retarget an existing request or duplicate its record.
3. **V01-03:** Edit a benign UI preference and restart. It persists. Invalid configuration is rejected and credentials are never displayed as ordinary chat/settings text.
4. **V01-04:** Close the main window, use the documented tray/background behavior, then explicitly Quit. Inspect which process/jobs remain; disconnected/offline state is honest.

**Gate:** a usable app foundation, not a claim that chat or all plugins already work.

## Phase 2 — Memory is correct through the app

Implement authenticated owner/space binding and explicit orchestrator memory operations, source inspection, current/history/conflict states, consent-aware mutations and context revisions. Use structured/manual requests before natural-language interpretation if needed. Generalize retained task contracts through a versioned path. Keep conversation retention separate from approved long-term facts.

1. **V02-01:** Propose “Cedar retention is 30 days,” inspect and approve it. Fresh-session recall returns 30 and the actual source/receipt; Maple cannot retrieve it.
2. **V02-02:** Reject a correction to 7 days: current value stays 30. Approve a fresh correction: current recall is 7 and historical/provenance inspection explains the change.
3. **V02-03:** Add an equally authoritative current conflict and ask an unsupported question. The UI shows dispute and missing evidence appropriately; no invented personal answer/citation.
4. **V02-04:** Replay the same approved write, including through both views. One immutable effect remains. Changed input under that identity is refused; unrelated space IDs do not share the write.
5. **V02-05:** Forget synthetic evidence, inspect retention/deletion status, restart and query in a fresh session. Active memory cannot serve it. Test failed storage: no false saved response.
6. **V02-06:** Use a real denied-role/foreign-space probe and a mid-request revision change. No protected data is returned and affected stale context/output is invalidated.

**Gate:** mandatory functional ownership, durability, correction, provenance, deletion and concurrency checks pass. Natural recall quality receives a measured evaluation as the model integration arrives; “perfect” is not asserted from a few examples.

## Phase 3 — Plugins, tool matching and enforcement

Build a reviewed registry, secure connection/configuration storage, enable/disable/update flow, vector/lexical discovery, operation schema validation and a trusted approval gateway. Start with explicitly labelled local connector fixtures. Required checks run inside handlers, not only middleware/prompts. Skills can declare capabilities but cannot grant them.

1. **V03-01:** Configure/test/enable a fixture plugin, inspect its operations and disable it. A dependent request is blocked; changing its account cannot silently retarget a saved operation.
2. **V03-02:** Ask discovery to find a read/search operation. Inspect candidates and the permitted schema set. A similarly worded send/delete tool stays unauthorized; no-match/ambiguous requests stop.
3. **V03-03:** Preview a fixture write, reject it and inspect zero calls. Approve a fresh exact payload: one receipt/effect appears. Changed payload, expired/revoked grant and approval replay are refused.
4. **V03-04:** Propose a manifest/permission update. Reject it: active version/rights remain unchanged. Unreviewed tool names or skill-generated installation instructions cannot execute.
5. **V03-05:** Fault the policy service and attempt an alternate execution bridge. The fixture records zero effects. No error turns into permission.

**Gate:** plugin configuration is useful and auditable without granting blanket tool access. No real external write is enabled before this gate.

## Phase 4 — Real chat, Hermes and Tavily

Connect Hermes to the memory/gateway adapters and real selected model routes. Add streamed responses where supported, stop/retry, attachments/selected documents, source references, disclosure controls and budgets. Tavily provides search/extract and bounded crawl/map through the same gateway. Broad native terminal/worker tools remain disabled until their isolation is verified.

1. **V04-01:** Ask a general question and a memory-grounded question from each interface. Real model output, current source citations and provider/model usage are visible; a UI animation is not proof of inference.
2. **V04-02:** Ask an online question, review the data/query scope and approve it. Tavily returns actual sources used in the answer. A failed page/search is reported, including partial failures.
3. **V04-03:** Ask to compare the selected Cedar documents using the current memory preference. Get a sourced answer, then correct the preference and verify the next answer uses the current value.
4. **V04-04:** Run Lightning and Ultra through the intended account's actual IDs and a harmless structured lookup/result loop. Distinguish NVIDIA and Nebius routes; blocked access is not a pass on the other provider.
5. **V04-05:** Cancel, exceed a small test budget and simulate a provider outage. Both windows show the same run state; no duplicate execution, false completion or unbounded retry occurs. Auxiliary inference obeys egress rules.

**Gate:** a useful remembering/web-enabled assistant in a minimal app, with real traces and still-restricted tool capability. This is the first usable-assistant milestone.

## Phase 5 — Restricted workers and runtime configuration

Trial/pin the chosen NemoClaw/OpenShell topology; expose validated runtime health/settings with reviewed changes. Bind worker identities, effective toolsets, scratch paths and network access. A fresh child conversation or shared container does not itself prove isolation. Use a safe fallback only after its claimed restrictions are demonstrated.

1. **V05-01:** Delegate a Cedar research assignment. Inspect its bounded context, source IDs, snapshot and allowed operations; Maple records and main-memory credentials are absent.
2. **V05-02:** Exercise controlled worker attempts to access memory APIs/files/stores, credentials, session search and alternative HTTP/tool bridges. Real probes are denied; a decorative “blocked” message is insufficient.
3. **V05-03:** Run an allowed lookup and two independent cross-space tasks. Useful work succeeds while results/citations stay scoped.
4. **V05-04:** Preview a runtime/configuration change and reject it. Current effective settings remain. A separately approved safe change is versioned, validated and reversible; pending grants are rechecked if it affects authority.

**Gate:** effective worker restrictions and a truthful runtime manifest. No broad workspace/code worker is silently enabled by passing a research-worker test.

## Phase 6 — Editable workflows

Build natural-language draft planning plus a simple step/dependency editor, schemas, validation, versions, saved templates, run progress, checkpoints and recovery. Use tools directly for atomic steps and workers only for bounded reasoning. No permanent seven-agent fleet or mandatory complex canvas.

1. **V06-01:** Ask for a research-and-draft workflow; inspect/edit its sources, step inputs, dependency order, limits and approval checkpoints. Save a version, close/reopen it and compare the exact definition.
2. **V06-02:** Build the equivalent workflow using the form. Unknown operations, cycles, foreign accounts and invalid output bindings are rejected before calls run.
3. **V06-03:** Run the permitted read/prepare steps and inspect actual progress/results. Independent reads can overlap, but a dependent step cannot consume an unvalidated/missing result.
4. **V06-04:** Pause/cancel, restart around a checkpoint and resume safely. Completed operations are not blindly repeated. A possible external timeout-after-commit is marked outcome unknown and reconciled before retry.

**Gate:** users can actually create, change, inspect and run workflows—not only receive an uneditable textual plan.

## Phase 7 — Reusable skills

Build approved procedure discovery/invocation, manifests, version/digest binding, test examples, reviewed changes and rollback. Workflow templates and narrative skills remain distinct reusable entities.

1. **V07-01:** Use an approved comparison/brief skill on two document sets. Procedure reuse does not copy one space's facts into the other.
2. **V07-02:** Propose a skill from a completed workflow; inspect/reject the change, then approve a fresh valid version and roll it back. Old runs retain their bound version.
3. **V07-03:** Try a skill that requests new credentials/tools or a forbidden send. It cannot expand the grant or install capabilities.

**Gate:** visible, useful reuse with no hidden self-modification or privilege expansion.

## Phase 8 — Background operation, quick tasks and schedules

Complete the persistent service lifecycle, tray/hotkey/quick-window behavior, optional startup setting, one scheduler owner, occurrence IDs/leases, missed-run policy and narrow recurring grants. Show runtime health, last/next run and offline/sleep limits. The quick window remains available on the running device; it is not an observer or a perpetual cloud service.

1. **V08-01:** Leave quick chat open while using other windows; hide/summon it and expand a complex approval into the main app. One request has one shared run/approval identity.
2. **V08-02:** Schedule a test brief a few minutes ahead with an approved local-draft destination. Verify the real output, occurrence receipt and next/last-run status; two accelerated occurrences happen once each.
3. **V08-03:** Pause/revoke a recurring grant or change its output destination. The next unauthorized run stops for review; the old grant cannot authorize email or a different account.
4. **V08-04:** Restart or recover from a missed due time under the selected catch-up/skip/ask policy. Do not replay every missed notification or a completed occurrence.
5. **V08-05:** Change startup/background settings through the UI, then explicitly Quit. Inspect accurate process/job status. A short test is not proof of 24-hour availability; collect a real soak log before making that claim.

**Gate:** controlled follow-through and truthful availability. This completes the workflow milestone.

## Phase 9 — Starter daily-life connectors, one handoff per connector

### Phase 9A — Calendar

Connect a selected test calendar through its supported authorization path. Begin with availability reads, then separately approved writes and sync/reconciliation.

1. **V09A-01:** Inspect availability and a proposed event's calendar/timezone/times/attendees/notifications. Reject it: no event. Approve a fresh proposal: verify one real matching event.
2. **V09A-02:** Replay, change the account after preview, simulate uncertain completion and revoke access. No duplicate or silently retargeted event; blocked/unknown states stay visible.

### Phase 9B — GitHub and optional bounded workspace tools

Connect selected test repositories; separate read, issue/comment, branch/PR, merge and workflow/admin rights. If local code tasks are included, review their sandbox/workspace contract separately before enabling them.

1. **V09B-01:** Read an allowed repo with real source references; an ungranted repo is denied. Preview/reject an issue, then approve a fresh exact proposal and verify one real issue/receipt.
2. **V09B-02:** Test duplicate operation replay and a repository instruction requesting ungranted merge/Actions access. Neither produces an unauthorized effect.
3. **V09B-03:** If the optional workspace adapter is enabled, prepare a diff in an approved test folder, reject it, then approve a fresh change. Verify exact file effects and denied paths/commands. Otherwise mark this capability Unsupported/Not enabled, not passed.

**Gate:** publish only validated capabilities. Notion, email, WhatsApp Business and fitness do not become “connected” merely because their catalog entries exist.

## Phase 10 — Memory/security release gate and packaging

Run the declared held-out memory evaluation and all mandatory invariant/failure checks. Finish selected-space export, deletion/restore behavior, secret/egress controls, stop-all, error recovery and clean setup. Earlier phases already enforce their relevant memory/permission rules; this phase verifies their composition.

1. **V10-01:** Run the [memory manual sequence](MEMORY-QUALITY-CONTRACT.md) with current/history/conflict/missing cases, scope probes, mid-run correction and restart. Inspect actual values, source IDs and failure reports in both views.
2. **V10-02:** Export one space; other spaces/secrets are absent. Forget evidence and test the defined delayed-event/reindex/isolated-restore path with tombstones applied before serving queries. No active resurrection; retained backup/audit limits are explicit.
3. **V10-03:** Fault a store/provider/policy service, exhaust a small budget and use stop-all. No false save/result, unauthorized action or blind repeat of uncertain effects occurs.
4. **V10-04:** Install/start from documented clean instructions in the chosen test environment. Demonstrate chat + Tavily + plugin configuration + edited workflow + approved memory/correction + skill reuse + scheduled draft + rejected/approved connector action.
5. **V10-05:** Review actual quality/latency/cost samples, runtime versions, failed/blocked/unsupported features and recovery limits before accepting the MVP. Historical memory tests and a synthetic UI screenshot cannot replace this evidence.

**Gate:** no known critical memory/authorization failure; accepted declared quality targets; required model/tool paths verified; useful configurable app packaged with a reproducible runbook. No promise of universally perfect recall or service availability.

## After the MVP — connector breadth and optional capabilities

Add Notion, saved notes expansion, mail intake, WhatsApp Business and fitness adapters through the same reviewed manifests, resource limits and acceptance protocol. Each connector gets its own read/configure/revoke/duplicate/recovery and protected-write tests before being advertised as supported. A general fitness SDK needs equivalent multi-format records, coverage/overlap rules, import fallback and separately validated cloud/mobile adapters.

Voice, broad browser control, expanded code execution and online multi-user/device sync require new scope. No new adapter or skill inherits all user permissions. Desktop scanning/capture and animal UI stay outside this version.

## Manual signoff

Use [MANUAL-ACCEPTANCE.csv](MANUAL-ACCEPTANCE.csv) and [PHASE-SIGNOFF.csv](PHASE-SIGNOFF.csv). Record the build, expected/actual observation, source/request/workflow/approval/occurrence IDs, failures and your acceptance. Rows are Not run until executed. A Blocked mandatory memory/security gate blocks release; optional unavailable integrations are reported honestly.
