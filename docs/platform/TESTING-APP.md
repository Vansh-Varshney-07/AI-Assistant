# Test the consolidated Wayfinder app

Current build: **0.3.0 workspace-parity candidate with task profiles**. Use the Git checkout on `main`, which on this laptop is `C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant`. The original `D:\Opencode_\AI assistant` checkout and its dirty work were preserved; it is not switched to main by this integration.

## Recommended first test: isolated manual demo

From PowerShell:

```powershell
Set-Location 'C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant'
.\Start-Wayfinder.ps1 -Demo
```

The command launches the **new Electron UI**, creates a dedicated app profile/runtime and disposable database, and prints the exact path to a generated `study-source.md`. Keep that terminal open. The graph data is removed when you quit the app; this demo does not read, reset or copy your normal Iron Web data. Existing Docker, the pinned database image, cached embeddings, compatible Python and the existing managed Hermes sandbox are prerequisites. No services are installed automatically. Pass `-Python '<absolute executable>'` if automatic existing-environment selection is unavailable.

1. Wait for **Backend connected**, then create a space named `Manual demo`.
2. Open **Capabilities → Inspect runtime**. Expect compatible installed Hermes and closed tools/memory. If inspection fails, document analysis stays unavailable; no sample answer should appear.
3. Open **Agents & apps**. Confirm M00's task-routing description, eight task profiles and six app presets. Choose **A05 Knowledge & Learning**. Select the generated `study-source.md` using **Select task document**.
4. Keep the study-guide goal or enter `Create a study guide, include the retention value and one practice question, and cite the supplied source.` Press **Run selected-file task**. Read and approve the trusted disclosure for this synthetic file only.
5. Expect a real final study guide containing **42 days**, a source name/hash, one existing W35 invocation, zero delegations and unknown token/cost values. There is no simulated streaming. A failed/revoked/missing-source run must not show a successful artifact.
6. Refresh task records and reopen the completed task. This observes the recorded result without replay. Try A01 for supplied-source research or A06 for local-file analysis on the same explicitly selected file. Their selected-file variants share the handler; A01 does not claim live web retrieval.
7. Create a second space. Expect no first-space task history or facts. Return to the first space to see its records. Selecting Fitness must show deferred status and no execution button. All six provider presets must remain unqualified.
8. Optional memory check: in **Memory**, propose `me.retention_days = 30` with the statement `Synthetic remembered policy is 30 days.` Creating the review must not save it. Cancel/reject once and confirm recall is missing. Create a fresh proposal, inspect and approve its exact trusted review; recall should then return **30**. A05's file-only guide should still use the document's **42**, not silently publish or change memory.
9. For cancellation, start a new file task and press **Stop task** while it is running. Expect a cancelled record with no late successful delivery; upstream abort/billing may remain unconfirmed. Clear only a terminal task artifact when desired; this is not full memory forgetting.
10. Quit Wayfinder. The demo terminal removes only its uniquely named database. Do not reuse the demo as durable storage.

These are user-performed app interactions, not W37 automation. Do not run Cedar, capture the desktop or inspect the clipboard. The earlier automated native-dialog attempt was blocked by unreliable app-window capture; it is not counted as a pass.

## Repeat automated checks

```powershell
.\Test-Wayfinder.ps1 -Mode Regression
.\Test-Wayfinder.ps1 -Mode Frontend
.\Test-Wayfinder.ps1 -Mode Rendered
.\Test-Wayfinder.ps1 -Mode NodeBridge
.\Test-Wayfinder.ps1 -Mode NeuralLive
.\Test-Wayfinder.ps1 -Mode Packaged
```

Regression uses deterministic model fixtures and disposable storage. NeuralLive additionally makes actual synthetic managed-model calls. Rendered uses explicit UI fixtures. Packaged runs the actual Windows app hidden with real preload/main/backend and isolated storage; it does not exercise native file/approval dialogs. Detailed reports stay ignored under `desktop-app/test-results/`. Build with `Test-Wayfinder.ps1 -Mode Build` when source changes. The app is an unsigned development folder, not a standalone installer; keep `release/win-unpacked` intact.

## Normal data and accounts

For normal use, `Start-Wayfinder.ps1 -Python '<existing executable>'` uses a stable packaged app-data root. To deliberately select a compatible existing runtime, quit first and add `-Runtime '<absolute root>'`; ownership is enforced and no automatic data import occurs.

Google OAuth dependencies are prepared in this checkout's ignored `.local/google-oauth`. The actual Desktop client and token are absent. Enable the selected Calendar/Tasks/Gmail APIs in your Google project, download a **Desktop app** OAuth client to this checkout's `secrets/credentials.json`, then run `ops/Connect-Google.ps1` and complete the consent yourself. Do not paste credentials or tokens in chat. `ops/Connect-Google.ps1 -Check` performs no account access; `ops/Test-GoogleConnection.ps1 -Live` is the separate bounded read qualification after consent. Consent alone does not activate the app presets or authorize sends/writes. See [Google setup](GOOGLE-SETUP.md).

Notion needs a chosen product connection/workspace and selected content. GitHub needs selected repositories and product authorization. Codex's own connected accounts are not product credentials. Drive/Docs/Sheets require separate file/scopes and adapters. Provider reading, content projection, account generations, each reviewed write/send, scheduling and broad development execution remain separate qualification work; they are not represented as done by this demo.
