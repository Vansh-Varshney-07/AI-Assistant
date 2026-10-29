# Khoj: actual REA package investigation

Date: 27 October 2026. Static inspection only; the application was never installed, launched, connected to an account or permitted to synchronize files.

## Target and identity

This target is the **historical Khoj Desktop companion 1.33.1**, not the current server or its web interface. The former publisher download page returned 404. Microsoft's [package manifest](https://github.com/microsoft/winget-pkgs/blob/master/manifests/k/Khoj/Khoj/1.33.1/Khoj.Khoj.installer.yaml) identified the publisher's ToDesktop download; the downloaded installer matched its SHA-256:

`d395ac9790a58dc9ad1b615a1ef9ee254457e0c99a49303fac7f4e4403dc4eb3`

The installer was opened with the existing 7-Zip utility, and its inner archive's `resources/app.asar` was extracted without executing it. REA identified that ASAR as:

`3e6d74499738a75f260d80febfaa1887abc4a2e2e09b8182ace0e08ce55ee0e9`

The publisher's [current service notice](https://app.khoj.dev/) says Khoj Cloud was sunset on 15 April 2026. Historical desktop code is useful research evidence, not proof that the old hosted integration remains available.

## Actual REA execution

The cloned REA 6.8.0 CLI ran `analyze-javascript-application` against the ASAR, selecting `package.json`, `main.js`, `preload.js`, `renderer.js`, `chatutils.js` and `settings.html`. The call used a 512 MiB worker heap, 20,000 retained semantic nodes overall, 10,000 per file and a 120,000 ms per-source deadline. It exited zero in 28.578 seconds.

Analysis Evidence: `ev_4dbe24524e395ed3b38fb9002d1f6eec0bba535ea8e4eaad509a605b3f99b57a`.

REA's `inspect-analysis-view` produced summary Evidence `ev_889e61e545b2caadada6bd21d7a1153a4a152edbc4f90b3125201050876f3849`.

REA's `trace-application-feature` then traced two exact IPC-channel seeds, using the saved immutable analysis rather than rerunning it:

| Seed | Trace Evidence | Result |
| --- | --- | --- |
| `handleFileOpen` | `ev_19b785d9a15eb5f731aa0b43af7645ab87b513b873535e3052edf8fb32ba878c` | Two matching seeds; includes the preload invocation and main handler. |
| `continue-conversation-button-clicked` | `ev_0a259f6a11941dc291c825c8e09941ca3771e544f1197afac0852ab2f7e05118` | Two matching seeds in the conversation-navigation boundary. |

Both traces exited zero. Their broad reachable graphs include artifact/module relationships; they are not proof that every reachable node executes as part of these user actions.

## Findings and adaptation

- **REA observation:** four BrowserWindow declarations, 17 context-bridge APIs and 22 exposed members. File selection and return-to-conversation have explicit IPC entry points. Wayfinder can make the corresponding existing file-selection and result-navigation steps easier to follow while retaining its single named bridge.
- **REA observation:** three recovered windows explicitly set `nodeIntegration: true`, at `main.js` lines 444–454, 519–530 and 689–699. Preserve Wayfinder's `nodeIntegration: false`, context isolation and sandbox settings. These are declaration observations, not a demonstrated exploit or a conclusion about every window's effective defaults.
- **Packaged-code inspection, supplementary to REA:** the settings window distinguishes file/folder configuration, while main-process code schedules uploads repeatedly. The preload also contains token and clipboard-related APIs. Wayfinder's design should show exactly which selected file is being read and disclosed; it should not acquire background synchronization or clipboard access from this reference.
- **Design choice:** apply the understandable choose-source → inspect → return-to-work interaction to existing Documents and Connections. The earlier Khoj source-pane recommendation still rests on the separately reviewed web-interface source; this desktop companion does not qualify that web UI through REA.

## Coverage and retained evidence

REA read 69,447 selected text bytes and parsed four JavaScript files without parse failures. Of 1,086 relevant inventoried files, 1,080 were outside the selected source scope. It explicitly did not analyze an inline JavaScript body in `settings.html`. The 18 renderer transmissions remained ambiguously paired; matching channel names alone do not prove handler identity. No runtime IPC enforcement, provider behavior, file synchronization or visual/accessibility behavior was tested.

Original commands, stdout, stderr, exit records, Evidence, summaries and traces are retained locally under `.local/rea-research/results/khoj/`. Acquisition metadata is under `.local/rea-research/artifacts/khoj/`. These large artifacts remain ignored by the Wayfinder repository.
