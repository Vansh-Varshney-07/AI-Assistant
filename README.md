# AI assistant

This folder is self-contained source for the FalkorDB + embedded Qdrant memory system. It contains the memory engine, three-tier context runtime, authenticated headless API, lifecycle rules, receipt queue, backup utility and focused tests. No files from the parent project are needed to install or run it. The base package contains no application frontend, travel agents, browser automation, private credentials, copied databases or downloaded models. A minimal local Memory Testing Workbench is included for manual validation; see below.


## Assistant stack setup

The canonical project folder is `D:\Opencode_\AI assistant`. See [ops/SETUP.md](ops/SETUP.md) for the dedicated Ubuntu environment, Hermes/NemoClaw/OpenShell installation steps, verified migration checks and remaining setup work.

## Architecture

| Tier | Contents | Implementation |
| --- | --- | --- |
| 1: hot context | Agent instructions and current subject/scope essentials, with equal configured token caps | `memory/context/`, bounded host RAM |
| 2: context cards | Evidence-backed task and explicit mood cards, selected within a token budget | `memory/cache/`, CPU matching; optional CUDA matching |
| 3: durable evidence | Source records, vectors, entities, temporal claims, provenance, corrections and work dependencies | FalkorDB graph + embedded Qdrant vectors; SQLite journal for receipts and replay |

The public `MemoryEngine` explicitly selects the existing dual-store implementation. Both `MemoryEngine` and the compatibility name `LegacyMemoryEngine` identify that implementation. There is no dependency on a sibling source folder. SQLite supports event receipts, notifications and processing state; FalkorDB and Qdrant remain the memory stores.

## Install and start

Use Python 3.12 and Docker Compose. Run these commands from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d falkordb
```

The included service uses `127.0.0.1:6381`, graph `memory_core`, and its own Docker volume `memory_system_falkordb_data`. Embedded vector files live in this folder's `data/`. The service does not reuse the original application's graph or Docker volume. Existing `FALKORDB_*` environment variables override connection settings; clear or adjust them if your shell points elsewhere.

## Memory engine

```python
from memory import MemoryEngine

with MemoryEngine() as memory:
    memory_id = memory.add('The project uses a weekly review cycle.')
    print(memory.get(memory_id))
    print(memory.search('review cycle', top_k=3))
```

The first semantic write/search downloads the configured embedding model if it is not cached. CPU execution is the default. The default extraction policy is `none`; pass validated entities/relationships or structured claims explicitly. Hosted extraction is optional (`requirements/nim.txt`) and requires its own configuration and environment credential.

## Three-tier API

Configure the **actual consuming model's existing tokenizer.json** and its versioned identity. The setup script creates fresh user, planner and reviewer credentials locally and enables all three tiers:

```powershell
.\.venv\Scripts\python.exe scripts/setup_shared_service.py --tokenizer C:/models/consumer/tokenizer.json --tokenizer-id consumer-model-revision
.\.venv\Scripts\python.exe shared_server.py --config data/shared_service/service.json --port 3351
```

`GET /health` returns API status. There is no HTML interface. Authenticated JSON endpoints and examples are described in [docs/api.md](docs/api.md). Use `memory.shared.client.SharedMemoryClient` for Python integrations.

Setup uses structured claims and makes no hosted model calls. Credentials are generated at setup time, stored privately under ignored `data/`, and never printed. Agent profiles are configuration; they do not grant access by themselves.

The retained context contract uses `trip_id` as its exact task scope key and supports `flight`, `hotel`, and `itinerary` task types. These are core schema defaults retained from the original implementation; the related website and agents are absent. Lower-level memory CRUD and structured claims accept other domains. For another context domain, define its task fields and scope contract in `memory/context/runtime.py` and `memory/context/contracts.py` before using `/v1/context`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements/dev.txt
.\.venv\Scripts\python.exe -m pytest
```

Integration tests use the included FalkorDB service on port 6381 and isolated `test_` graph names, plus temporary Qdrant/journal paths. Cleanup only removes graphs owned by the tests. The default test selection excludes GPU, downloaded neural-model and dataset checks. Injected deterministic embeddings verify control flow and storage behavior, rather than neural relevance quality.

## Configuration and operations

`config.yaml` configures the direct engine. The shared service uses its private JSON configuration and per-tenant runtime directories. Its default engine factory uses validated engine defaults plus `FALKORDB_*` environment overrides; editing `config.yaml` alone does not change the shared-service factory.

One process must own each embedded Qdrant/journal runtime. Pending or failed events block dependent actions; stale context proofs must be revalidated before completing work. Graph/vector writes use compensation and receipt replay, rather than a single crash-atomic transaction across databases.

Stop the API before taking a cold backup:

```powershell
.\.venv\Scripts\python.exe scripts/shared_memory_snapshot.py backup --config data/shared_service/service.json --destination data/backup_1
.\.venv\Scripts\python.exe scripts/shared_memory_snapshot.py restore --snapshot data/backup_1 --runtime data/restored_1
```

Restore refuses existing targets and uses fresh graph names. Backups contain private source data and credentials. Optional GPU card matching is configured with `context.use_gpu`; its dependencies are listed in `requirements/context-gpu.txt`. GPU matching holds retrieval vectors, not a generative model KV cache.


## Wayfinder AI Desktop Interface & Memory Workbench

The project now includes the full **Wayfinder AI Desktop Interface** (merged from the `stitch_wayfinder_ai_desktop_interface` design system) alongside the existing dual-store FalkorDB + Qdrant memory testing engine.

### Integrated Subsystems & Screens

The interface is served locally via `workbench_server.py` and provides a responsive, single-page application with dark/light themes, keyboard shortcuts (`Ctrl+K` for Quick Search, `Alt+Space` for Companion Pet), real-time host telemetry, and 10 integrated views:

1. **Home Command Center** (`#home`): Chat with Wayfinder, diurnal schedule summary, animated compass reticle, quick action pills, and active automations.
2. **Planner Matrix** (`#planner`): Operating schedule timeline (08:00–18:00), priority task queue, and telemetry gates.
3. **Notion Connected Knowledge** (`#notion`): Workspace documents tree, architecture specifications, and database cards.
4. **Workflows Automation Engine** (`#workflows`): Workflow catalog, triggers, and visual DAG state-machine node canvas.
5. **Activity & Execution Monitor** (`#activity`): Live status of the 16 Wayfinder agent workers (`W01` to `W24`), execution logs, and trace inspector.
6. **Connections & Data Bridges** (`#connections`): Service bridges for FalkorDB, Qdrant, SQLite Journal, Notion, GitHub, Linear, Google Calendar, and NVIDIA NIM.
7. **Permissions & Security** (`#permissions`): SecOps matrix, enforced policy engine, human sign-off gates, and sandbox status.
8. **Memory & Knowledge Workbench** (`#memory`): Full FalkorDB + Qdrant testing workbench with isolated memory spaces, prompt ingestion/retrieval, assertion confirmations, explicit JSON claims, live inventory filters, and record inspectors.
9. **Settings & Diagnostics** (`#settings`): Service status, loopback checks, telemetry auto-refresh, and clean shutdown.
10. **Pet & Desktop Companion** (`#pet`): Contextual summon overlay accessible via `Alt+Space`.

### Running the Desktop Interface

#### 1. Full Mode (Live FalkorDB + Qdrant Memory Engine)
```powershell
# Start FalkorDB
docker compose up -d falkordb

# Start the Desktop Interface Server
.\.venv\Scripts\python.exe .\workbench_server.py
```
Open [http://127.0.0.1:3352](http://127.0.0.1:3352) in your browser.

#### 2. Preview / UI-Only Mode (Offline / No Docker Required)
You can explore and test the entire UI, workers, and simulated memory spaces without starting Docker:
```powershell
python .\workbench_server.py --preview
```

#### 3. Standalone Stitch Design Screens
Any individual Stitch mockup screen can also be viewed directly in isolation:
- [http://127.0.0.1:3352/screens/home](http://127.0.0.1:3352/screens/home) — Home Command Center
- [http://127.0.0.1:3352/screens/planner](http://127.0.0.1:3352/screens/planner) — Planner Today Matrix
- [http://127.0.0.1:3352/screens/notion](http://127.0.0.1:3352/screens/notion) — Connected Notion Workspace
- [http://127.0.0.1:3352/screens/workflows](http://127.0.0.1:3352/screens/workflows) — Workflow Editor
- [http://127.0.0.1:3352/screens/activity](http://127.0.0.1:3352/screens/activity) — Activity Execution Monitor
- [http://127.0.0.1:3352/screens/connections](http://127.0.0.1:3352/screens/connections) — Data Bridges
- [http://127.0.0.1:3352/screens/permissions](http://127.0.0.1:3352/screens/permissions) — Security & Permissions
- [http://127.0.0.1:3352/screens/list](http://127.0.0.1:3352/screens/list) — Catalog of all Stitch source screens

- [Inspection report](docs/workbench-inspection.md)
- [Startup and all eight manual scenarios](docs/workbench-guide.md)
- [Editable test results](docs/workbench-results.csv)
- [Automated validation and limitations](docs/workbench-validation.md)


## Nemotron Lightning and Ultra

The workbench supports explicit selection of `nvidia/nemotron-3.5-lightning-30b-a3b` and `nvidia/nemotron-3-ultra-550b-a55b`. To enable the requested hosted models on this machine:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\workbench_server.py --nvidia --key-file 'D:\Opencode_\reserchpaper\.env'
```

Stop an existing workbench process before running this command. The interface stays on loopback; selected-model prompts and relevant evidence go to NVIDIA. Embeddings and storage remain local. Without --nvidia, evidence-only mode makes no hosted calls. See [repairs, full startup and model usage](docs/nemotron-repairs.md) and [latest real-model comparison](docs/nemotron-validation/nemotron-report.md). `scripts/validate_nemotron.py` reproduces the live comparison in new retained test namespaces.

## Independent memory spaces

Use **New isolated space** and the **Active memory space** selector to keep tests separate. IDs and empty spaces persist across server restarts. All prompt operations and the inventory API use the selected space; old test namespaces remain individually selectable. Space IDs are local scopes, not authentication. See [usage, API and future user ownership](docs/memory-spaces.md) and [final tests](docs/memory-spaces-test-report.md).

## Personal AI companion foundation

The 30-page Personal AI Hackathon Foundation Research report is retained at the repository root. Its requirements are incorporated into the [companion product plan](docs/personal-ai-companion/PLAN.md) and [source-page integration record](docs/personal-ai-foundation-integration.md). These are design additions, not a claim that new provider, sandbox or connector features are implemented. Existing Windows/local, orchestrator-only memory and no-desktop-capture choices remain in force.

The [phase-by-phase build and manual test plan](docs/personal-ai-companion/PHASE-BY-PHASE-PLAN.md) adds 19 testable handoffs, 69 manual acceptance cases and a synthetic fixture kit. Every case starts Not run; the document does not claim that the planned runtime features are implemented.

## Current Wayfinder MVP plan — minimal app and quick chat

The latest user scope is the [Wayfinder MVP v2 plan](docs/wayfinder-mvp-v2/PLAN.md): configurable chat/plugins/workflows/memory/skills/settings in a minimal app, plus a persistent plain quick-chat window. Animal UI and desktop scanning/capture are excluded. Use the [new phased manual acceptance plan](docs/wayfinder-mvp-v2/PHASES.md) and [memory-quality contract](docs/wayfinder-mvp-v2/MEMORY-QUALITY-CONTRACT.md). Earlier animal-first plans remain historical; this documentation update does not implement the proposed runtime.
