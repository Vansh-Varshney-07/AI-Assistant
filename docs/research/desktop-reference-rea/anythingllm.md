# AnythingLLM: actual REA package investigation

Date: 27 October 2026. Static inspection only; no installer or application code was executed and no screen or clipboard was accessed.

## Target and identity

Target: the official [AnythingLLM Desktop 1.19.0 Windows release](https://github.com/Mintplex-Labs/anything-llm/releases/tag/v1.19.0), `AnythingLLMDesktop.exe`, 403,299,096 bytes. Downloaded bytes matched GitHub's published SHA-256:

`743d10ddf920087b46cd614cafd2e0e31550089405436f00cbd827c43ca4c90a`

The existing 7-Zip utility extracted the installer archive and its packaged ASAR without launching the installer. REA bound its findings to ASAR SHA-256:

`6f336dfd08c06a42f1ed2633d3d11aa2d116b6accb2dfe1b3ac2a788a9dfea28`

This directly studies shipped desktop code, supplementing the earlier documentation and public web-client source review.

## Actual REA execution and recovery

The first cloned REA 6.8.0 `analyze-javascript-application` call selected `package.json`, `dist-electron/main/index.js`, `dist-electron/preload/index.js`, `dist/assistant.html` and `dist/assets/assistant-ca9cac1f.js`.

The 1.6 MB minified main bundle reached the explicit 120,000 ms per-source provider deadline. The command exited one after 160.39 seconds including finalization, retaining partial Evidence:

`ev_0fcf819f82b41d75a3385c819b88cbff8e2c3fb5279cb2aa4ad277fe6c35fa86`

That result is a **partial timed-out analysis**, not a passed full analysis. Its retained static facts include 82 literal main-process handlers. Minified aliases and unfinished semantic work leave other boundaries unresolved; zero recovered BrowserWindow or renderer observations cannot be interpreted as absence.

Following REA's returned recovery guidance, the main analysis was not repeated. A second call analyzed only the previously unprocessed preload, assistant HTML and 119 KB assistant renderer bundle, plus the package metadata, with smaller retained semantic limits. It exited zero in 44.97 seconds and produced:

`ev_e243e2b9c261bb7f60063af2951e2c5a9fecdd05e5bb7ea45c08e2dad5415f30`

REA's `trace-application-feature` then reused each saved Evidence record:

| Trace | Evidence |
| --- | --- |
| Exact `get-preference` channel in the partial main analysis | `ev_e1f92026f9b8045436ce31b9db8522b0f4db5eb0a97eb8cddb58a341ea52e6d7` |
| Exact assistant module in the successful remaining-source analysis | `ev_f7bd21f6927ca94b86ea9ec93ddd7000654713e5b931569a2103a2a6222654fe` |

Both trace commands exited zero. The records remain separate; no combined or fictitious complete-application Evidence identity was created.

## Findings and adaptation

- **REA observation:** the packaged main bundle has explicit preference IPC handlers. The assistant module and its imports are present in the shipped application graph. Use this separation as a reference for clear existing preferences and conversation state, rather than introducing a new Wayfinder runtime.
- **Packaged-byte inspection supporting the UI interpretation:** the assistant renderer reads an open-thread preference and retains assistant state; it distinguishes aborted/error responses from session-completion responses. Wayfinder can improve existing conversation continuity, stop/error messages and settings discoverability using its current chat IDs and handlers.
- **Packaged-byte inspection:** the renderer also requests pending screenshot context. That mechanism and its global-overlay behavior are outside Wayfinder's authorized feature set. Apply fast navigation through the existing in-app palette, without copying capture or adding a global overlay.
- **Packaged-byte inspection:** some window configuration literals include Node integration and disabled context isolation. REA did not fully resolve their minified ownership, so they are not presented as a whole-application security verdict. Wayfinder should retain its independently enforced isolated renderer, named IPC, denied browser permissions and final-handler grants.
- **Design choice:** show actual context and run outcomes plainly; offer expandable parameters and evidence. Do not import this product's capture, background-agent, voice, provider or automatic-disclosure behavior.

## Coverage and retained evidence

The first call parsed one JavaScript file before timeout and retained 381 static findings; other requested sources remained skipped or incomplete. The second parsed two JavaScript files with no parse failures and 447 static findings. It left 1,982 inventoried files outside its selection. Its zero IPC-operation count reflects unresolved imported bridge ownership, not proof that the renderer has no IPC.

The feature graphs contain static observations, inferred relationships and unavailable facts. Ten native handoffs are candidates requiring further native-provider analysis, not completed decompilations. No global-shortcut, capture, permission enforcement, provider request, visual layout or accessibility behavior was tested at runtime.

Original commands, stdout/stderr, nonzero timeout result, partial Evidence, corrected selection, successful follow-up and traces are retained under `.local/rea-research/results/anything-llm/`. Acquisition metadata is under `.local/rea-research/artifacts/anything-llm/`. These artifacts remain ignored.
