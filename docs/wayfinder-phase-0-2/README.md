# Wayfinder phases 0–2

Implemented on 2026-10-24 in `D:\Opencode_\AI assistant`. The former `memory_system` folder is a compatibility junction to that project.

This build provides a native Windows main app and an always-on-top quick-chat window. Both use one authenticated local service, one conversation identity and one selected memory space. It implements explicit memory operations with a review/approval step. General model chat, Tavily, plugin connections, workflow execution and reusable skill execution remain in their later planned phases; their sections state that they are unavailable.

The app has been launched in a clean, separate runtime. It does not import, adopt or overwrite existing workbench memories. Create a space to begin.

## Start and stop

Run in PowerShell:

```powershell
Set-Location 'D:\Opencode_\AI assistant'
docker compose -f compose.yaml up -d --pull never falkordb
.\Start-Wayfinder.ps1
```

Docker Desktop must be running. The existing Python environment is reused automatically; a project-local `.venv` takes precedence when present. A fresh environment needs Python with Tcl/Tk plus `pip install -r requirements.txt`. First real embedding use may fetch BGE model assets from Hugging Face; memory text is embedded locally, not sent to an inference provider.

Use **Quick chat** or **Ctrl+Alt+Space**. The tray icon opens quick chat; right-click it for main app / quick chat / Quit. A conflicting global shortcut can make hotkey registration unavailable; Settings health reports the actual result. The main app always has its own Quick chat button.

Main-window close exits by default. Enable **Keep running in the tray** in Settings to change that behavior. **Quit** stops this app's API, releases its runtime lock, closes its memory engine and removes its tray/hotkey registration. It does not stop Docker or the separately installed Hermes service. There is no Windows startup job, scheduler or 24-hour soak qualification in these phases.

If storage is unavailable, startup displays an offline message with Retry. If another instance already owns the runtime, it cannot open a second embedded-vector owner. The app never reports an unconfirmed write as saved.

## First manual walkthrough

1. Create **Cedar** and **Maple** with New space. Select Cedar in the dropdown. The full space/conversation IDs appear below the toolbar and in quick chat.
2. In Chat, save a synthetic local message. Open quick chat: it shows the same transcript. New chat creates a new conversation in the selected space. Transcripts do not become long-term facts. Clear transcript deletes only that conversation's messages.
3. Open Memory. Keep `subject=me`, `task_id=general`, `predicate=retention_days`, `value=30`. Set source text to `Cedar retention is 30 days.` Click **Propose memory**.
4. In Runs / Approvals, inspect the body, space, revision and request identity. Click **Approve selected**. A completed receipt contains actual source/claim IDs. Reapproving the same proposal returns the same receipt.
5. Return to Memory and click **Recall current**. The packet shows 30, its source/claim evidence and a revision proof. Use New chat and recall again. Select Maple and recall: it is missing. Source/evidence views clear on a space switch.
6. Select Cedar, Refresh sources, then select its source. Copy the claim ID from the displayed provenance. For a correction, set action to `correct`, value to `7`, source text to `Cedar retention is 7 days.`, target to that claim ID and reason to `User correction`. Propose and reject: 30 remains. Propose a fresh correction and approve: current is 7. Recall history and source inspection explain the earlier value and change.
7. Add a fresh `assert` with a different value, clearing targets and reason. Approve it: equal-authority incompatible values produce `disputed`. Recall an unknown field: `missing`, with no invented answer.
8. Refresh sources, select a synthetic source and **Propose forget source**. Review and approve. Refresh sources and recall again, including after restart. Forgotten active evidence and its completed proposal's extra text/result copies are removed; identity digests and tombstones remain. Separately retained transcripts and old private backups are separate retention surfaces.
9. Set font size to 14, save and restart. It persists. Values outside 10–24 are rejected. Test tray-close behavior, reopen main, then Quit.

If a proposal becomes stale because another memory changed after its preview, create a fresh proposal and inspect it again. Rejected proposals cannot later be approved; create a new one. If an operation is `applying` after a failure, retry its exact approval to reconcile its original effect. Pending deletion recovery blocks that space's reads.

## Reproduce tests

Quit the app first to release its global shortcut, then:

```powershell
Set-Location 'D:\Opencode_\AI assistant'
.\Test-Wayfinder.ps1
```

This creates a unique loopback-only disposable FalkorDB container, disables AOF/snapshots, assigns an ephemeral port, runs the suite with isolated Qdrant directories, writes `.local/verification/regression.xml`, and removes only its own disposable container. It does not test against the live database. Do not point the old test suite at persistent port 6381: the pinned FalkorDB release has a documented persistence replay bug triggered by test graph history.

The recorded final run is **218 passed, 3 deselected**. Those excluded tests are opt-in neural/GPU/dataset checks. An additional real CPU BGE smoke test passed independently. See TEST-REPORT.md and the XML/JSON evidence.

## Backup, restore and return path

Quit the app before either operation. Use fresh paths:

```powershell
Set-Location 'D:\Opencode_\AI assistant'
$python = 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe'
& $python -m wayfinder.runtime backup --runtime '.local\wayfinder' --destination '.local\backups\phase02-checkpoint-1'
& $python -m wayfinder.runtime restore --snapshot '.local\backups\phase02-checkpoint-1' --target '.local\wayfinder-restored-1' --current-runtime '.local\wayfinder'
.\Start-Wayfinder.ps1 -Runtime 'D:\Opencode_\AI assistant\.local\wayfinder-restored-1'
```

Backup requires a stopped owner and copies closed vectors, SQLite application state and the named graph's records with checksums. Restore refuses an existing target, creates a different graph, preserves source/owner/space IDs and merges current deletion tombstones before exposing restored memory. Both current and target runtimes must be stopped. Restore was tested with evidence saved before a later deletion: the deleted source did not reappear.

Backups contain private data in plaintext under the current Windows account's filesystem protection. Checksums detect corruption; they are not an encryption or signature system. Copying an old backup elsewhere bypasses this application's reconciliation process. Keep the latest runtime/tombstones when restoring; do not expose raw copied vectors or graphs directly.

To stop using this build, Quit and return to the existing workbench launcher. Its facts and directories were not migrated. Keep the Wayfinder runtime for later reuse; no downgrade or data deletion is necessary. A cold backup is a checkpoint, not a guarantee against every storage or operating-system failure.

## Phase status

Phases 0–2 are implemented and verified by automated storage/API and native-controller tests. Your hands-on visual/accessibility acceptance remains pending. Desktop automation approval timed out, so no human-style click-through or screenshot review is claimed. Later phases have not been started.
