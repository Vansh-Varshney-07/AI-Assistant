# Platform implementation plan — 25 October 2026

Branch: `codex/platform-integration`, based on `4913ee9`. Existing dirty work is preserved. Native UI, clipboard access, and desktop capture stay disabled.

Update, 26 October: the user instructed us not to wait for the other developer's branch or agreement. Continue independently against the existing interfaces; adapt future worker configurations if supplied. The [controlled Git increment](CONTROLLED-GIT.md) follows the read-only slice.

Current increment: [EXPANSION.md](EXPANSION.md) records scoped memory previews/events, explicit read-only retries, artifact evaluation/telemetry/clearing, local activity CSV and prepared Google read adapters. These use the existing systems and preserve all worker-owned definitions. Real account qualification requires provider choice and local consent; broader dependency graphs and W37 native execution remain unqualified.

## Current state and reuse

- Installed Hermes is **0.21.3**, Python 3.13.5. Its inspected SDK supports `run_budget_seconds`, `request_overrides`, tool allow/deny sets, and memory/session isolation. Installed delegation supports batches and output schemas; cron and MCP modules exist. Module presence is not connector qualification.
- Existing `HermesBridge` reaches the managed OpenShell sandbox and the existing `WorkerHub` supplies bounded W35 execution, cancellation, scoped results, and file-hash evidence. Do not replace or change W33–W36 worker prompts/contracts.
- `AppService` already authenticates orchestrators, enforces owner/space/task memory scopes, supplies recall/freshness proofs, and owns memory updates. Reuse these APIs rather than introducing another memory engine or exposing storage to workers.
- Atlas already has registry discovery and keyword/vector retrieval. Reuse retrieval; treat registry availability as metadata. The current Windows PATH-based inspector does not establish the installed sandbox's capabilities.
- W37 has a disconnected default gate and a test adapter with a recorded resource refusal. Its execution is unqualified. Keep those artifacts and uncertainty.

## Concrete sequence

1. Publish `wayfinder.platform/1` context/capability/workflow binding contracts and synthetic examples. Preserve the existing worker task/result interface as the compatibility baseline. Worker configurations can use later explicit adapters when supplied; they do not block independent platform work.
2. Inspect the existing sandbox read-only: package version, source/schema fingerprints, SDK compatibility, and actual isolation probe. Cache this evidence with a short lifetime; do not call optional tool check functions that may install software or mutate configuration.
3. Connect one fixed read-only workflow: authenticated request → stored controller plan → Atlas candidates → owner/space/task-bound Iron Web recall → existing W35 job on a granted file → worker/evidence validation → final memory/file/runtime freshness check → response with provenance. No external effects or new reasoning/delegation loop.
4. Persist request/digest, stages, cancellation, deadline, job references, result and audit transitions in the existing SQLite application store. Reuse WorkerHub's two-run limit, cancellation and Hermes time budget. Do not implement a new general scheduler. Interrupted read-only work is marked interrupted; no automatic replay.
5. Qualify with synthetic inputs and disposable FalkorDB/Qdrant storage. Separate contract/mock results from a real installed-Hermes run. Test worker denial, scope escape, changed input under the same request ID, expired context, revocation, cancellation, concurrent duplicate submission, restart and missing runtime.

## Later milestone gates

- Controlled writes: adapt existing approval/receipt boundary, qualify a selected connector with explicit resource authorization, verify and reconcile outcomes. Existing calendar/task/Notion metadata is not sufficient evidence. Do not send messages or perform live writes by inference.
- Recovery/evaluation: extend the stored transitions with provider reconciliation, eligible bounded retries, usage/cost data only where returned by providers, and explicit unknown values elsewhere.
- Expand connectors after installed compatibility checks and source selection. Fitness requires a supported authorized source. Reminders must use the existing Hermes scheduling interface. W37 requires a qualified host connection and separately re-enabled native testing.

## Ownership handoff

Platform-owned context/action enforcement and central APIs live under `wayfinder/platform/`. Worker-owned prompts, skills, and task/result definitions remain unchanged. Consume worker configuration fragments through one reviewed binding path once supplied; do not edit competing central registry entries or invent worker reasoning procedures. The first binding explicitly names existing W35; unsupported roles fail closed.

## Completion evidence

Each report must name reused components, changed integration files, contract versions, actual test tiers, and outstanding dependencies. Milestones beyond the demonstrated read-only workflow remain incomplete until their gates pass.
