Title: Choose background availability and scheduled-run ownership
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 01, 04, 06

## Question

What does persistent quick access mean while Windows is running, asleep, offline or restarting? Decide startup/background/quit behavior, one scheduler owner, occurrence leases, missed-run policy and grant invalidation after workflow edits.

## Proposed direction — not a resolved decision

A user-controlled local service with visible state; narrow recurring grants and durable occurrences. Do not claim permanent service availability or exact-once effects across arbitrary providers.

## Comments

Charted for the new MVP; not worked or approved as a technical design. Claim before working. Record the user's actual decision and evidence on resolution; do not answer for the human.

## Prerequisites

- [Choose the main-app and quick-window state contract](01-app-quick-state.md)
- [Choose task approvals, egress and standing grants](04-approval-egress.md)
- [Choose workflow editing, validation and recovery semantics](06-workflow-contract.md)
