# Wayfinder desktop · 0.1

A real Windows Electron application using React, TypeScript and the **existing completed backend slices**. This is a memory-and-evidence workspace, not the v4 plan's fully accepted R1–R7 product. No Tkinter/ttk, replacement agent loop, memory engine, scheduler or desktop driver was added.

## Open the app

Double-click **release/win-unpacked/Wayfinder.exe**, or **Start.cmd** in this directory. Keep the entire win-unpacked directory together. This local unpacked build is unsigned; it is not a standalone installer and still uses this checkout's existing Python/backend environment.

The development task did not launch the app window, capture the screen, inspect the clipboard, or run native desktop automation. UI tests ran in jsdom; backend/model tests ran from the terminal. Ordinary use of the app's native file picker/confirmation happens only when you launch it and press those controls.

The default app data root is project/.local/wayfinder-electron, **separate from the earlier .local/wayfinder runtime**. No automatic data import, live-store copy or alternate-root fallback occurs. To open a deliberately selected compatible runtime, quit Wayfinder first, then run Start.ps1 -Runtime <absolute-path>. An already-owned root is refused, not reset.

Existing prerequisites: configured Python environment (project .venv or the existing sibling reserchpaper .venv), existing FalkorDB on the configured address, and cached BAAI/bge-small-en-v1.5 embeddings. Model loading is offline; launching the app does not download weights or install/start/reset services. Document inference additionally needs the existing Ubuntu/OpenShell Hermes sandbox. WAYFINDER_PYTHON can explicitly select a compatible existing Python executable. WAYFINDER_PROJECT_ROOT and WAYFINDER_DESKTOP_RUNTIME are trusted launcher settings, never renderer inputs.

## First user walkthrough

1. Launch and wait for Backend connected. If unavailable, the recovery screen reports failure and offers Retry; no fake online state or data is shown.
2. Create a space. In Memory, choose Propose memory, enter subject me, field retention_days, value 30, and your source statement. Create the review. Nothing is stored yet.
3. Inspect the pending plan and press Review exact change. A main-process-owned confirmation shows the actual service-issued scope, digest, payload and expiry. Cancel once if desired; prepare a fresh proposal to approve. The existing gate independently verifies the resulting receipt.
4. Recall retention_days. Inspect the source. Correct or retract a selected claim with a reason; historical recall stays separate from current recall. Refresh sources when needed.
5. Open Capabilities and Inspect runtime. It qualifies the installed version and isolated zero-tool/no-memory worker, for five minutes. Atlas search returns candidates; it never grants execution.
6. In Documents, explicitly select a supported UTF-8 text file. Ask a question and choose Analyze document, or compare it with one scoped memory field. The separate native disclosure confirmation identifies the file, question and optional memory field. Runs shows actual progress, results, stop, audit and supported recovery.
7. Local Git can inspect preconditions and prepare **one new local codex/ branch** in an explicitly selected ordinary repository. Review requires another trusted confirmation. It cannot edit, checkout, commit, push, merge, run hooks/tests, or contact a remote. Use a disposable repository for your first trial.

There is no ordinary Retry for an uncertain effect. Reconcile the original record. Reselect the original repository first if its short-lived grant expired. An unresolved same-family effect blocks new proposals in this desktop task even if it falls outside the recent-results display window.

Selected file/repository metadata is retained by the trusted main process per space while its grant is valid, so switching views/spaces does not hide its revoke control. Choosing a new file replaces previous file access and can stop the old bound analysis; cancelling the picker preserves the existing selection. All grants expire on app exit and are revalidated by the original backend on use.

## Connected backend parts

| App surface | Actual reused backend | Completed scope connected |
|---|---|---|
| Spaces | AppService create_space/spaces and owner checks | Persistent separate owned spaces |
| Memory | Iron Web inventory/source/recall; current/historical lifecycle | Attributed evidence, missing/disputed states, local neural retrieval; no generated chat answer |
| Memory reviews | Platform MemoryControl + existing ActionGate | Scoped assertions, corrections and retractions, immutable exact review, expiry/revocation, verification/reconciliation and audit |
| Files | Existing FileBroker/W34 | Explicit file/folder selection, bounded discovery, changed-file/scope/revocation checks |
| Document analysis | Existing WorkerHub/W35 + HermesBridge | Bounded selected UTF-8 text analysis; no inherited tools or memory |
| Document + memory | Existing PlatformService fixed recipe, ContextGateway and Atlas | Scoped recall → qualified W35 → source/runtime/freshness validation → synthesis; stop, audit, explicit bounded retry |
| Runs/reviews | Existing persisted worker/workflow/action tables | Read-only bounded listing facade, actual states/results, separate terminal artifact clearing, no automatic replay |
| Quality/metrics | Existing WorkflowReview | Historical artifact/phrase/provenance checks and latency/dispatch counts; semantic accuracy, tokens and cost stay unknown when absent |
| Local Git | Existing GitConnector + exact-action gate | One new local refs/heads/codex/ branch; no broader Git/terminal capability |
| Local activity data | Existing activity CSV adapter | Canonical bounded CSV read, source hash, separate provider totals and overlap warnings; no live fitness vendor or memory write |
| Capabilities | Existing RuntimeInspector and Atlas catalog | Actual installed SDK/isolation evidence; registered/unqualified candidates remain non-executable |
| Settings | Existing application settings | Persisted reading size; background remains off |
| Google setup status | Existing GoogleRead status only | Reports configuration presence and unqualified live state; no account reads/refresh/consent or writes |

Full backend/operation mapping and exclusions are in FEATURES.json. The UI does not turn every registry entry into a feature.

## Deliberately excluded

- General chat: transcript storage exists, but a complete general-chat inference/session service does not. The memory field composer is explicitly grounded recall, not a fake chatbot.
- Google live reads/writes and Gmail bodies/sending: real-account qualification is unfinished. Credential presence is not a live pass.
- Wayfinder WorkItem/task-list service, two-way sync, arbitrary workflow builder, scheduler, quick-chat background lifecycle and agent/skill publish/rollback: missing or partial integration contracts. The installed Hermes Kanban/task code exists, but its dispatcher is not a qualified Wayfinder scope/approval adapter; it is not connected by bypassing the existing service. The one completed comparison recipe is included.
- W33 image input, W36 planning and W37 native execution: excluded from this build; native qualification remains incomplete. No screenshot, desktop capture or clipboard-inspection route is exposed.
- Full forgetting/erasure and store-wide maintenance: cross-copy privacy/retention workflows are incomplete. Retraction preserves history; artifact clearing is narrowly labelled.
- Cold backup/restore: existing CLI primitives remain available after the runtime is stopped. They are not exposed as hot UI operations; a safe stopped-runtime/restore activation flow is not implemented in this app. No second store owner is opened to make a button work.
- Hosted GitHub, other messaging providers, fitness vendor integration, voice/mobile/sync and research/notes connectors remain unqualified/deferred.

## Hermes-first decision and isolation

Actual installed agent: Hermes 0.21.3. Isolated probe: zero effective tools, memory false. The managed installation also contains desktop source/SDK 0.17.2 with dependencies but no built output. Its declared build Node range is ^22.22.0 || ^24.11.0 || >=26.0.0; the laptop build Node inspected here is 22.19.0.

Installed src/contrib/plugin.ts and src/api/plugins.ts constrain plugin REST to /api/plugins/<id> on the Hermes host. Wayfinder already exposes authenticated Windows loopback /v2 operations. There is no qualified Wayfinder namespace adapter/native approval/bootstrap route through that SDK. Using it would require another host/server integration and compatibility qualification; it is not an already working Windows front end for these services. This build therefore takes the planned **thin Electron fallback**, leaves the managed Hermes installation/config untouched and reuses its existing execution bridge. This is not a claim that the SDK is absent or can never support Wayfinder.

The Electron renderer has no Node integration, bearer token, generic IPC/HTTP/shell bridge or network access. Named preload intents go through sender/frame/payload validation in main. Native selections are generated in main; renderer-supplied paths do not grant access. Python owns API credentials and serves the existing authenticated transport. Workers retain existing limited inputs and tools. Native numerical imports initialize on the owned Python main thread before request threads; this fixed a real Windows startup stall hidden by fixture imports.

## Build and verify

From this directory:

    npm ci
    npm run check
    npm test
    npm run package

From the project root, using the existing pinned Docker image:

    .\desktop-app\scripts\Test-Backend.ps1
    .\desktop-app\scripts\Test-Backend.ps1 -ClientOnly
    .\desktop-app\scripts\Test-Backend.ps1 -Neural -Live
    .\desktop-app\scripts\Test-Backend.ps1 -NodeBridge

Each backend run creates/removes only its uniquely named disposable database, with isolated runtime directories. It never runs destructive tests against live Iron Web. -Neural -Live uses actual cached ONNX embeddings and one synthetic managed-model comparison. It does not use live Google/account data or a mock model. -NodeBridge exercises the actual production Node/Python transport with no Electron window. New tests and private reports live under desktop-app; no existing backend or Tkinter files were edited.

Actual evidence and limitations: VERIFICATION.md. No claims of full memory-quality acceptance, a real-browser accessibility pass, or a native desktop pass are implied by these checks.
