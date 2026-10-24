# AI assistant setup

Target project: `D:\Opencode_\AI assistant`.

Consolidation scope: only the files formerly inside `D:\Opencode_\memory_system`, plus the new setup files requested for this assistant. The larger research-paper repositories are separate projects. Extra research report copies were removed after verifying their originals remain in the research chat's output folder. Existing memory data stays private and ignored by Git. The existing database volume remains `memory_system_falkordb_data` to preserve its data.

The old `D:\Opencode_\memory_system` path is a compatibility junction to this folder. Existing report files retain historical names and observations. The Python package remains `memory` so imports continue to work.

## Dedicated Ubuntu

`Ubuntu-24.04` is the newly downloaded distribution for this project. The original `Ubuntu` distribution is Ubuntu 26.04 and remains separate.

The user explicitly approved installation in `Ubuntu-24.04` on 2026-10-24. `ubuntu-prerequisites.sh` has completed as root only in the new distribution. It installed prerequisite packages and created the unprivileged, password-locked `assistant` user without sudo membership. This account is the default only for the new distribution; the global default WSL distribution was not changed.

`prepare-user.sh` completed as `assistant`. It verified the pinned NVM installer checksum, installed Linux Node.js **22.23.4** and npm **10.9.9**, and created the shortcut `/home/assistant/ai-assistant` to the canonical project on D:. Python **3.12.3** and Git **2.43.0** are available. Linux Git can access the same project repository.

Docker Desktop integration must be enabled for this distribution. Applying Docker settings may restart Docker and interrupt running containers, so coordinate that step first.

Run `install-stack.sh` as `assistant` after Docker is reachable. The installer uses a recorded immutable revision of the maintained NVIDIA release and disables optional completion telemetry. Host CLI installation precedes sandbox creation; installing the CLI alone does not mean Hermes is running.

## Inference onboarding

Use Nebius Token Factory for the hackathon: `https://api.tokenfactory.nebius.com/v1/` with model `nvidia/Nemotron-3_5-Lightning`. Validate Ultra separately as `nvidia/Nemotron-3-Ultra-550b-a55b`.

Enter a Token Factory API key through the supported local credential prompt/form, never into chat or tracked files. Select Hermes, a loopback-only dashboard, and a restrictive policy compatible with the selected provider. Optional messaging and search are deferred.

Use `nemohermes onboard` with the documented custom OpenAI-compatible provider. Do not accept local-model Express setup: this project intends to use Token Factory. Provider configuration, credential collection and an actual model response must pass before reporting setup complete.

## Verification

Check the host CLI and OpenShell versions, actual sandbox status, Hermes health, loopback dashboard, tool-call execution and model route. Check that the existing memory workbench still loads and that its database volume is unchanged. Run the existing focused workbench and memory-space tests after the project move.

Git setup is local only. No remote repository will be created or code published without selecting the remote destination. Private data, credentials, runtime disks and local logs must remain ignored.

## Current state

Verified on 2026-10-24:

- The standalone project was moved to `D:\Opencode_\AI assistant`; the old path redirects here.
- Only the former standalone project's files were consolidated. Extra report copies were removed to follow the user's clarified scope. Larger research repositories remain in their original locations.
- Local Git was initialized on `main`. Private data, credentials, logs and runtime disks are ignored.
- The existing workbench was restarted and its health endpoint returned online at `http://127.0.0.1:3352/health`.
- The database still uses the existing `memory_system_falkordb_data` Docker volume.
- Focused relocation checks passed: **48 passed, 1 deselected** across `test_workbench.py`, `test_memory_spaces.py`, and `test_hosted_boundaries.py`. These checks use deterministic embeddings and isolated test storage; they do not verify hosted model quality.
- The three relocated validation scripts compile. A pattern scan of 133 candidate Git files found no likely credentials; this is a limited pattern scan, not a guarantee.

The workbench currently uses the existing Windows Python environment at `D:\Opencode_\reserchpaper\.venv` and its existing private NVIDIA credential file. Creating a dedicated Ubuntu runtime and connecting the assistant to this memory service are still pending.

The new `Ubuntu-24.04` distribution is registered (Ubuntu 24.04.5 LTS, WSL 2). The original Ubuntu 26.04 distribution is separate. The earlier installation approval block was resolved by explicit user approval; prerequisites and the project account are now installed. Hermes, NemoClaw and OpenShell are **not installed or running in the new distribution** yet.

The current blocker is Docker Desktop WSL integration: a check from the assistant account returned Docker's instruction to enable integration. Open **Docker Desktop → Settings → Resources → WSL Integration**, enable **Ubuntu-24.04**, and apply. Applying may briefly interrupt existing containers. No Docker restart has been initiated by the setup scripts.

Once Docker integration is ready, execute the prepared managed installer from PowerShell:

```powershell
wsl -d Ubuntu-24.04 -u assistant -- bash '/mnt/d/Opencode_/AI assistant/ops/install-stack.sh'
```

The official installer will present its Apache 2.0 / third-party software notice. Completing host installation is followed by credential onboarding and sandbox verification; a successful host install alone does not complete the assistant setup.

Run the focused checks from the project directory with an installed development environment:

```powershell
python -m pytest -q -p no:cacheprovider --tb=short --maxfail=1 --basetemp .local/tests-relocation tests/test_workbench.py tests/test_memory_spaces.py tests/test_hosted_boundaries.py
```
