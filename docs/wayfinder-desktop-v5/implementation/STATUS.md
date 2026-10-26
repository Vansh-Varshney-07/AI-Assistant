# Integration implementation and evidence

26 October 2026 · `codex/ui-backend-integration` · **workspace-parity candidate, not an accepted R1–R7 release**

The user authorized implementation after reviewing v5. The original planning package remains the baseline. This document and [ACCEPTANCE-EXECUTION.csv](ACCEPTANCE-EXECUTION.csv) record the current implementation; they do not relax its gates.

## Delivered in the isolated branch

| Milestone | Work completed | Acceptance state |
|---|---|---|
| I0 | Frozen GitHub `7b59c06d817a08b53d1f139764a757ac9acfdbd9`; 98 reviewed local source imports; explicit initializer/dependency/registry collision resolutions; upstream numbered worker definitions preserved; old and new regression suites run together. | Source assembly/regression implemented. Deliberate import-drift/fault scenarios remain unqualified. |
| I1 | New GitHub visual shell, local fonts/licenses, grouped navigation and command palette, light/dark themes, responsive layouts and source inspector around the existing backend forms. One inclusion manifest governs navigation, preload and owned-host operations. Manifest hash and generation pairing precede readiness. Stable packaged root; explicit existing-root selection; unresolved-effect family fencing and monotonic expiry at memory/Git dispatch. | Working candidate with rendered, actual packaged, transport and live synthetic evidence below. Native dialogs, manual accessibility and broader lifecycle faults remain open. |
| R1–R7 | Existing narrower backend capabilities retained and truthfully labelled. | **Not implemented/accepted by this integration.** Ordinary chat remains disabled; no fake reply or memory-store substitute. |

Original checkout `D:\Opencode_\AI assistant` remains on `codex/platform-integration` at `4913ee9b41442a71fe2630eb59664d57649129ca`. No checkout/stash/reset/clean, private-data migration, service stop, commit, push or main merge was performed there. Integration changes are uncommitted in the separate worktree. Codex could not attach the temporary side-chat worktree; the explicit directory is authoritative.

## Reuse and necessary additions

Hermes 0.21.3/OpenShell remains the only model execution path. Actual isolation inspection reported zero effective tools and memory disabled. The installed SDK exposes explicit history/system-message parameters, but that is not a qualified app conversation service. No agent loop, scheduler, parser, memory engine or desktop driver was added.

The existing Electron/React host, named IPC broker, Python owned helper, authenticated AppService/API, Iron Web graph/vector stores, ActionGate, FileBroker/W35, ContextGateway, Atlas and fixed comparison recipe were reused. The new design is ported from GitHub's workbench/Stitch sources; the demo workbench server, random telemetry, sample spaces, CDN assets and Home-to-store submission are not production routes.

New components fill concrete gaps: `Workspace.tsx` and local design CSS supply the GitHub presentation; `FEATURES.json` supplies one build inclusion declaration; a packaged snapshot and host hash bind the same declaration across layers; `runtime-path.ts` prevents executable moves from silently selecting another data root; the existing ActionGate now enforces conservative unresolved-family locks and monotonic lifetime in the service. The private bridge now enforces 64-KiB UTF-8 frames. Oversized complete results return an explicit narrow-request error; chunked artifact/event recovery is still unfinished.

No upstream worker prompt, task/result schema or numbered worker fixture was rewritten. Existing flat infrastructure modules received the enforcement additions. A legacy test that allowed a new proposal after an unknown effect was tightened to the new invariant; no denial was weakened to make tests pass.

## Actual verification, kept separate by tier

| Tier | Actual result | Limits |
|---|---|---|
| Merged backend and worker contracts | **279 passed, 2 skipped, 1 UI test deselected**; `desktop-app/test-results/backend.xml` | Disposable FalkorDB/Qdrant; deterministic fixture embeddings/model results where declared. Supplied worker contracts are not proof that all roles execute live. |
| React/main/preload contract suite | **38 passed, 0 failed**; `test-results/ui.json`; TypeScript passed | Component and boundary fixtures. Includes foreign-scope/stale-response handling, exact review, manifest mismatch and UTF-8 frame bounds. |
| Rendered Chromium matrix | **6 configurations passed**, zero remote requests and uncaught errors | Explicit synthetic UI fixtures; widths 600/1280/1440/1920, device scales 1/1.25/1.5. Themes, palette, drawer focus/Escape/resize, long inert source and reading-size changes checked. Device scale is not a physical Windows DPI or screen-reader qualification. |
| Actual hidden packaged Windows app | **14 checks passed** against this exact ASAR | Real packaged renderer/preload/main/Python/API and disposable actual neural storage. Creates a space, keeps a proposal unapplied, rejects it, denies foreign/unselected work and verifies persistence plus fresh generation after restart. No fixture bridge. App never shown; no native dialogs or desktop driver. |
| Production Node/Python bridge | **7 checks passed** | Actual owned bootstrap, API/storage, denied unavailable route/foreign space and observed child shutdown. |
| Actual neural memory and managed Hermes | **13 checks passed** in 74.953s | Actual cached ONNX embeddings, scoped memory write/receipt and one synthetic 30-day-memory versus 42-day-file comparison per run. One model invocation, zero worker tools, source hash/freshness checked. Cost/tokens unknown. No held-out quality, account or native proof. |
| Approved app-only native check | **Blocked; zero clicks/typing/native-dialog interactions** | The helper first timed out on app approval, then returned an image from outside the selected Wayfinder app. Automation/capture stopped; only the isolated test process and database were cleaned up. No native pass is claimed. |
| Static package audit | **23 checks passed** | Exact executable/ASAR/host/manifest hashes, isolation/CSP, local fonts/licenses and correspondence with hidden-app evidence. Unsigned local x64 folder; requires the existing checkout/Python/database/model runtime. |

The current binary identity and code fingerprints are in [BUILD-ID.json](BUILD-ID.json). The original source-import ledger is [SOURCE-IMPORT.json](SOURCE-IMPORT.json). Detailed private test reports and synthetic screenshots remain ignored by Git; public counts above are summaries, not reliability percentages.

Failures corrected during implementation: a copied npm cache was removed from the isolated import and exclusion tightened; a missing drawer focus trap was fixed; a renderer test's heading and ambiguous missing-state selector were corrected; the builder was switched to the already installed pinned Electron distribution after DNS download failure; concurrent build/package verification was sequenced; the inclusion manifest was explicitly snapshotted inside ASAR after the package audit found it missing; reading size was connected to actual source text.

## What remains

- **I1 acceptance:** visible native file-picker/approval/cancel walkthrough, screen-reader/real-DPI/forced-colors and detached-trigger checks, full component-fault/lifecycle matrix, typed-result coverage and bounded artifact pagination/chunk recovery. These are not marked passed by headless tests. The user approved the bounded app-only check, but unreliable target capture blocked it. No further native inputs/captures were attempted; W37 remains disabled.
- **R1:** canonical durable conversation/turn service, pending-command journal and expiring admission namespace, durable dispatch reservation, global model admission/budget, stop/crash/disk-full races, genuine history/disclosure and final-result recovery. Transcript storage and SDK compatibility do not satisfy these requirements.
- **R2:** full forget/lineage/privacy barrier, purge/restore reconciliation and the preregistered 40-case held-out neural gate. Retraction and artifact clearing retain their narrower labels.
- **R3:** verified Google account lifecycle/resource grants/projections and independent local WorkItems. Human Google consent is needed only when that reviewable connection flow is ready; no passwords/tokens in chat. Fitness remains deferred.
- **R4–R7:** bounded versioned templates/root budgets, actual Hermes schedule callback qualification and quick-chat lifecycle, binding version/publish/rollback and W01/W10/W35 reconciliation, then safe repository reads. Optional external/native effects remain separate.

No Google account was connected and no W37 action or clipboard access was attempted. During the specifically approved Wayfinder-window check, the helper unexpectedly returned content from another app; it was neither reused for action nor saved into this project. The native check was stopped and isolated test resources cleaned up. A reliable app-only capture/control path is required before retrying. Later Google consent remains a human dependency; the remaining engineering above is unfinished code, not something a human is expected to implement.

## Review the build

The candidate is `desktop-app/release/win-unpacked/Wayfinder.exe`; keep the full folder together. Launch only when the user wants the visible app. For this laptop the existing Python can be selected without changing global settings:

```powershell
.\desktop-app\Start.ps1 -Python 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe'
```

Packaged default data is the stable Electron user-data `runtime` directory. To inspect a deliberately selected compatible existing runtime, quit first and add `-Runtime '<absolute path>'`. An owned root is refused; no automatic import/copy occurs. Do not use the parent thread's active runtime for a test. `WAYFINDER_VERIFY_HIDDEN=1` is a presentation-only harness setting; it grants no new operation or resource access.
