# Controlled local Git execution — 26 October 2026

The platform now has a bounded local Git connector using the installed **Git 2.51.0.windows.2**. It can create one new `refs/heads/codex/…` branch at an exact reviewed commit. Qualification uses generated repositories only. Hosted GitHub writes, checkout, commits, file edits, deletion, pushes and native UI are outside this connector's command surface.

The user instructed us to proceed independently using current interfaces. No worker prompt, skill, task/result definition or central Atlas registry entry was changed. This controller is available through explicit authenticated APIs; it has not been added as an automatically executable Atlas search result.

## Hermes-first inspection and reuse

The installed Hermes runtime was re-inspected before implementation: **0.21.3**, compatible SDK, isolated effective tools `[]`. It registers terminal, code execution, delegation and cron tools, but registration alone does not qualify resource-specific operations. The GitHub CLI is not installed; no hosted GitHub credential or write is claimed qualified.

Reuse:

- Git owns object/ref storage, transactions, concurrency checks and reflogs; no Git engine or shell agent was built.
- The existing `ActionGate` owns immutable approval digests, expiry, revocation, receipts, uncertainty and non-replay. It accepts a trusted plan model and one of two fixed store names; default desktop behavior remains unchanged.
- Existing path/reparse checks and verified file-opening helpers are reused for repository grants. The existing authenticated application service owns identities and task scopes.

New integration is necessary because a general terminal tool does not enforce Wayfinder owner/space/task grants or exact action approval. `git_connector.py` adds that narrow resource adapter; `connectors.py` supplies authenticated request, decision, audit and reconciliation entry points. Neither adds a reasoning loop, memory engine, scheduler or desktop driver.

## Exact operation and permission boundary

The reviewed `GitPlan` binds repository path and directory identities, an expiring opaque grant, new full branch ref, expected HEAD commit, state fingerprint, one operation and an unpredictable receipt nonce. Filesystem identities use strings in the contract to preserve large Windows IDs across JSON clients.

For the Git binding, the review digest covers the canonical JSON envelope `{scope: [owner, space, task], plan: GitPlan, expires: epoch_seconds}`. The server owns this envelope; clients return the reviewed opaque digest rather than modifying the plan or lifetime. Existing desktop digest behavior is preserved for compatibility.

The handler revalidates the grant, repository identities, configuration fingerprint, destination and HEAD. It then uses one Git transaction to verify HEAD and create the absent branch. Git's `create` command refuses an existing ref; its transaction checks old values while locking the requested references. The provider acknowledgement is followed by independent ref and nonce-bearing reflog reads. [Git update-ref reference](https://git-scm.com/docs/git-update-ref).

Approvals last 120 seconds; grants last 300 seconds and disappear on shutdown. Expiry is checked after observation and again immediately before the Git process is dispatched. Request IDs are immutable within owner/space/task. Workers cannot create grants, approve, revoke another task's actions, or read another task's receipts.

Repository/system Git hooks are disabled per command, including `reference-transaction`. Inherited Git environment overrides and system/global configuration are excluded. Only fixed plumbing commands are permitted; no shell command string is accepted. [Git hook configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath), [reference-transaction hook](https://git-scm.com/docs/githooks#_reference_transaction).

Supported repositories have an ordinary in-place `.git` directory, initialized SHA-1 HEAD, no metadata links/reparse points, external includes, extensions, object alternates or worktree redirects. Metadata traversal is bounded to 10,000 entries and 16 levels; configuration reads to 64 KiB; each Git subprocess to 10 seconds. Private application/credential roots are excluded. Unsupported repositories fail closed. These checks are an application permission boundary; they are not a new OS sandbox against another process with the same user's filesystem privileges.

## API

All routes use the existing `/v2/` transport and require authenticated orchestrator identity plus owned `space` and explicit `task`. The bearer credential belongs only to the trusted host/client, never the model or worker.

| Operation | Additional fields | Result |
|---|---|---|
| `platform_git_grant` | `path` | Task-bound repository grant and observed HEAD; permits only the supported new-branch operation. |
| `platform_git_observe` | `grant`, full `branch` ref | Read bounded target/precondition state. |
| `platform_git_propose` | `grant`, `branch`, `expected_head`, `request_id` | Immutable pending plan, digest and expiry; no branch creation. |
| `platform_action_decide` | `id`, reviewed `digest`, boolean `approve` | Exact approval/rejection, then bounded execution and verification where approved. |
| `platform_action_revoke` | `id` | Revoke pending authorization. |
| `platform_git_revoke` | `grant` | Revoke the grant and associated pending proposals. |
| `platform_action_result` | `id` | Scoped stored status, approved plan and receipt/uncertainty. |
| `platform_action_reconcile` | `id`, fresh same-task `grant` | Read-only reconciliation of an uncertain outcome against the original repository identities. |
| `platform_action_audit` | `id` | Latest 100 scoped audit entries. |

`GitPlan` and `GitStep` schemas accompany the existing platform contracts. `ActionBinding.backend` now also accepts `git_branch_gate`. API callers review the plan and digest before submitting a decision. No generic command endpoint was added.

## Recovery behavior

A lost acknowledgement after the provider writes is `outcome_unknown`, never an automatic retry. Repeated delivery of that approval does not execute again. Read-only reconciliation requires the exact ref target **and** the original receipt nonce in the latest reflog entry; a matching ref from an unrelated actor is insufficient. Changed approved payloads are rejected before reconciliation reads.

On restart, pending approvals expire and executing attempts become uncertain. Repository grants are not restored. Reconciliation therefore requires a fresh grant for the same original directory identities. If the target is absent, different or unattributed, uncertainty remains; no compensating write or replay is performed.

Revocation prevents pending dispatch. An already dispatched atomic Git transaction may complete; cancellation does not undo a created branch. The outcome/audit records retain what was actually verified. This local creation protocol does not establish exactly-once external effects for other providers.

## Qualification and transport correction

The first native-Git tests exposed Windows text-mode stdin translating LF into CRLF, causing Git to reject `start`. Sending the transaction as UTF-8 bytes preserves the required LF protocol. Fresh synthetic repositories verified the correction. No project branch was used for that diagnosis or test write.

Tests exercise actual Git through the authenticated API and independently inspect the ref/reflog. Separate fault injections simulate lost acknowledgements and concurrent changes; no mocked Git executable substitutes for the successful write case. Tests include rejection, changed digest/payload, grant and approval expiry, expiry during observation/dispatch, revocation, worker/cross-task denial, reference injection, existing destinations, hook suppression, redirected/private repositories, restart and unattributed outcomes.

Private evidence: `.local/verification/git-prerequisites.json`, `.local/verification/git-connector.json`, and the final `.local/verification/platform.xml`. Run `ops/Test-Platform.ps1` for terminal-only tests against synthetic repositories and a disposable database. `-Live` remains the separate installed-Hermes read-only qualification and does not publish Git changes.

Final result: **93 passed, one live-Hermes test skipped, one UI test deselected**, in 145.96 seconds. The Git cases use the real installed CLI with synthetic repositories; lost acknowledgements and concurrent changes are explicit fault injections. Ruff, whitespace checks and consistency checks for all eight exported schemas passed. The project remains on `codex/platform-integration` at `4913ee9`; its existing local edits are preserved, with no project commit or push.

This qualifies one local Git operation. Hosted GitHub/account writes, broader coding execution, calendar/tasks/messaging, fitness and maintenance integrations remain later work. W37 native testing remains disabled.
