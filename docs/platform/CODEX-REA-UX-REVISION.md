# Codex-informed UX revision and acceptance gates

The user rejected preview 1's chat and light palette. Its functional evidence remains historical; it does not establish UX acceptance. This revision applies the [bounded Codex REA findings](../research/wayfinder-rebuild/codex.md) throughout the existing 95-task plan. It adds no provider, agent loop, memory engine, advertising, sketch feature or broader approval scope.

| Gate | Atomic implementation and verification |
| --- | --- |
| U01.1 Theme | Consolidate three overlapping stylesheets into one semantic token source. Neutral light surfaces/ink, monochrome primary actions, explicit focus/error/success. Verify both themes and actual rendered controls. |
| U01.2 Shell | Conversation-first entry, one compact chat title, remove repeated workspace ribbon/page heading/footer on chat. Preserve navigation and space selection. Check small windows and keyboard navigation. |
| U01.3 Composer | Anchor composer to available viewport; one transcript scroller and bounded reading width. Separate history, sending, generation and stopping. Allow drafts while generating; no automatic queue. Check 600x600 and 900x700. |
| U01.4 Recovery | Scope in-memory draft/selection/scroll caches by owner, backend generation and space. Preserve drafts across navigation; no prompt localStorage. Keep history failures distinct from empty history and accepted sends distinct from title refresh failure. Verify stale response, lost acknowledgement, cancellation and no replay. |
| U01.5 Evidence | Inspect own-app screenshots in both themes and window sizes. Synthetic fixture evidence is separate from live provider and packaged executable evidence. Rebuild and requalify any executable before declaring it updated. |

Apply these rules to the remaining phases:

- Onboarding: one decision per step, honest prerequisite progress, editable recovery, optional connections and explicit model consent. No faux progress or automatic permission grants.
- Agents: task-first entry, genuine availability and required connection/resource visible before execution. Preserve logical Hermes roles; a card or icon does not mean a role is qualified.
- Workflows: one run title, readable steps and separate queued/running/stopping/uncertain states. Show evidence and recovery near the affected step; preserve user reading position.
- Connections: consistent neutral cards, color for status, explicit scope and disconnect/revoke. Missing authorization remains unavailable; no fake success.
- Memory: readable source material first, provenance and technical detail on demand. Reviewed writes remain separate from conversation.
- Approvals: dedicated exact-target/payload/resource/expiry review, clear reject and single-use approval, disabled/loading feedback. Backend enforcement remains authoritative.
- Activity: concise outcome first, detailed receipts on demand. Preserve failed, denied, revoked, expired and uncertain outcomes.

The wider P01-P14 backlog remains active. U01 is a UI repair gate before UX-dependent milestones are accepted. Historical completed service/contract checks are not reset; visual acceptance must be repeated against the new renderer. W37 native effects and deferred fitness remain outside this revision. Account authorization is required only when a real connector needs it.

Implementation evidence: [Checkpoint 2](REBUILD-CHECKPOINT-02.md). U01.1-U01.4 have passing frontend/rendered checks; U01.5 includes inspected screenshots and matching packaged-app checks. User UX acceptance remains pending direct inspection.
