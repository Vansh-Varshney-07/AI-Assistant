# Desktop integration evidence · 26 October 2026

This is a local application build, not a declaration that the complete v4 release ladder has shipped. Only new desktop-app files were added. Existing uncommitted backend, Tkinter, registry, runtime configuration and planning files were preserved.

| Tier | Actual evidence | Limits |
|---|---|---|
| Existing backend plus new adapter regression | 153 passed, one live test skipped, one UI test deselected; private backend.xml | Real disposable FalkorDB/Qdrant with deterministic test embeddings; model fixtures where declared |
| Updated client-adapter cases | 14 passed; private client-adapter.xml | Includes an unknown effect older than the 60-row display window, foreign retry-intent denial and failed-start transport/owner cleanup |
| Production private transport + neural engine + Hermes | 13 checks passed in 31.687 seconds; actual-transport.json | Actual cached ONNX embeddings, authenticated API, isolated stores and one actual model call; no UI or live account |
| Managed model outcome | Hermes 0.21.3; comparison completed in 19.274 seconds, one worker invocation | Synthetic 42-day file versus 30-day memory; file hash/isolation/freshness checked; semantic accuracy beyond this case unqualified; token/cost unknown |
| Production Node/Python bridge | Seven checks passed; node-bridge.json | Actual owned bootstrap, authenticated space/inventory, unsupported/foreign scope denial and child shutdown; no Electron window |
| React/IPC boundary tests | 25 passed, zero failed; final ui.json and build-evidence.json | Actual components/handlers with contract fixtures in jsdom; no real native dialogs, browser layout or screen reader |
| Build | TypeScript, Vite renderer, esbuild main/preload, Windows Electron package | Local unsigned x64 folder; current checkout and existing Python/database/model setup still required |
| Native/Google/user walkthrough | Not run | No W37, screen capture, clipboard inspection, live Google data or desktop test window |

## Failures found and corrected

- Initial test discovery used the renderer root and found no tests. Test root now explicitly points to the app directory.
- The first production-transport harness passed the wrong project path; it was corrected before qualification.
- The real owned helper then stalled while initializing NumPy/native libraries inside a pool thread. Numerical/runtime modules now import on the Python main thread before the request pool. Fixture tests had already loaded these modules and could not expose this bootstrap problem. The actual neural/Node transport reruns passed.
- Authorization subclasses were initially normalized as generic schema errors. The private adapter now retains the existing safe scope-denial messages.
- Cross-checking preload and main handler names found a test-environment URL assumption; the fixture reads the source using the known app path. The production route map is checked for exact correspondence.
- Additional review tightened explicit read-retry disclosure, unresolved-action checks beyond recent display limits, and stale green health badges after storage failure.
- Final source/resource checks also verify scope-bound selection restoration, exact preload/handler correspondence, startup-failure server cleanup and Windows ASAR path normalization in the package checker.

All fixes were confined to the new client/adapter and its tests. No existing backend agent prompt, output contract, database engine, action driver or scheduler was rewritten.

## Unverified and intentionally absent

No full held-out neural retrieval quality suite, native app screenshot/layout/accessibility walkthrough, installer/signing/distribution qualification, production account OAuth, external send/write, or W37 execution was performed. A generated app is not proof of those outcomes. Google remains unqualified even if a credential file exists. The app has no automated effect retry or unrestricted terminal capability.

Use the README user walkthrough on the packaged app. Source and packaged-file integrity, exact final frontend counts and executable metadata are recorded in build-evidence.json after the final package checks.
