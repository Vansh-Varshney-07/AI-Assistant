Title: Choose retention, deletion and outbound data controls
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 04

## Question

What enforceable local data-control promise covers memory, raw connector data, logs, skills, backups and remote inference? Decide retention, encryption/key recovery, export/forget semantics, restore tombstones and allowed destinations per data class.

## Recommended direction — not a resolved decision

Expose local locations and egress receipts; keep credentials outside agents; separate health/work/personal data; invalidate derived material and dependent workflows when forgetting. State provider-copy limits explicitly.

## Resolution evidence

A reviewed data inventory and retention/egress/delete/export/restore policy with implementable guarantees and unresolved key-management choices recorded.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Choose the orchestrator-only memory contract](04-memory-contract.md)
