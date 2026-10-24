# AI assistant setup

Target project: `D:\Opencode_\AI assistant`.

Consolidation scope: the standalone memory project and copies of the assistant research reports. The larger research-paper repositories are separate projects. Existing memory data stays private and ignored by Git. The existing database volume remains `memory_system_falkordb_data` to preserve its data.

The old `D:\Opencode_\memory_system` path is a compatibility junction to this folder. Existing report files retain historical names and observations. The Python package remains `memory` so imports continue to work.

## Dedicated Ubuntu

`Ubuntu-24.04` is the newly downloaded distribution for this project. The original `Ubuntu` distribution is Ubuntu 26.04 and remains separate.

After explicit installation approval, execute `ubuntu-prerequisites.sh` as root only in the new distribution. It installs prerequisite packages and creates the unprivileged, password-locked `assistant` user. It does not change sudo privileges.

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
- The research HTML and PDF reports are in `research/`. Larger research repositories remain in their original locations.
- Local Git was initialized on `main`. Private data, credentials, logs and runtime disks are ignored.
- The existing workbench was restarted and its health endpoint returned online at `http://127.0.0.1:3352/health`.
- The database still uses the existing `memory_system_falkordb_data` Docker volume.
- Focused relocation checks passed: **48 passed, 1 deselected** across `test_workbench.py`, `test_memory_spaces.py`, and `test_hosted_boundaries.py`. These checks use deterministic embeddings and isolated test storage; they do not verify hosted model quality.
- The three relocated validation scripts compile. A pattern scan of 133 candidate Git files found no likely credentials; this is a limited pattern scan, not a guarantee.

The workbench currently uses the existing Windows Python environment at `D:\Opencode_\reserchpaper\.venv` and its existing private NVIDIA credential file. Creating a dedicated Ubuntu runtime and connecting the assistant to this memory service are still pending.

The new `Ubuntu-24.04` distribution is downloaded and registered (Ubuntu 24.04.5 LTS, WSL 2). The original Ubuntu 26.04 distribution is separate. Automatic approval review blocked prerequisite installation and account creation; explicit confirmation is pending. Neither setup script has been executed. Hermes, NemoClaw and OpenShell are **not installed or running in the new distribution** yet. Docker Desktop integration must also be enabled there before the managed installation.

Run the focused checks from the project directory with an installed development environment:

```powershell
python -m pytest -q -p no:cacheprovider --tb=short --maxfail=1 --basetemp .local/tests-relocation tests/test_workbench.py tests/test_memory_spaces.py tests/test_hosted_boundaries.py
```
