# Wayfinder rebuild: tests and phase gates

Status: test specification for future implementation. These are required checks, not newly passing tests. Research REA outcomes live in the linked reference reports; they are not product regression results.

## Task and phase protocol

1. Read the task's dependency, acceptance criterion and applicable existing code/contracts.
2. Make one bounded change. Add a test for the behavior/security invariant it introduces or repairs; do not create tests that merely restate implementation details.
3. Run the focused checks. Save the exact command, source/binary identity, status, failure details and report path. Fix failures before enabling dependent behavior.
4. At phase end, run the affected integration suites and a representative user-outcome scenario. Broad final regression is required before packaging; it need not be repeated after every purely decorative change.
5. Mark each check passed, failed, blocked, not run or not applicable with a reason. Fixture, live-Hermes, live-provider, package-integrity, headless-render and native-UI evidence are separate tiers.

No phase passes on invented activity, test counts, screenshots or an unrelated old report. A phase that qualifies only a read variant cannot qualify a send/write variant. Record total coverage and exclusions; do not sum overlapping test suites into a reliability percentage.

## Verification families referenced by the atomic backlog

| ID | Meaningful checks and representative scenario | Existing starting points / proposed extension |
| --- | --- | --- |
| T01 Contract/capability truth | Unknown fields/version/role denied; authenticated owner cannot be supplied by model; configured != qualified; metadata-only Docs/Sheets not full content; manifest/preload/API correspondence; legacy schema round-trip. | Existing profile, API-surface, Atlas and platform contract tests; add typed DTO/variant cases where interfaces change. |
| T02 Installed runtime/isolation | Actual SDK signatures/schema/version; closed inherited tools/memory; role-specific permitted tools; two simultaneous child contexts cannot read each other; revoked/expired binding refused; cancellation/child cleanup; streaming/delegation only when demonstrated. | Runtime probe and Hermes isolation tests. Read-only compatibility probe is separate from inference. |
| T03 Conversation lifecycle | Accepted request persisted before dispatch; double submit returns same attempt; changed payload under same ID denied; scoped pagination; Unicode/size limits; scope switch ignores late response; stop != proven upstream abort; restart/ack-loss does not resend. | `tests/test_chat.py`, chat and broker component tests, task-profile duplicate cases. |
| T04 UI/a11y/layout | Keyboard order, dialog focus/restore/Escape, accessible icon names, non-color status text, theme contrast, long targets/code, empty/error/offline states, reading size, reduced motion and 600/900/1440px layout. | Existing Vitest/jsdom tests; headless synthetic renderer checks only where allowed. These do not prove native dialogs or screen-reader behavior. |
| T05 Rendering/secrets/assets | Hostile Markdown/HTML/SVG/URLs stay inert; CSP and sender checks retained; local assets work with renderer network blocked; origin/license inventory; encryption failure never writes plaintext; no secret in IPC results/logs/renderer settings; user-click copy is write-only if included. | Broker/sender/vault tests, package checks, new formatter/asset admission cases. Use synthetic markers rather than real credentials. |
| T06 Onboarding | Missing/stopped Docker, remote/wrong-engine context, wrong pinned image, missing model/backend, expired qualification, changed model consent, failed write, restart at every step, repeated finish and optional provider skip. Never delete/reset existing stores to repair setup. | Existing setup/onboarding/runtime-path tests and mocked owned-command runner; disposable storage for persistence cases. |
| T07 Actual model path | Synthetic chat/task input reaches approved model with frozen history/context; provider/model mismatch refused; real progress vs unsupported streaming; actual result validated; timeout/interruption preserved; no automatic memory publication or provider fallback. | Existing managed-Hermes synthetic tests and transport verification, extended only for new bindings. Record cost/tokens as unknown unless supplied. |
| T08 W-role integration | Every W01–W47 has one explicit responsibility mapping; existing 16 definitions validate; missing fragments cannot dispatch; deterministic roles reuse APIs; W01→W03→capability selection→worker→W06→W07 obeys scope and result schema. | Existing worker contract suites, fresh readiness matrix, proposed binding/route tests. Offline fixtures do not qualify a live role by themselves. |
| T09 Context/files/data | Authorized file succeeds; traversal/reparse/symlink/private-state escape denied; file replacement/hash drift/expired grant denied; evidence provenance and bounds retained; stale/retracted memory excluded; activity CSV duplicate/timezone/overlap handling correct. | Existing FileBroker, platform sources/context/activity tests; isolated Iron Web fixtures. |
| T10 Exact effects/review | Preview does nothing; changed resource/payload/scope/precondition/expiry/revocation denied immediately before effect; duplicate attempt does not blindly repeat; lost acknowledgment becomes uncertain; reconciliation is read-only; verified receipt matches exact outcome. | Existing approval, local Git, memory and integration-action-safety tests; provider-specific adapter contracts. No exactly-once claim without provider support. |
| T11 Provider reads | Imported/passed/expired states; exact account/resource/returned identity; response/time/field/page limits; partial/truncated disclosure; token rotation/revoke during read withholds result; fixed endpoints/no redirects; no secrets/direct store in workers; manual read not automatic model disclosure. | Existing connection/boundary/Google/Notion/Tavily fixtures; opt-in bounded live read on already authorized resources when needed. |
| T12 Task/profile outcomes | M00 and every A/P entry has supported variants and explicit gates. Evaluate answer grounding, intended source use, required output and warnings, not just a generic “completed.” Test unavailable variant directly at API as well as UI. | The fresh readiness matrix and profile tests; add one meaningful scenario per enabled variant and shared worker isolation checks. |
| T13 Workflow safety | Immutable definition/run versions; allowed-node/typed-edge validation; cycle/unknown step/cross-scope edges denied; dependency ordering; concurrency/deadline/admission bounds; cancellation before ready/dispatch/child finish; test data isolated; edit/test UI cannot grant or execute by itself. | Extend existing W05 service tests; synthetic clocks/barriers and fixture workers. Reuse Hermes for reasoning/execution. |
| T14 Recovery/audit | Restart before/after acceptance and dispatch, duplicate delivery, stale versions, unknown external outcome, partial child failure, network loss, disk full, cleanup failure and eligible explicit read retry; audits preserve rejected/expired/revoked/uncertain outcomes without secrets. | Existing W44/evaluation/action tests, disposable process/storage integration and owned-process bridge checks. Never crash or repair the user's live memory. |
| T15 Package/release | Exact source/ASAR/backend/contracts/model/asset identity; no credentials/databases/private logs/dev paths; valid Windows executable and checksum; no source checkout/system Python prerequisite; stable data root across moves/upgrades; signing state honest. | Existing freeze/build/static-package scripts and actual Node/backend transport. Native packaged tests stay separate and permission-gated. |
| T16 Authorized live effects | First pass fixtures. Then only one user-approved disposable effect per enabled provider with exact resource/payload and independent verification; provider-specific reconciliation before retry. No unapproved email, calendar change, Notion write or GitHub mutation. | Existing controlled-execution pattern; new connector-specific live test only after H-WRITE. Mark unrun writes unavailable. |
| T17 Human EXE acceptance | User launches exact candidate; first-run diagnostics/consent and optional connections; chat; supported source task; workflow/node evidence; memory/local Git review; restart; missing-provider and cancelled/unknown behavior. | Versioned acceptance checklist tied to binary SHA-256. User outcome is recorded separately from automated checks. |

## Representative cross-feature acceptance tasks

1. **Learn from a file:** select a synthetic project note, ask for a study guide, inspect the source, stop one attempt and run a fresh explicit attempt. Compare with selected isolated memory using the existing recipe. No unrelated files enter context.
2. **Prepare a meeting:** use authorized Calendar, Tasks, selected Gmail content and a selected Notion page. Show which sources are used and gaps. A useful draft is possible only from qualified content variants; metadata/snippets cannot masquerade as complete messages/documents. No event/task/message is written.
3. **Review code:** select a disposable repository, investigate a failing fixture and propose a diff/test plan. Only a separately qualified and reviewed edit/test variant changes files or executes a fixed scoped runner. Hosted Git operations are independent gates.
4. **Correct memory:** preview one synthetic correction, reject it, expire another, approve a fresh exact proposal, then inspect the verified result and source. No automatic extraction or global forget is implied.
5. **Run and recover a workflow:** execute selected-file read → scoped recall → validation/synthesis; switch spaces, cancel, interrupt an owned test worker and restart the service in separate cases. Observe old runs without replay. Changed versions require new run identity.
6. **Inspect connections:** import fixture credentials, pass one scoped check, expire it, rotate/revoke during a read, and restart. The badge and result admission both change correctly. Failure text exposes no secrets.

## Existing commands to reuse after reviewing their current implementation

These commands already exist. Selecting a command does not mean it was run during planning:

```powershell
# TypeScript and headless component/boundary tests
& .\Test-Wayfinder.ps1 -Mode Frontend

# Existing backend regression with its disposable database
& .\Test-Wayfinder.ps1 -Mode Regression

# Existing platform contracts; optional synthetic Hermes test is a separate tier
& .\ops\Test-Platform.ps1

# Source frontend/backend packaging, after the frozen bundle is prepared
& .\Test-Wayfinder.ps1 -Mode Build
```

Use the existing database runner for selected backend tests rather than executing them against live Iron Web. Extend it deliberately as new suites are added. Inspect flags before using `Rendered`, `Packaged`, `NeuralLive` or external-account verification scripts: native windows and live providers are not silently authorized by a generic regression request.

## Per-phase evidence record

Store phase ID/task IDs, source revision and input hashes, exact commands, environment/runtime identity, test tier, counts and exclusions, output/report locations, failed cases, active capability variants and human dependencies. Store private runtime/provider evidence under ignored local storage. Public notes contain safe summaries and hashes.

Completion statuses must distinguish `passed`, `failed`, `blocked_dependency`, `not_run` and `not_applicable`. A disabled live effect may be a deliberate release exclusion after denial tests pass, but its live qualification remains not run. Do not use a mock driver to pass W37 or a fake provider to claim account connectivity.
