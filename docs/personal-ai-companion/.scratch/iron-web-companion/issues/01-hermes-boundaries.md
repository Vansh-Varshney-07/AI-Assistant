Title: Establish Hermes isolation and extension boundaries
Parent: ../map.md
Labels: wayfinder:research
Type: research
Status: resolved
Mode: AFK
Assignee: Codex research agent — Hermes
Blocked by: none
Context: ../research/hermes-boundaries.md

## Question

Which current Hermes extension points can support orchestrator-only Iron Web access, task-scoped workers, metadata-based tool discovery, approvals and reusable skills? Which built-in behaviors could bypass that boundary, and what must be enforced outside prompts?

## Comments

Claimed before investigation. Public primary sources only; inspect no private accounts. Findings belong in the linked context asset; append the resolution under Answer when finished.

## Answer

Use a primary-only Iron Web memory-provider adapter and narrowly granted worker broker toolsets. Hermes isolates child conversations and skips their external memory provider, but inherited tools/shared host access require additional enforcement. Hermes Tool Search is currently BM25, so vector metadata matching is an added discovery layer and must remain separate from deterministic authorization. Enforce user approvals and narrow recurring grants inside a fail-closed execution broker; Hermes dangerous-shell approval and fail-open middleware do not alone satisfy this requirement. Reuse reviewed, versioned Hermes skills without granting additional capabilities. Findings and acceptance gates: [Hermes isolation and Iron Web integration boundaries](../research/hermes-boundaries.md).

Research only: no runtime/code/service changes. Git exception: workspace and standalone source have no Git metadata, so no research branch/push was possible.
