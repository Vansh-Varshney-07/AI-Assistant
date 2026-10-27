# Checkpoint 2: Codex-informed chat and theme revision

27 October 2026. Preview target 0.5.0-preview.2. The user rejected preview 1's chat and light palette. This checkpoint addresses that feedback; the larger 95-task rebuild remains in progress.

## Reused and changed

Used cloned REA against the installed Codex desktop archive, with two successful bounded semantic analyses and verified selected member hashes. [Research and limitations](../research/wayfinder-rebuild/codex.md). No Codex code, icons, assets, account state or agent runtime was copied. Reused Wayfinder's existing Electron isolation, named IPC, Hermes chat execution, Markdown components, local fonts, Lucide icons, memory engine and exact-action controls.

Consolidated overlapping renderer styles into one semantic light/dark system: neutral surfaces, readable ink, monochrome primary controls and status/focus colors. Removed the workspace ribbon and chat's duplicate global heading/footer. Chat is the initial destination. The chat title and recent-history search are compact; assistant replies have no repeated decorative identity or normal completion badge.

Chat now has one transcript scroller, bounded reading width and anchored autosizing composer. Editing stays available during sending/generation, with no automatic follow-up queue. In-memory drafts, selection and reading positions survive route navigation and are separated by owner, backend generation and space. Prompt text is not persisted in localStorage. History failure is distinct from an empty conversation; an accepted send remains accepted if only recent-title refresh fails. Lost acknowledgement still requires observation before another explicit request; stale results and stale cancellation polls remain fenced.

The [cross-plan revision](CODEX-REA-UX-REVISION.md) applies the same principles to onboarding, workflows, agents, connections, memory and approvals. Existing worker task/result definitions and resource authorization contracts were not modified.

## Verification record

Frontend: 70 tests passed. TypeScript and production renderer build passed. Ten headless rendered scenarios passed, including 600x600 and 900x700, both themes, primary-control contrast, keyboard navigation, draft recovery, long-reply scrolling, visible composer/stop control and no nonlocal requests or uncaught renderer errors. Own-app screenshots inspected in light and dark; no whole-desktop capture or native automation.

The initial packaged attempt correctly refused a stale embedded frozen-backend manifest. A full freeze and package rebuild are required; a new stage-only guard rejects mismatched embedded manifests rather than producing another incompatible package. This failure is separate from frontend fixture success. Final packaged and outer portable results are recorded below only after execution.

## Remaining scope

This does not complete all agent/workflow integrations, improve the model's underlying reasoning, qualify Google writes or W37 native effects, or add deferred fitness. Existing Docker Linux engine and managed Hermes/provider prerequisites remain. The executable remains unsigned. Preview 1 functional evidence is historical and does not imply user acceptance of this revision.

## Corrected package verification

Full backend freeze and portable rebuild succeeded. All three app/adjacent/frozen-internal release manifests match. The corrected hidden packaged app passed 18 checks, including two real synthetic model turns, canonical conversation history, no automatic memory publication, fresh backend generation on restart and persisted conversation without replay. All 34 static package checks passed, including the new embedded-manifest identity check. The delivered outer portable EXE passed all 11 fresh-directory checks, verified all 3007 extracted resources, completed real CPU memory inference and Hermes setup, opened an empty isolated memory store and quit normally. No live Google/Tavily operation or native desktop action was performed.

Executable: `desktop-app/release/Wayfinder-0.5.0-preview.2-Windows-x64.exe`, 514760926 bytes. SHA-256: `fb479c17ee96695e68c0dfc7898a09fab86352e1f52477637e925df050835e94`. Versioned checksum and verification JSON are adjacent to the local executable. Screenshots are under `desktop-app/test-results/rendered/`.
