Title: Choose the orchestrator-only memory contract
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 01

## Question

Which service boundary, identity mapping and context-packet contract will preserve existing Iron Web spaces while giving Hermes workers no memory access? Settle primary-only provider behavior, native-memory policy, worker sandbox constraints, generic scope migration and stale-context checks.

## Recommended direction — not a resolved decision

Keep the dual-store engine and existing shared-service primitives; map owner/profile to authorized space on the server; give workers immutable packets and broker tools only. Version the travel-specific context contract rather than silently reinterpreting trip_id.

Foundation report update: test explicit orchestrator-only memory operations before enabling automatic provider hooks. Decide the PDF's journal-authority proposal against the actual dual-store architecture: preserve the current authority or design a versioned, tested migration; do not simply relabel the receipt journal. Add consent, source authority, revision, tombstone and restored-deletion behavior to the contract. [Report integration](../research/foundation-report-integration.md).

## Resolution evidence

A precise principal/space/task/snapshot contract, migration/compatibility rule and denial paths, reviewed with the user. No runtime change in this ticket.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Establish Hermes isolation and extension boundaries](01-hermes-boundaries.md)
