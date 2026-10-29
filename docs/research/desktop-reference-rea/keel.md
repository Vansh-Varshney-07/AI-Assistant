# Keel 0.5.1 — actual REA package investigation

Date: 27 October 2026. Scope: static release-package analysis for Wayfinder security and UI/UX planning. No Keel process, model, connector or installer was executed. No account or desktop access occurred.

## Target and execution evidence

- Publisher release: [Keel-Labs/keel v0.5.1](https://github.com/Keel-Labs/keel/releases/tag/v0.5.1), `Keel-0.5.1-win-x64.zip`, 244,647,723 bytes.
- Download SHA-256: `f0b4b69e59e2a1aa0bfcda98f77f403f55f4e6300a571fc2c8c157a3d7eed671`, matched GitHub's published asset digest.
- Existing 7-Zip extracted only `resources/app.asar`; ASAR SHA-256 `ae23392d2344a82ec1734925aaf993d931788c6ddbe9c0ff2ec622e118cb986f`.
- Tool: cloned REA 6.8.0 CLI under isolated Node 24.22.1. Analysis selected package metadata, Electron main/preload, FileManager, settings, context assembly, export guard, renderer HTML and its bundled JavaScript.

Executed operation:

```text
node rea/scripts/rea.mjs analyze-javascript-application <Keel app.asar>
  --source-paths-json <selected-sources.json> --max-heap-mb 768
  --analysis-timeout-ms 60000 --format json
```

The operation returned **exit 1 / provider_timeout**, not a passing complete analysis. It reached the declared 60-second per-source deadline while processing the final 550,182-byte minified renderer bundle. Total invocation elapsed time, including earlier files, partial-evidence construction and delivery, was 213.859 seconds.

REA preserved authenticated partial Evidence:

`ev_300dd77996145228d1c688ecc8254fc987cd82ece7f88a9e1b4bc91b6295ffb0`

The partial result reports six completed JavaScript files, one skipped JavaScript source, zero parse failures, three BrowserWindow candidates, three context-bridge APIs, 132 exposed members, 130 literal IPC channels and 110 main-handler candidates. All 110 renderer transmissions remain ambiguously paired. The caller selected nine paths; REA reports 5,919 inventoried files outside that selected scope. Counts are REA's reported categories, not a claim that all package members were analyzed.

Raw stdout/error JSON, stderr, exit code, exact arguments, source selection, acquisition metadata and a compact partial summary are retained under ignored `.local/rea-research/results/keel/`. The failed operation was not replayed unchanged. The preserved partial result was reused for the findings below.

## Findings and their authority

| Finding | Basis and limitation | Wayfinder application |
| --- | --- | --- |
| The package has a broad named renderer API rather than only chat. | REA's partial preload/main analysis reports three bridge APIs, 132 exposed members and 110 handler candidates. Static identity and graph pairing have limitations. | Keep Wayfinder's existing narrow allowed methods; present only its actual supported operations. A reference application's API breadth is not a feature checklist. |
| The model context assembler has an explicit assembly stage. | Completed packaged `dist/electron/src/core/contextAssembler.js` contains `assembleContext` and source-labelled sections. No real context retrieval or transmission was observed. | Make Wayfinder's existing scoped evidence understandable with source summaries and disclosure, while keeping Iron Web as its memory system. Do not introduce Keel's file memory or automatic capture. |
| Keel's installed defaults differ from a simple “local-only” interpretation. | Packaged `dist/electron/src/core/settings.js:75–87` declares `cloudEnabled: true` for new installs; comments distinguish existing saved settings. No network traffic or actual cloud use was tested. | Show the actual approved provider, destination and disclosure scope. Avoid blanket claims that a local desktop app keeps every operation on-device. Do not import Keel's cloud, fallback or provider selection. |
| Settings include credential fields and plain JSON persistence. | Packaged settings defaults include API-key fields; `writeSettingsFile` serializes settings as JSON, and `saveSettings` writes stable/legacy locations. Main's `keel:get-settings` returns `loadSettings()` directly at `main.js:1048–1050`. These source-derived branches were inspected as inert packaged text, not exercised with credentials. | Preserve Wayfinder's main-owned encrypted vault and secret-free renderer responses. Do not copy the reference's settings transport/storage. No exploit or current-user credential exposure is claimed. |
| The export guard separates intended content from a generated completion announcement. | Completed packaged `tools/exportGuard.js` rejects several heuristic self-summary/dialog patterns. This is a content heuristic and can misclassify; no export occurred. | For existing memory and local Git changes, show exact authoritative payload and independently verified outcome. Do not rely on generated “done” text or a heuristic as authorization. Google export remains outside scope. |
| Cancellation and thinking events have dedicated bridge methods. | Packaged preload exposes chat request IDs, cancellation and thinking/stream callbacks; the minified renderer did not finish analysis. | Improve status presentation for Wayfinder's current chat/run methods. Do not claim streaming, billing cancellation or upstream abort unless its existing service actually reports them. |

## What remains unknown

The minified renderer's static/semantic analysis did not complete, so this pass does not establish its complete navigation, citation rendering, accessibility, actual layout or UI state transitions. Prior repository-source review can suggest those patterns separately, but it cannot fill this release-package analysis gap as if REA observed it.

The package's exact main/preload/core findings are static observations or source-derived explanations. BrowserWindow counts, IPC candidate pairing and absent generic sender-validation observations do not prove containment or the absence of custom validation. Actual sender enforcement, key storage behavior, network destinations, cloud consent, memory writes and provider effects were not tested. No runtime replay, blanket security approval or Wayfinder feature expansion follows from this result.
