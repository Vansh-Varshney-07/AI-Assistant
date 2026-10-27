# Handrail 0.1.9 — actual REA package investigation

Date: 27 October 2026. Scope: static release-package analysis for Wayfinder security and UI/UX planning. No Handrail process was launched; no desktop capture, clipboard inspection, provider request or account access occurred.

## Target and execution evidence

- Publisher release: [M19K/handrail v0.1.9](https://github.com/M19K/handrail/releases/tag/v0.1.9), asset `Handrail.0.1.9.exe`, 99,584,005 bytes.
- Download SHA-256: `07e1efd9aaeef0efc811b225ac03ed7d61e7eec2c0c0262d253cd630436500c5`, matched GitHub's published asset digest.
- Existing 7-Zip extracted the NSIS container's `$PLUGINSDIR/app-64.7z`, then `resources/app.asar`, without executing the installer.
- ASAR SHA-256: `a0c87f060da1febac7d2bbb227c74d0bd02120abbad877d9d4e479d65fe99a0a`.
- Tool: cloned REA 6.8.0 CLI, Node 24.22.1. Source selection: package metadata; main/preload; IPC, storage, window and turn modules; overlay JS/HTML and onboarding JS. Exact arguments and selections are retained privately under `.local/rea-research/results/handrail/`.

Executed CLI operations:

```text
node rea/scripts/rea.mjs analyze-javascript-application <Handrail app.asar>
  --source-paths-json <selected-sources.json> --max-heap-mb 768
  --analysis-timeout-ms 60000 --format json
node rea/scripts/rea.mjs trace-application-feature <trace-channel-input.json> --format json
```

The trace input contains the complete returned application Evidence and seed `{kind:"channel", value:"hr:setup:validate", match:"exact"}`, direction `both`. An initial trace used the unsupported kind `ipc-channel`; its validation error and exit 1 are retained. The corrected query was a new request conforming to REA's returned schema.

| Result | Actual outcome |
| --- | --- |
| Application analysis | Exit 0; 25.028 seconds; 8 JavaScript sources parsed; zero parse failures; 10 requested sources, 15 inventoried files outside selected scope |
| Application Evidence | `ev_1e31f87ecd84f84bdc0cc32a8887f3979a7c7855209a4bf8c3b7760e700273a9` |
| Feature trace | Exit 0; 2 matching channel nodes, 356 traced nodes, 396 edges and 45 terminal paths; partial source coverage |
| Trace Evidence | `ev_63154a263d3cd37f980100ba9ec55b434993fc8307aabebbae5cb83057d50824` |

REA recovered three BrowserWindow constructions, one context-bridge API, 34 exposed API members, 31 literal channels and 32 main-handler candidates. The 29 renderer transmissions remain ambiguously paired. These are static observations/inferences, not proof of runtime registration or enforcement.

## Findings and their authority

| Finding | Basis and limitation | Wayfinder application |
| --- | --- | --- |
| One named preload API makes the renderer boundary understandable. | REA observes `contextBridge.exposeInMainWorld('handrail', …)` in packaged `preload.js:30–110`; the member inventory is an AST-static observation. It is not an authorization verdict. | Retain Wayfinder's named preload methods and sender checks; give new UI components no generic IPC, file or shell bridge. |
| Setup decisions belong to a dedicated trusted surface. | Packaged `src/main/ipc.js:246–270` checks `event.sender` against the onboarding window before setup handlers. REA's generic `sender_validation_observations` count is zero, illustrating a recognition limit; it does not mean checks are absent. | Keep main-owned import/confirmation and service-side validation. A renderer page or model response cannot approve a change. |
| A request ID is established before dispatch and late turn events are ignored. | Packaged `renderer/overlay.js:293–329` sets the ID before `bridge.ask`; `:360–369` drops events belonging to another turn. This source-derived lifecycle explanation is consistent with the analyzed package, not a runtime race test. | Use existing Wayfinder request IDs/scope epochs to keep delayed results from appearing in a different space, chat or run. Reconnect must observe, not replay. |
| Statuses distinguish capture, thinking, result and completion. | Packaged overlay's single event switch and `showBusy` rendering were inspected; no actual layout or animation was observed. | Reuse the status pattern for Wayfinder's existing queued/running/stopping/result/error states. Do not add capture, watching or pointing features. |
| The encryption policy includes a plaintext fallback. | Packaged `src/main/store.js:166–202` uses OS encryption when available but writes a labelled base64/plaintext record otherwise. This is an observed static branch; no real key was imported. | Preserve Wayfinder's stronger fail-closed vault behavior. Explain encryption errors and offer re-import; never silently fall back to plaintext. |
| Capture and step watching are enabled in Handrail defaults. | Packaged `src/main/store.js:27–30` declares capture/pointing/stealth/watching defaults; execution and actual permissions remain untested. | Exclude these defaults entirely. Wayfinder's native UI/capture boundary remains disabled. |

## Limits and retained material

The exact release and extracted ASAR were analyzed, not the repository's current HEAD. Complete application and trace JSON, stderr, original exit codes, selections, command arguments, acquisition metadata and compact summaries are retained in ignored local research storage. Selected packaged files were read as text through the ASAR library for corroboration; those reads are identified as source-derived observations rather than additional REA tools.

Both graphs retain partial coverage and unknowns. A matched IPC channel and reachable inferred graph do not prove a complete renderer-to-handler path, authorization enforcement or exploitability. Defaults not explicitly declared by the application remain unproven. No native, visual, accessibility, provider, OS keychain or actual cancellation behavior was tested. These findings inform Wayfinder's existing features only.
