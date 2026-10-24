# Extraction validation

Verified on 2026-10-23 using Python 3.12.14 and the existing installed project environment.

- Focused memory suite: **154 passed, 2 deselected** (GPU checks excluded by the retained default selection).
- Ruff: all checks passed for `memory/`, `scripts/` and `shared_server.py`.
- Real FalkorDB v4.20.7 on isolated port 6381; actual embedded Qdrant and SQLite receipt journals.
- Checked CRUD, graph/vector rollback, lifecycle/provenance, context invalidation, tenancy, event replay, killed-process recovery, cold backup and fresh restore.
- Dependency audit found no missing local modules or imports from application packages.
- A relocated temporary copy successfully generated fresh credentials and initialized the three-tier runtime and journal without parent source files. Repeat setup refused to overwrite credentials.
- The copied API is headless. Source scans found no excluded integration references in runtime code, scripts or test fixtures.

The standalone facade explicitly uses the existing FalkorDB + Qdrant engine. Unused single-store migration hooks were removed. Snapshot restoration was corrected to preserve JSON-string observation embeddings as graph properties; the existing backup/restore integration test verifies the fix.

Tests use deterministic injected embedding fixtures. Downloaded neural-model relevance, optional hosted extraction and CUDA execution were not evaluated. A fresh dependency installation was not performed. Test databases were isolated from existing services; the temporary Compose service and its newly created volume were removed after verification.
