Title: Choose reusable skill review and versioning
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 01, 05, 06

## Question

How are reusable procedures created, reviewed, tested, published and rolled back without copying user secrets or expanding tool permissions? Decide skill manifests, candidate generation, write approval and runtime version binding.

## Recommended direction — not a resolved decision

Skills are reviewed versioned procedures with declared capabilities and test cases; workers propose changes, the user reviews diffs, and gateway grants remain authoritative.

## Resolution evidence

A skill lifecycle, manifest fields and accept/reject/rollback examples; no auto-installation or mutation during this ticket.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Establish Hermes isolation and extension boundaries](01-hermes-boundaries.md)
- [Choose tool discovery and capability enforcement](05-tool-routing.md)
- [Choose interactive approvals and recurring grants](06-approvals-recurring.md)
