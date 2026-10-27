# Consolidated implementation status · 26 October 2026

Build **0.3.0** implements the local foundation and selected-file task slice of [the consolidated plan](CONSOLIDATED-AGENT-PLAN.md). It does not claim that every cross-app scenario or the previous R1–R7 ladder is complete. [Manual and automated test guide](TESTING-APP.md).

## Source integration

GitHub exposes one remote branch (`main`). Local branches inspected: `main`, `codex/platform-integration`, `codex/ui-backend-integration`, plus the new preservation and profile branches. The UI candidate was checkpointed at `8fa7690`. Relevant dirty platform sources were snapshotted with a separate temporary index at `488683b`, leaving the original checkout's HEAD/index and unrelated dirty work untouched. Both histories were merged at `b2d87f0`; the supplied GitHub worker contracts and UI commits are ancestors. The existing stash was inspected and retained without applying or dropping it.

Six overlaps retained the UI branch's tested ActionGate hardening, native/memory/Git expiry checks, stricter unknown-outcome regression, 0.2 backend package initializer and combined upstream/local worker initializer. The four functional overlap files matched the frozen import, so this preserves stricter later work rather than discarding newer platform logic. Benchmarks, private runtime data, caches, credentials and generated packages were not imported into the preservation commit. Git history/branch ancestry records the final main consolidation; no history rewrite or forced remote update is needed.

## Reuse and implemented interfaces

- Installed Hermes **0.21.3** was inspected again: compatible SDK, effective tools `[]`, memory disabled for the isolated binding. Existing managed Hermes/OpenShell jobs remain the execution path; no new loop, scheduler, parser, memory engine, native driver, MCP server or worker prompt was added.
- `wayfinder/platform/task-profiles.json` defines versioned **M00, A01–A08 and P01–P06**. These are logical routing definitions and app focus presets, not permanent processes or authority. Fitness stays deferred. Worker references and connection eligibility do not grant access.
- `TaskProfiles` supplies scoped `platform_profiles`, `platform_profile_start/result/runs/cancel/clear` behind the authenticated API. Strict request validation, immutable request deduplication, durable pre-dispatch reservation, restart interruption, file identity/hash validation and existing worker cancellation are enforced. An interrupted/unknown model attempt is never automatically redispatched.
- The qualified A01/A05/A06 **selected UTF-8 file** variants use exactly one existing W35 job. The direct baseline and profile path produce the same worker payload, with no additional reasoning call or helpers. A07 opens the existing scoped Memory view. Other task variants and all app presets remain unavailable until qualified.
- The new UI has **Agents & apps**, real profile availability, selected-document disclosure, task artifacts/source evidence, cancellation and bounded recent history. Root `Start-Wayfinder.ps1` now launches the new UI; `-Demo` creates disposable test resources. Root tests default to terminal/headless checks, not the legacy UI suite.
- Persistent canonical memory remains Iron Web. Profile artifacts reference the existing worker result instead of copying it into another memory engine. Clear removes the task and its linked worker artifact only. Full forget is still a distinct unfinished privacy workflow.
- The already existing Google OAuth helper was prepared locally with pinned dependencies. No shared Python environment was changed, no client/token was supplied, and no account consent/read/send/write was performed.

## Actual results, separated by tier

| Tier | Result | Limit |
|---|---|---|
| Merged backend/worker/profile suites | **298 passed, 2 skipped, 1 UI test deselected** | Disposable actual stores; deterministic fixture embeddings/models where declared. |
| React/main/preload suite | **40 passed**; TypeScript passed | Component and boundary fixtures, not native-dialog proof. |
| Rendered Chromium | **6 configurations passed**, no remote requests/errors | Synthetic UI data; profiles/presets, narrow/large layouts, themes, focus, source text and reading size. |
| Actual hidden Windows package | **16 checks passed** | Real renderer/preload/main/Python/API, disposable actual neural storage, inventory/gating and restart; no native dialog automation. |
| Actual Node/Python bridge | **7 checks passed** | Owned bootstrap, authenticated scope denial and shutdown. |
| Actual neural memory + managed Hermes | **18 checks passed** in 47.719s | Actual 30/42 comparison and A05 study guide, source hash verified; one existing worker per task, zero helpers; no duplicate redispatch. Cost/tokens unknown. |
| OAuth helper SDK | **12 passed** after local preparation | Synthetic/SDK PKCE and safe failure handling; no Google account accessed. |
| Package audit | **23 passed** | Exact ASAR/host/manifest identity, local fonts/licenses, CSP/isolation and correspondence to package evidence. |

These counts are not summed into an accuracy/reliability score. The executable is an unsigned local development package. Source support beyond the synthetic case, the full held-out memory gate, native dialogs, accessibility, account live reads and provider writes remain unqualified. Earlier 0.2 reports are historical and do not certify this build.

## Remaining work and human dependencies

The plan's first three implementation steps are delivered as the explicit selected-file slice. The rest remains staged: Google/Notion reads and Gmail content projections; verified account identity/resource lifecycle; read-only productivity orchestration; one separately authorized write per provider; safe repository reads/edit/test adapters and GitHub actions; Drive/Docs/Sheets; full profile/skill publishing, memory forgetting and reminders. Account consent is necessary but is not proof these adapters are finished. No send was authorized or attempted.

Human input is needed for Google Desktop client/consent, Notion connection/workspace/content choice and GitHub product repository authorization. No one needs to pick W-workers, paste tokens, perform code integration or repeatedly approve unchanged operations. W37 remains disconnected. The earlier app-only computer-use test returned non-target imagery and was stopped before clicks/typing; it is not retried or reported as native success.

Detailed code/package fingerprints are in [CONSOLIDATED-RESULTS.json](CONSOLIDATED-RESULTS.json). Use the manual demo rather than destructive experiments against normal Iron Web or a user repository.
