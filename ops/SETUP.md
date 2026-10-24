# AI assistant setup

Target project: `D:\Opencode_\AI assistant`.

Consolidation scope: only the files formerly inside `D:\Opencode_\memory_system`, plus the new setup files requested for this assistant. The larger research-paper repositories are separate projects. Extra research report copies were removed after verifying their originals remain in the research chat's output folder. Existing memory data stays private and ignored by Git. The existing database volume remains `memory_system_falkordb_data` to preserve its data.

The old `D:\Opencode_\memory_system` path is a compatibility junction to this folder. Existing report files retain historical names and observations. The Python package remains `memory` so imports continue to work.

## Dedicated Ubuntu

`Ubuntu-24.04` is the newly downloaded distribution for this project. The original `Ubuntu` distribution is Ubuntu 26.04 and remains separate.

The user explicitly approved installation in `Ubuntu-24.04` on 2026-10-24. `ubuntu-prerequisites.sh` has completed as root only in the new distribution. It installed prerequisite packages and created the unprivileged, password-locked `assistant` user without sudo membership. This account is the default only for the new distribution; the global default WSL distribution was not changed.

`prepare-user.sh` completed as `assistant`. It verified the pinned NVM installer checksum, installed Linux Node.js **22.23.4** and npm **10.9.9**, and created the shortcut `/home/assistant/ai-assistant` to the canonical project on D:. Python **3.12.3** and Git **2.43.0** are available. Linux Git can access the same project repository.

Docker Desktop integration was enabled for this distribution after the user instructed the assistant to perform it. Existing default-distro integration settings were preserved. The Linux engine **28.3.3** is reachable from the unprivileged assistant account.

`install-stack.sh` completed as `assistant` after Docker became reachable. The installer used the recorded immutable NVIDIA revision `f00fb1dafe2113940b89bcd82f0561adf2696a7b` and disabled optional completion telemetry. Installed versions were independently checked: **NemoClaw / NemoHermes CLI 0.0.137**, **OpenShell 0.0.116**. The OpenShell release archives passed the installer's SHA-256 checks. Host CLI installation precedes sandbox creation; installing the CLI alone does not mean Hermes is running.

## Inference onboarding

Recommended hackathon route: Nebius Token Factory, `https://api.tokenfactory.nebius.com/v1/`, with model `nvidia/Nemotron-3_5-Lightning`. Validate Ultra separately as `nvidia/Nemotron-3-Ultra-550b-a55b`. The user has been asked to choose Token Factory or authorize reuse of the existing local NVIDIA workbench credential; no provider has been configured yet.

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

The new `Ubuntu-24.04` distribution is registered (Ubuntu 24.04.5 LTS, WSL 2). The original Ubuntu 26.04 distribution is separate. The earlier installation approval block was resolved by explicit user approval; prerequisites, the project account, NemoClaw/NemoHermes CLI and OpenShell are installed. `nemohermes list` reports **no sandboxes registered**. The installed OpenShell user service is disabled and inactive until onboarding. The **Hermes agent runtime is not yet deployed**, and no live assistant model call has been verified.

Docker Desktop WSL integration is now ready. The required restart encountered a stale `dockerInference` socket startup failure. Following the reversible workaround described in [Docker's issue tracker](https://github.com/docker/desktop-feedback/issues/554), setup preserved only the temporary `Docker\run` directory under `run.stale-ai-assistant-20261024094724` and let Docker recreate it. No container images, volumes, or database directories were removed. The previous settings file is backed up under ignored `.local/`.

Both existing containers, `memory-system-falkordb` and `iron-web-2-falkordb`, were restored to running and then verified healthy. The workbench health endpoint returned online after recovery.

The prepared managed installer has already completed. For a future repair/reinstallation, its command from PowerShell is:

```powershell
wsl -d Ubuntu-24.04 -u assistant -- bash '/mnt/d/Opencode_/AI assistant/ops/install-stack.sh'
```

The installer used its standard Apache 2.0 / third-party notice acceptance option under the approved software setup. Credential onboarding and sandbox verification remain. A successful host install alone does not complete the assistant setup.

## Dependency audit findings

`npm audit --omit=dev --json` was run separately for the host CLI and plugin after installation. The host CLI reported **four production dependency findings: one high and three moderate**, with **zero critical production findings**. Affected package entries are `undici` (high), `fast-uri`, `ajv`, and `smol-toml` (moderate). The plugin reported **zero production findings**. These counts are time-sensitive; development/build dependency findings printed during installation have higher totals.

The findings remain unresolved in the pinned upstream installation. No automatic dependency upgrade or forced audit fix was applied, because it would alter the managed dependency set without proving compatibility. This setup must not be described as free of dependency vulnerabilities. Reproduce the audit with `ops/audit-stack.sh` (host) and `ops/audit-stack.sh plugin` inside the assistant account. Raw reports are retained privately in `/home/assistant/ai-assistant-install/` and copied to the project's ignored `.local/` directory.

- [Undici excessive-content-encodings denial of service](https://github.com/advisories/GHSA-xjj6-f33q-929c)
- [fast-uri URI scheme spoofing](https://github.com/advisories/GHSA-w74x-v6f9-j3xg)
- [smol-toml parsing complexity](https://github.com/advisories/GHSA-r4xh-jqrq-34v2)

Run the focused checks from the project directory with an installed development environment:

```powershell
python -m pytest -q -p no:cacheprovider --tb=short --maxfail=1 --basetemp .local/tests-relocation tests/test_workbench.py tests/test_memory_spaces.py tests/test_hosted_boundaries.py
```
