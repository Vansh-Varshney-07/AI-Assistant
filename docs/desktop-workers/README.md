# Desktop workers: first implementation

Launch `Start-Wayfinder.ps1` from the project folder and open **Desktop workers**. Select a memory space first. Docker/FalkorDB must be available for the main application, and the existing Ubuntu-24.04/OpenShell sandbox must be running for Hermes analysis.

1. Choose one file or a folder. File access is read-only and expires after 15 minutes or application exit. Folder search matches filenames and returns bounded metadata; it does not send every matching file to a model.
2. Select a discovered file, enter a question and choose **Analyze selected file**. Only that file's bounded content is supplied to Hermes. Text results include a source reference and content hash.
3. For screen context, take/select the screenshot yourself, then choose **Share screenshot/image**. Inspect the preview and confirm sharing. **Analyze shared image** sends that image to the configured provider. This release does not capture or monitor the desktop or clipboard.
4. **Plan desktop request** produces a proposed workflow and identifies missing selections or exact parameters. A plan never executes itself.
5. Use **Stop run**, **Revoke sharing**, and **Clear result** as needed. Revocation prevents later reads and pending result delivery. It cannot recall content already transmitted to a provider. Clearing a result deletes its application record; it is not a forensic erasure guarantee.

## Worker status

| Worker | Implemented behavior |
|---|---|
| W33 Desktop Context Analyst | User-selected image → isolated Hermes vision run |
| W34 File Discovery Worker | Task-scoped, bounded read-only filename search |
| W35 Local File Analyst | Selected file → isolated Hermes analysis; document parsing reuses Hermes |
| W36 Desktop Action Planner | Schema-validated proposal/outline; no execution tools |
| W37 Desktop Action Worker | Exact-plan approval/revocation/receipt boundary implemented and tested; Windows execution locked |

W37 is not yet a qualified Windows automation connection. The default application has no desktop driver connected. A portable, signed Cua driver was exercised through a test-only adapter pinned to one synthetic process/window: one editor click was delivered, but typing was refused by its capability manifest and no file was saved. That run remains `outcome_unknown`, not completed. The private driver and test windows were stopped. A production connection still requires successful fixture acceptance and independent completion verification.

These are logical roles, not five permanent agents. Hermes owns inference through its existing `AIAgent` SDK. The application supplies authorized artifacts, orchestrates bounded jobs, and enforces permissions. No separate reasoning loop, model client, memory engine, or document parser was built.

## Supported inputs and retention

- UTF-8 text, Markdown, CSV, JSON, YAML, Python source and logs. Text extraction is limited to 60,000 characters and marked when partial.
- DOCX and XLSX use the installed Hermes reader. PDF requires an already installed, reviewed converter. Worker runs do not install missing converters automatically; unsupported extraction fails explicitly.
- Selected files are limited to 2 MiB. PNG/JPEG shares are limited to 2 MiB and 16 megapixels, stripped of metadata, and bounded to 1600 pixels per dimension for analysis. The shared bytes must match the user's preview.
- Directory discovery is bounded to 3,000 visited entries, eight levels, and 50 returned files per search. Hidden/private runtime and credential paths, links/reparse points, network/device paths and alternate data streams are excluded. Changed file identities require rediscovery.
- Grants and image shares remain in application memory. File and image artifacts processed in Hermes use a temporary separate home that is removed after the run. Analysis results persist locally in the application's SQLite store until cleared. The external model provider has its own data-handling policy.

The main assistant remains on the configured model, currently NVIDIA Lightning. W33 uses `nvidia/nemotron-3.5-super-vl-120b-a12b` on the same managed NVIDIA endpoint because Lightning is text-only. This is an isolated worker setting; it does not change the main Hermes configuration. The vision endpoint was verified against the authenticated catalog and a generated image. [NVIDIA Super VL](https://build.nvidia.com/nvidia/nemotron-3.5-super-vl-120b-a12b).

Analysis workers receive zero tools, no main-assistant memories, no shared session database, and no project instructions or user plugins. The runtime performs an explicit effective-tool check before inference. Only the trusted provider bootstrap reads the selected managed model route; its credentials remain inside the sandbox. The current bridge is qualified for the installed NVIDIA/OpenShell topology, not arbitrary providers.

## Verification

Run the focused suite with a disposable database:

```powershell
.\ops\Test-DesktopWorkers.ps1
```

By default this runs terminal-only checks, without opening any windows. It uses a uniquely named, temporary database container and never runs tests against the live persistent database. The XML report is written under ignored `.local/verification/desktop-workers.xml`. UI tests require the explicit `-IncludeUi` switch; do not use it during a terminal-only session.

The latest [terminal test report](terminal-testing-20261025.md) records the GitHub merge, live Hermes results, and the remaining W37 limit. Cedar is only the name of the fictional test data, not an application component.

The [W37 diagnosis](w37-diagnosis.md) distinguishes the default application's missing driver connection from the native test's resource-authorization failure and records the terminal-only corrections.

Verify Hermes isolation without inference:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' ops/verify-desktop-workers.py
```

The existing environment is a local fallback; use `.venv/Scripts/python.exe` when a project environment is configured. The Windows app dependencies are in `requirements.txt`; the managed Nous/NVIDIA stack is installed separately through `ops/`, not similarly named Python packages.

Run explicit hosted smoke checks with generated artifacts only:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' ops/verify-desktop-workers.py --live --output .local/desktop-workers-research/live-verification.json
```

The live script tests a generated Markdown file, Word document, image containing `CEDAR 42` on green, and a planning request with no target selected. It does not inspect personal documents, the desktop or clipboard. A single successful fixture does not establish broad model accuracy or Windows automation reliability.

The underlying [research and red-council decision](../research/desktop-workers/hermes-first-research-and-plan.md) records the rationale and remaining Windows integration gates.
