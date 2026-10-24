# Iron Web baseline inspected for this plan

Date: 24 October 2026. Read-only source inspection; no runtime tests, account reads or application changes in this planning session.

Source root: `D:\Opencode_\memory_system`.

- `README.md`, `memory/engine.py`: direct `MemoryEngine` is the FalkorDB + embedded Qdrant implementation. Core source/claim lifecycle and retrieval should be preserved.
- `memory/spaces.py`, `memory/workbench.py`: saved spaces use a local directory; source IDs and request replay are scoped; old namespace spelling remains compatible. A space ID is not user authentication.
- `workbench_server.py`: local development UI exposes session/status/spaces and scoped inventory through loopback GET routes. Those routes are not a production worker authorization mechanism; host/network isolation alone does not make a shared OS user trustworthy.
- `memory/shared/service.py`, `docs/api.md`: existing shared service binds tenant/actor/role to credentials; persists receipts; includes processing readiness, work lease/completion and context-validation operations. Do not invent a replacement journal until the reusable portion is assessed.
- `memory/context/contracts.py`, `memory/context/runtime.py`: context requests still require `trip_id` and retained travel task contracts. General personal/work/fitness workflows need a versioned schema change and compatibility tests, not a superficial rename in user prompts.
- `memory/cache/` and `memory/context/`: bounded context cards and explicit proof validation are present; their presence does not prove every requested future workflow already uses them. The workbench path is a direct-engine path.
- `docs/memory-spaces-test-report.md` and the chat outputs: prior implementation session recorded 204 automated tests and 21 live checks using BGE/Nemotron and server restart. Historical validation is not validation of the proposed Hermes product.
- Current standalone source has no `.git` directory, and no issue tracker was supplied. This plan uses the Wayfinder local Markdown tracker within the outputs planning bundle. No research branch or issue was pushed.

User decisions in this conversation: Windows/local first; narrow recurring grants allowed; desktop scanning/capture excluded; general fitness adapter design required. Other architecture choices in PLAN.md remain proposals for the decision tickets.
