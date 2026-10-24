Title: Choose task approvals, egress and standing grants
Parent: ../map.md
Labels: wayfinder:prototype
Type: prototype
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 01, 02, 03

## Question

Which task/data preview, exact-change review and revocable grant UX supports familiar chat and safe tasks in both views? Decide how configured read/model scopes are approved, protected writes, memory promotion, settings changes, budgets and recurring limits.

## Proposed direction — not a resolved decision

Use explicit narrow scopes, exact content/resource/version binding and handler-enforced checks. Expand complex approvals into the main app; no prompt self-approval, global unattended bypass or implied permission from connecting an account.

## Comments

Charted for the new MVP; not worked or approved as a technical design. Claim before working. Record the user's actual decision and evidence on resolution; do not answer for the human.

## Prerequisites

- [Choose the main-app and quick-window state contract](01-app-quick-state.md)
- [Choose Iron Web authority and memory-release invariants](02-memory-authority.md)
- [Choose the plugin configuration and capability contract](03-plugins-capabilities.md)
