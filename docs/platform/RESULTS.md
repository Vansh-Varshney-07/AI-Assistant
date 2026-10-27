# First platform integration result — 26 October 2026

The minimum read-only workflow passed using installed Hermes **0.21.3** and isolated Iron Web storage. Work is on `codex/platform-integration`; existing uncommitted work remains present. No commit, push, native desktop action, screen capture, clipboard access or external account write was performed.

The detailed read-only results below are historical evidence for the first slice. The current status includes [controlled Git execution](CONTROLLED-GIT.md) and the [memory/recovery/source expansion](EXPANSION.md). Peer coordination is no longer a blocker. Latest regression evidence: **139 passed**, one live-model test skipped, one UI test deselected; separate installed-Hermes synthetic run **one passed**. Google transport qualification remains mocked, not a live account pass.

## Milestone status

| Milestone | Demonstrated result | Outstanding dependency |
|---|---|---|
| 1. Inspect and establish contracts | Installed-version/SDK/registry inspection; implementation plan; platform-owned schemas and fixtures. | Optional future worker configurations. Existing interfaces are the baseline; peer coordination is no longer a blocker. |
| 2. Minimum read-only workflow | Authenticated request → fixed stored plan → Atlas selection → scoped Iron Web recall → existing W35 → source/runtime/freshness validation → synthesis with provenance. | Integrate the other developer's worker configuration through an agreed adapter; qualify additional task types. |
| 3. Controlled execution | Real local Git branch transaction and scoped Iron Web events, exact approval, independent verification and read-only reconciliation. | Hosted account writes and broader operation types remain unqualified. |
| 4. Recovery/audit | Persistent stages/audit; duplicate suppression; cancellation/deadlines; restart without automatic replay; one explicit read retry; artifact checks, latency/failure metrics and terminal artifact clearing. | Broader dependency graphs through existing Hermes delegation, additional provider reconciliation and provider usage/cost reporting. Partial at the overall milestone level. |
| 5. Expand integrations | Qualified local activity CSV; scoped memory previews/change events; Google Calendar/Tasks/Gmail-reference read adapters with fixture HTTP qualification. | Real account consent/tests, external writes, hosted GitHub, fitness-vendor mapping, store-wide maintenance and qualified W37 host connection. Partial. |

## Reuse and new integration

- Reused `HermesBridge` and `WorkerHub`: no agent loop, worker prompt, worker task/result schema, SDK update, or main provider configuration was replaced.
- Reused existing Atlas keyword retrieval. A controller overlay marks every candidate non-authoritative and only binds the demonstrated W35 handler after installed-runtime evidence. No replacement index or embedding model download was introduced.
- Reused `AppService` authentication, memory scopes, Iron Web `recall`, freshness validation and existing file broker. No worker receives memory credentials or storage access. Internal owner/space IDs and proofs stay outside model input.
- Added `wayfinder/platform/` for owned contracts, read-only runtime inspection, candidate qualification, bounded context tickets and a fixed workflow controller. The controller stores orchestration state in the existing application SQLite database; facts remain in Iron Web.
- Added only platform initialization, endpoint routing and safe shutdown ordering to `wayfinder/service.py`. Existing worker and memory interfaces remain available. No central registry edits were made for this platform slice.
- Reused the disposable-database test runner, with separate platform and live test reports. New entry point: `ops/Test-Platform.ps1`.

## Actual verification

| Tier | Result | What it proves |
|---|---|---|
| Contract/API/regression | **64 passed**, one live test skipped, one UI test deselected | Real disposable FalkorDB and embedded Qdrant with deterministic fixture embeddings; W35 inference mocked. Authenticated scopes, immutable requests, concurrent deduplication, conflicts, revoked/changed files, stale memory/runtime, deadline cancellation without polling, restart, invalid outputs, and existing regressions. |
| Live installed Hermes | **1 passed**, 65 other tests deselected | Actual managed Hermes 0.21.3, existing OpenShell transport, authenticated API, generated document and real disposable Iron Web storage with fixture embeddings. No mocked worker in this test. |
| Schema export consistency | Six schemas match their implementations | Platform-owned context/workflow/action wrappers plus existing DesktopPlan; worker task/result definitions unchanged. |
| Static checks | Ruff and tracked diff whitespace checks passed | Static checks only; they do not establish connector or model accuracy. |
| Native desktop | **Not run** | W37 remains unqualified. Earlier uncertain attempts remain historical evidence, not a pass. |

The live runtime exposed **99 registered tools**, labelled registered/unprobed. The isolated worker probe exposed **zero tools** and no memory. Registration is not proof that optional tools, MCP connectors, scheduling integrations or desktop input are configured or authorized.

The final live case compared a generated document stating **42 days** with scoped synthetic memory stating **30 days**. Hermes identified the **12-day discrepancy**, cited the selected document and memory references, and preserved uncertainty about precedence. The workflow independently verified the file hash and current memory proof. It completed in **20.115 seconds**, with **one worker invocation**. Model token usage and monetary cost are explicitly `null`; broader answer accuracy remains a task-level evaluation responsibility.

Private generated evidence (ignored by Git):

- `.local/verification/platform.xml`
- `.local/verification/platform-live.xml`
- `.local/verification/platform-live.json`

## Interfaces and next step

The [platform interfaces](INTERFACES.md), [JSON Schemas](contracts/) and `tests/test_platform_integration.py` are the concrete handoff. The user removed the peer-coordination dependency; continue against these existing interfaces and adapt later worker configurations explicitly when supplied.

Run terminal checks with:

```powershell
.\ops\Test-Platform.ps1
.\ops\Test-Platform.ps1 -Live
```

The live option sends only generated fixture data through the existing model route. Both commands use a uniquely named temporary database and exclude UI tests. Native testing remains disabled until explicitly re-enabled by the user.

Current limitations: one fixed read-only recipe, broader dependency graphs unqualified, historical completed-result artifacts rather than ongoing freshness guarantees, and a five-minute runtime inspection lifetime. Terminal platform artifact clearing, local Git writes and scoped memory changes were added after this historical read-only run; see [EXPANSION.md](EXPANSION.md) for their boundaries. Hosted account writes and W37 native execution remain unqualified.
