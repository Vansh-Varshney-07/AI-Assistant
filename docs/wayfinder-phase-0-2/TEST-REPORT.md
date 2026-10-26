# Phase 0–2 verification, 2026-10-24

Implementation: Wayfinder 0.2.0, canonical source `D:\Opencode_\AI assistant`.

The complete regression run passed **218 tests**, with **3 opt-in neural/GPU/dataset tests deselected**, in **154.74 seconds**. After a final startup-resource cleanup improvement, all **13 memory/startup tests passed again** in **16.27 seconds**. Counts overlap; they must not be added. The native tests were included in the full suite. Static checks passed after the final change.

Evidence: `regression.xml`, `startup-memory-tests.xml`, `phase02-tests.xml` (the new application cases extracted from the complete run), and `real-embedding-smoke.json`. The test runner/source are included in the implementation archive. An earlier failed focused report is retained under `history/`; it is superseded by the complete passing run.

## How storage was tested

All pytest graph traffic went to a disposable FalkorDB 4.20.7 container on loopback port **6392**, with Redis `appendonly=no` and `save` empty, independently checked through `CONFIG GET`. Each case used owned `test_` graphs and fresh embedded Qdrant/SQLite paths. No pytest traffic was sent to the live persistent database on 6381. The disposable container was removed after verification; synthetic test files remain under the chat workspace's `work` directory.

Pytest's existing deterministic embedding fixtures test control flow and storage behavior. A separate script then instantiated the production BGE embedder with **CPUExecutionProvider**, performed actual embedding/search over Cedar/Maple sources, and tested cold backup/restore. This verifies local neural integration on these examples; it is not a broad semantic-quality benchmark.

The production database was healthy with zero automatic restarts after testing. No live volume, existing workbench facts or installed Hermes policies were modified. Docker initially failed on the previously documented stale inference socket; only its temporary `run` directory was preserved under a timestamped name and recreated. No database repair or reset was run in this implementation.

## What the new tests assert

| Area | Procedure and observed assertion |
|---|---|
| Consent and isolation | Propose Cedar=30; it remains missing until approval. New conversations recall 30 with its actual source ID. Maple returns no Cedar evidence. |
| Transcripts | Store a transcript saying 99; long-term recall remains the approved 30. Message replay creates one transcript record; changed input with the same ID fails. |
| Correction and history | Reject 7: 30 remains. Approve a new correction targeting the original claim: current=7; history contains 30 and the original claim records its change provenance. |
| Conflict and missing | An equally authoritative incompatible assertion yields `disputed`. An unknown predicate yields `missing` and an empty evidence list. |
| Immutable replay | Two concurrent approvals return the same receipt and one source. Same request/different payload fails. Same request in a distinct space has an independent identity/effect. |
| Actual API denial | HTTP requests with a worker credential, foreign-owner credential and unknown token fail before the record-inspection spy can run. Browser-origin requests are denied. Valid owner access succeeds. |
| Scope restrictions | Foreign-space and foreign-task correction targets fail. A conversation cannot be rebound to another space. Caller-supplied owner fields are rejected. |
| Revisions | A proof validates only in its original space/revision. Another memory change invalidates it and pending approval. A real mutation injected during recall makes the read fail as stale. |
| Failed writes | Simulated write failure produces no completed receipt. Retry succeeds when still valid. A failure after actual engine commit reconciles one source; a failed uncommitted operation cannot bypass a newer revision. |
| Forget and recovery | A failing delete leaves a durable pending tombstone and blocks reads. Retrying completes deletion, removes active source/claims and redacts the completed source proposal. Reapproving its old write cannot resurrect it. |
| Cold recovery | Restart preserves IDs/settings. A checksummed cold backup restores into a different graph/directory with the same answer/source. Existing-target restore and corrupted snapshots fail. Later deletion tombstones prevent evidence from returning when an older checkpoint is restored. |
| Native main/quick views | Real Tk widgets and their event loop use the real authenticated API. All seven pages open; resize and quick hide/show work. Both views share transcript/conversation. A space switch clears evidence, and an in-flight callback cannot repaint a different space. |
| Native lifecycle | Real Windows tray and hotkey registration succeed. Explicitly enabled background close hides main; reopening works. Quit closes the API; a subsequent client request fails as disconnected. |
| Settings and ownership | Valid font preference persists; invalid settings/extra secret fields fail. A second runtime owner is denied. A simulated application-state initialization failure releases its engine/lock, allowing Retry. |
| Numeric transport | The maximum INT64 value survives transport as a decimal string rather than losing precision. |

## Reproduction commands used

From the canonical project with the disposable database already running:

```powershell
$env:FALKORDB_PORT = '6392'
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest -q --tb=short --basetemp '<fresh-workspace-directory>' --junitxml '<report-directory>\regression.xml'
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest tests/test_wayfinder_app.py -q --tb=short --basetemp '<another-fresh-directory>' --junitxml '<report-directory>\startup-memory-tests.xml'
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m ruff check wayfinder wayfinder_app.py tests/test_wayfinder_app.py tests/test_wayfinder_desktop.py
```

For future use, the supplied `Test-Wayfinder.ps1` handles unique disposable container creation, an ephemeral port and cleanup. Quit the running app first so its hotkey is available to the native test.

## Limits of this evidence

- Native-controller tests call the app's own controllers/widgets; they do not certify a human visual or accessibility review. Desktop automation approval timed out. OS window inventory independently confirmed the launched `Wayfinder — Personal AI | Phases 0–2` window.
- One intermediate focused run encountered an intermittent Tcl initialization I/O error; the final complete native tests and actual app launch succeeded. Its OS-level cause was not established. This is recorded rather than treated as proof that all desktop conditions are handled.
- The final startup cleanup patch was followed by the 13-test memory/startup rerun, not another full-suite run. The native UI code was unchanged by that patch.
- No NVIDIA model, Tavily search, email/calendar/WhatsApp connector, workflow, skill execution or OS-isolated worker ran through this new app. Installed Hermes/OpenShell versions were inspected, without claiming those integrations work here.
- There is no 24-hour soak, multi-device sync, online multi-user deployment or encryption-at-rest qualification. Current-account filesystem access remains trusted. The upstream FalkorDB persistence bug and existing CLI dependency findings remain documented risks.

The implementation and automated phase gates are complete. User manual acceptance remains pending and is tracked separately.
