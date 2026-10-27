# Wayfinder rebuild checkpoint 1 — conversation and first-run foundation

Date: 2026-10-27. Branch: `codex/wayfinder-rebuild`. Baseline: `47f0dca`, desktop 0.4.1. Preview target: `0.5.0-preview.1`.

This is an initial implementation checkpoint of the [master plan](WAYFINDER-REBUILD-PLAN.md). It does **not** complete all 95 backlog tasks or activate all workers, task profiles, app presets or arbitrary workflows. The CSV and state ledger retain partial and unstarted work. UI preparation reuses the existing stable API; it does not activate dependent routing before qualification.

## Reuse and changes

Hermes, its managed OpenShell transport, WorkerHub, Atlas, Iron Web, approval services and the existing Electron build remain the implementations. There is no replacement model loop, memory system, scheduler, document parser or desktop driver.

- Runtime truth: inspect installed signatures and registered tool parameter names; add explicit evidence limits for delegation, structured outputs and streaming. Atlas candidates now expose discovered/configured/qualified/available/reason while remaining non-authoritative. Correct stale Chat/Connections/Settings descriptions.
- Contracts: platform-owned `wayfinder.task-envelope/1` and `wayfinder.worker-outcome/1` wrap selected-file profile execution. They bind server-issued run IDs, authenticated scope, bounded source references/hashes, deadline and cancellation reference. Worker-owned definitions/schemas are unchanged. Legacy profile rows remain readable without invented wrapper metadata.
- Conversation isolation: each new chat turn gets a service-issued `chat-run:` scope. A small additive SQLite table records it; older jobs retain their original conversation scope for observation and cleanup. Resources and grants are never copied during this migration. The wider desktop broker still uses `general` for existing file/memory/Git workflows; that migration remains open.
- Visual system: semantic light/dark colors, readable cards, rounded controls, existing local fonts and Lucide icons. Original onboarding SVG provenance is recorded in `desktop-app/resources/visual-assets.json`. Optional stock photographs were omitted for this checkpoint. No renderer network dependency was added.
- Onboarding: three navigable stages for local checks, model verification and workspace/consent; separate optional connections; actionable check errors; expire consent with the five-minute model check. Existing trusted bootstrap verifies the exact model again before opening the workspace. Partial setup persistence needs further work.
- Chat: stable selection/reset, stale-response fencing, synchronous operation admission, Enter/Shift+Enter/IME handling, explicit deletion review, observed generation states, known-turn stop and observation of unacknowledged requests without replay. Only opaque IDs enter the pending-send hint, never prompts.
- Message formatting: reuse pinned [react-markdown](https://github.com/remarkjs/react-markdown) and [remark-gfm](https://github.com/remarkjs/remark-gfm) for code, tables and Markdown. Disable raw HTML, remote images and navigation in model output; show source URLs as inspectable text. Host CSP and named IPC remain enforced. Installed production notices are collected locally with integrity hashes.
- Connections: a passing badge expires while its page remains open. Missing expiry and disconnected credentials cannot appear qualified. Space changes clear old state and ignore old responses/errors.

## Interfaces for worker-configuration development

`wayfinder/platform/contracts.py` supplies strict frozen wrappers; `desktop-app/src/shared/types.ts` supplies their matching read-only transport types. These are integration envelopes, not a revision of the other developer's worker task/result definitions. Selected-file profile results include `envelope` and `outcome`, nullable for historical records. No new external write or generic execution endpoint is exposed.

Capability flags describe a specific existing binding. They cannot mint grants, approve actions, transfer a file between scopes or prove that every provider operation works. Provider-wide operation projections, expiry-aware runtime badges across every view and broader task-scope migration remain P01 work.

## Verification and evidence tiers

All test storage is synthetic and disposable. Native W37 action execution, desktop capture and clipboard reads remain disabled. App-only browser/packaged tests use isolated hidden windows and never send OS mouse/keyboard input or activate another application.

| Tier | Actual result |
| --- | --- |
| Installed Hermes inspection | Hermes 0.21.3, 99 registered tools; isolated analysis exposes zero tools and memory is disabled. Inference was not invoked for this probe. |
| Backend regression checkpoint | 321 passed, 1 live-model test skipped, 1 native UI test deselected; 327.68 seconds. |
| Final contract/profile/chat checks | 29 passed, including new envelopes, legacy records, per-turn isolation and restart without replay; 64.47 seconds. These overlap the regression suite and must not be added as independent coverage. |
| Frontend | 64 tests passed, including delayed-history, stale polling and asset/notice integrity cases; TypeScript check passed. |
| Headless UI | Nine scenarios passed, including an explicit 900px case. Screenshots reviewed for Home, chat and onboarding at desktop/narrow sizes. Model/provider data in this tier are fixtures. |
| Real packaged preview | 18 checks passed on the delivered archive: fresh setup, real CPU memory inference, two synthetic Hermes messages, canonical history, no automatic memory writes and restart without replay. |
| Actual portable EXE | 11 checks passed; all 3,007 extracted backend/source/model files match staging. No development checkout/Python environment selected. Clean quit preserves the isolated profile. |

Local ignored evidence: `desktop-app/test-results/backend.xml`, `rebuild-contracts.xml`, `rebuild-frontend.json`, `rendered/report.json`, and `.local/verification/rebuild/runtime-inspection.json`. Build reports bind the exact archive and portable SHA-256 when available.

Observed problems were corrected before continuing: expired green connection checks, stale scope responses, an outdated test locator, old onboarding CSS leaking into the light theme, and screenshot scroll positioning. Initial unit-test attempts failed because their default temporary path was unavailable; reruns used dedicated test directories/disposable storage. Initial packaging could not see the existing PyInstaller tools and Electron runtime in this checkout. The build reuses those already installed tools and a hash-verified copy of Electron 45 rather than modifying the shared Python environment or installing a global runtime.

## Remaining work

Finish P01 runtime/feature projection and provider operation projections and wider task-scope migration; persist/revalidate partial onboarding progress; integrate and qualify the 16 worker definitions; close the missing role contracts; connect M00 and bounded helpers; then provider task context, every A/P variant, finite workflow infrastructure/editor, recovery, controlled effects and final full-release qualification. The existing document-plus-memory recipe remains available; this preview does not introduce an arbitrary workflow builder.

Google/Gmail/Notion/Tavily manual reads retain their existing permission boundaries. Hosted writes/sends, fitness, recurrence and real W37 execution are not enabled by this UI work. Any later live effect needs its own exact target/payload authorization. The final full-build acceptance and the user's exact-EXE walkthrough remain open.

## Exact preview artifact

`Wayfinder-0.5.0-preview.1-Windows-x64.exe` (514765918 bytes), unsigned Windows x64 portable. SHA-256: `f0e9f3643ab8ab7b7be98e80f766d3b08bedf754ee4b18b15e91565fec280b00`. See the matching verification JSON and checksum in `desktop-app/release/`. This is a checkpoint preview, not acceptance of the full rebuild.

The supported 7z payload and compression level 1 avoid the previous four-minute NSIS compressor limit. The package helper uses Below Normal priority when supported. The portable extraction test compares every staged resource, including native binaries; it does not substitute a successful unpacked launch for portable proof.
