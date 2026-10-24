# AI assistant setup

Target project: `D:\Opencode_\AI assistant`.

Consolidation scope: only the files formerly inside `D:\Opencode_\memory_system`, plus the new setup files requested for this assistant. The larger research-paper repositories are separate projects. Extra research report copies were removed after verifying their originals remain in the research chat's output folder. Existing memory data stays private and ignored by Git. The existing database volume remains `memory_system_falkordb_data` to preserve its data.

The old `D:\Opencode_\memory_system` path is a compatibility junction to this folder. Existing report files retain historical names and observations. The Python package remains `memory` so imports continue to work.

## Use the assistant

Open the [Hermes dashboard](http://127.0.0.1:18789/). Docker Desktop and the dedicated Ubuntu distribution must be running. The local bearer-authenticated API is `http://127.0.0.1:8642/v1`.

To chat from a PowerShell terminal:

```powershell
wsl -d Ubuntu-24.04 -u assistant -- /home/assistant/.local/bin/nemohermes launch ai-assistant
```

The OpenShell user service is enabled, active and configured to start when this distribution starts, with user lingering enabled. Windows login startup and sleep/wake behavior have not been configured or qualified as an always-on deployment.

## Dedicated Ubuntu

`Ubuntu-24.04` is the newly downloaded distribution for this project. The original `Ubuntu` distribution is Ubuntu 26.04 and remains separate.

The user explicitly approved installation in `Ubuntu-24.04` on 2026-10-24. `ubuntu-prerequisites.sh` has completed as root only in the new distribution. It installed prerequisite packages and created the unprivileged, password-locked `assistant` user without sudo membership. This account is the default only for the new distribution; the global default WSL distribution was not changed.

`prepare-user.sh` completed as `assistant`. It verified the pinned NVM installer checksum, installed Linux Node.js **22.23.4** and npm **10.9.9**, and created the shortcut `/home/assistant/ai-assistant` to the canonical project on D:. Python **3.12.3** and Git **2.43.0** are available. Linux Git can access the same project repository.

Docker Desktop integration was enabled for this distribution after the user instructed the assistant to perform it. Existing default-distro integration settings were preserved. The Linux engine **28.3.3** is reachable from the unprivileged assistant account.

`install-stack.sh` completed as `assistant` after Docker became reachable. The installer used the recorded immutable NVIDIA revision `f00fb1dafe2113940b89bcd82f0561adf2696a7b` and disabled optional completion telemetry. Installed versions were independently checked: **NemoClaw / NemoHermes CLI 0.0.137**, **OpenShell 0.0.116**, and sandboxed **Hermes Agent 0.21.3**. The OpenShell release archives passed the installer's SHA-256 checks. Sandbox `ai-assistant` is deployed and verified running.

## Inference onboarding

The user explicitly selected reuse of the existing NVIDIA workbench credential. Provider **nvidia-prod** uses `https://integrate.api.nvidia.com/v1`, with **nvidia/nemotron-3.5-lightning-30b-a3b** active. The authenticated NVIDIA catalog also listed **nvidia/nemotron-3-ultra-550b-a55b**; Ultra has not been selected or separately exercised through Hermes in this setup.

`onboard-nvidia.mjs` reads only `NVIDIA_API_KEY` from the authorized local `.env` file and supplies `NVIDIA_INFERENCE_API_KEY` to the official CLI through its child environment. It does not print the key or copy the credential file. The managed provider stores the credential outside the Git checkout. Messaging and web search are disabled; no project host directory was mounted into the sandbox.

The sandbox uses the release's **balanced** policy with npm, PyPI, Hugging Face and Homebrew presets. This grants selected package-host egress; it is not an inference-only network policy. GPU passthrough is disabled. Nebius Token Factory remains a possible later provider migration and is not configured here.

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

The new `Ubuntu-24.04` distribution is registered (Ubuntu 24.04.5 LTS, WSL 2). The original Ubuntu 26.04 distribution is separate. The earlier installation approval block was resolved by explicit user approval. Sandbox `ai-assistant` is **Ready**, Hermes is **running**, and the OpenShell managed service is **enabled and active**. NVIDIA onboarding's live inference smoke passed; the local Hermes API then successfully completed both a real model request and an independently verified tool action.

Docker Desktop WSL integration is now ready. The required restart encountered a stale `dockerInference` socket startup failure. Following the reversible workaround described in [Docker's issue tracker](https://github.com/docker/desktop-feedback/issues/554), setup preserved only the temporary `Docker\run` directory under `run.stale-ai-assistant-20261024094724` and let Docker recreate it. No container images, volumes, or database directories were removed. The previous settings file is backed up under ignored `.local/`.

Initial Docker recovery restored both database containers, but the final persistence checks found restart loops during their subsequent startup. See the database recovery section below for current state; an online workbench HTTP endpoint alone does not prove database health.

After refreshing the assistant account's Docker group membership, Docker Desktop's WSL integration proxy required reconnection and a clean Desktop restart. Temporary client binaries were extracted from the already-installed Docker Desktop ISO while diagnosing its empty injected CLI directory. The maintained CLI bundle was restored after Desktop restart; the temporary account-level copies were removed only after byte comparisons. The final native client is `/usr/bin/docker` (28.3.3), with Compose 2.39.2-desktop.1 and Buildx 0.27.0-desktop.1. The managed gateway no longer depends on the standalone startup fallback.

The prepared managed installer has already completed. For a future repair/reinstallation, its command from PowerShell is:

```powershell
wsl -d Ubuntu-24.04 -u assistant -- bash '/mnt/d/Opencode_/AI assistant/ops/install-stack.sh'
```

The installer used its standard Apache 2.0 / third-party notice acceptance option under the approved software setup. Credential onboarding and sandbox verification completed. The standalone memory service has not yet been connected to Hermes through an API/tool bridge; moving its source files does not automatically integrate it with the agent.

## Live assistant checks

| Check | How | Result |
| --- | --- | --- |
| NVIDIA credential and catalog | Authenticated `GET /v1/models`; only model IDs printed | Passed; Lightning and Ultra listed |
| Upstream inference | Official NVIDIA onboarding smoke | Passed with Lightning |
| Dashboard | HTTP request from both Ubuntu and Windows | HTTP 200; Hermes dashboard HTML |
| Local model listing | Bearer-authenticated `GET /v1/models` | HTTP 200; `hermes-agent` |
| Authentication enforcement | Chat request without a bearer token | HTTP 401 |
| Agent model response | Authenticated chat requesting `SETUP_SMOKE_OK` | HTTP 200; expected marker received |
| Terminal tool | Agent asked to write `/sandbox/setup-smoke-tool.txt` | Expected response marker received |
| Independent tool check | Docker exec compared the file content to `SETUP_TOOL_OK` | Passed |
| Runtime and policy | `nemohermes ai-assistant status` | Ready; Hermes 0.21.3 running; Lightning selected |

`ops/verify-hermes.mjs` reproduces the API tests while obtaining the local token in memory and keeping it out of output. It deliberately does not claim independent tool verification; inspect the test file separately. The completed evidence, including independent verification, is in ignored `.local/hermes-smoke-results.json`. These checks verify the installation path, not broad task accuracy or long-term reliability.

## Database persistence recovery

Both existing FalkorDB 4.20.7 instances crashed with signal 11 in `GraphContext_GetSchemaByID` while replaying `GRAPH.EFFECT` operations for test-prefixed graphs. This matches the failure class described in [FalkorDB issue 2201](https://github.com/FalkorDB/FalkorDB/issues/2201).

The originals are stopped to prevent the crash loops; their persistence files have not been changed. Full checksummed archives are saved under ignored `.local/database-recovery/20261024-111839-df443c/`. Isolated copies using the same image started successfully after filtering **only GRAPH commands whose graph keys match test-owned prefixes**. All other commands were retained byte-for-byte. The memory copy removed 18,587 test commands and loaded 3 graphs; the research copy removed 1,927 test commands and loaded 87 graphs.

Applying the validated repair is awaiting explicit approval because it changes persistence files and one affected store is outside the consolidated project. No database reset, deletion of the original volume, or major-version upgrade has been performed. Do not rerun the existing tests against the persistent service while this upstream AOF issue remains unresolved; test graph isolation alone does not isolate the shared persistence log.

## Dependency audit findings

`npm audit --omit=dev --json` was run separately for the host CLI and plugin after installation. The host CLI reported **four production dependency findings: one high and three moderate**, with **zero critical production findings**. Affected package entries are `undici` (high), `fast-uri`, `ajv`, and `smol-toml` (moderate). The plugin reported **zero production findings**. These counts are time-sensitive; development/build dependency findings printed during installation have higher totals.

The findings remain unresolved in the pinned upstream installation. No automatic dependency upgrade or forced audit fix was applied, because it would alter the managed dependency set without proving compatibility. This setup must not be described as free of dependency vulnerabilities. Reproduce the audit with `ops/audit-stack.sh` (host) and `ops/audit-stack.sh plugin` inside the assistant account. Raw reports are retained privately in `/home/assistant/ai-assistant-install/` and copied to the project's ignored `.local/` directory.

- [Undici excessive-content-encodings denial of service](https://github.com/advisories/GHSA-xjj6-f33q-929c)
- [fast-uri URI scheme spoofing](https://github.com/advisories/GHSA-w74x-v6f9-j3xg)
- [smol-toml parsing complexity](https://github.com/advisories/GHSA-r4xh-jqrq-34v2)

The earlier 48-test relocation run exercised `test_workbench.py`, `test_memory_spaces.py`, and `test_hosted_boundaries.py`. Future runs should use a disposable FalkorDB instance and a test-only persistence volume rather than the live service.
