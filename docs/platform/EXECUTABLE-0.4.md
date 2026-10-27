# Wayfinder 0.4: onboarding and a bundled local backend

This is a usable local assistant candidate, with a portable Windows x64 executable, first-run setup, a bundled Python backend and a public CPU memory model. It reuses Wayfinder's authenticated service, Iron Web, scoped file broker, existing approval controls, WorkerHub and the installed Hermes/OpenShell runtime. It adds no agent framework or memory engine.

## First launch

1. Start Docker Desktop with its local Linux engine. The managed Ubuntu/OpenShell Hermes installation and configured model provider must already exist on this computer.
2. Double-click **Wayfinder-0.4.0-Windows-x64.exe**. No Python installation or development checkout is needed. Extraction needs approximately 1 GB of temporary disk space; keep the executable while using the app.
3. In setup, prepare the private database, verify the bundled memory model, and check Hermes. Downloading the fixed database image is a separate explicit button if it is absent.
4. Review the actual model, provider and endpoint. Enter a space name and accept the displayed chat disclosure, then create the workspace.

The app starts its own labelled, password-protected FalkorDB container on a random loopback port. It preserves its persistent volume on quit. It refuses foreign volumes, remote Docker engines, changed launch settings and an image that differs from the verified AMD64 release. Docker and Hermes are prerequisites, not bundled services.

The new workspace is in the app's per-user `workspace-v1` directory. Old development/runtime data is preserved and is not silently migrated. Onboarding settings contain public route details and the selected space; provider credentials remain in the managed Hermes environment. The database key is local private app state and is never a renderer response or repository file.

## Try it as a new user

1. Open **Chat**, select **New conversation**, and write “For this conversation, my test colour is amber.” Ask “What test colour did I give you?” The second request uses bounded completed history.
2. Quit Wayfinder normally, reopen the same executable, and select that conversation. Completed messages should remain.
3. Open **Memory**. Chat should not have automatically published that colour as a fact. Propose a synthetic fact and reject its review; recall should still report missing evidence.
4. To deliberately store a fact, create a new proposal, inspect the exact change, and approve it in the app's confirmation dialog. Verify recall and restart persistence. This manual approval-dialog check is separate from automated tests.
5. In **Documents**, explicitly select a UTF-8 document and review the disclosure before analysis. File grants expire and must be selected again after restart.

Conversation input is bounded to 4,000 UTF-8 bytes. Up to six recent completed pairs within an 18 KB serialized context are sent to the approved model. Failed or cancelled turns are omitted. Older turns are paginated. A changed model/provider requires setup review. Expired runtime inspection is refreshed before dispatch.

Cancelled, failed and uncertain requests are never automatically replayed. A durable turn reservation and immutable input digest prevent a duplicate request ID from changing its message. Restart reconciles a recorded worker result where available; unresolved turns become interrupted. Cancellation does not prove upstream abort or billing cessation. Token and cost telemetry are unavailable.

## Boundaries and dependencies

Google Calendar/Tasks, Gmail, Notion, hosted GitHub actions, fitness, scheduling, quick chat, arbitrary workflow building and native desktop actions are not qualified in this build. Their planned presence does not mean account connectivity. W37 and screen/clipboard access remain disabled. This is an unsigned local build, not an installer that provisions all external services.

The bundled memory weights are the public quantized [Qdrant BGE small model](https://huggingface.co/qdrant/bge-small-en-v1.5-onnx-q), based on [BAAI BGE](https://huggingface.co/BAAI/bge-small-en-v1.5). Public model, Python, bundled dependency and font notices are included. The installed Python runtime's explicit public certificate-policy file is retained; TLS verification was not disabled to fix packaging.

## Verification and rebuilding

Synthetic fixtures and disposable storage are mandatory. `scripts/verify-onboarding.mjs` runs the actual packaged app hidden, completes onboarding against an owned private test database, performs two real Hermes turns, checks no automatic memory writes, and restarts. It does not capture the desktop, use native automation, connect Google, or open Cedar. Its database cleanup is limited to exact labels derived from its newly created test profile.

`scripts/check-onboarding-package.mjs` checks the packaged archive, backend/source/model hashes, trust-policy inclusion, notices, absence of private state, and pairing with the actual packaged test. Older 0.3 reports remain historical evidence and are not substituted for this acceptance.

Build with the verified Python 3.12 environment and locally installed PyInstaller 6.16 tools: run `scripts/freeze-backend.py`, then `npm run package` inside `desktop-app`. `--stage-only` refreshes public source/assets after an existing freeze; it is not a substitute for freezing changed entry-point/dependency code. Never copy `.env`, user profiles, provider tokens or entire model caches into release resources.
