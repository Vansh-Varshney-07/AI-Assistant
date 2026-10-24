Title: Choose workflow editing, validation and recovery semantics
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 02, 03, 04

## Question

Which versioned workflow/template/run/step model supports natural-language and form-created plans, dependencies, dynamic workers, approval pauses, output validation and safe restart? Define simple-chat/atomic shortcuts and uncertain-effect reconciliation.

## Proposed direction — not a resolved decision

Start with an editable step list and dependency view, transactional run records, operation IDs and deterministic validation. Avoid a forced giant workflow for every question and do not repeat uncertain writes blindly.

## Comments

Charted for the new MVP; not worked or approved as a technical design. Claim before working. Record the user's actual decision and evidence on resolution; do not answer for the human.

## Prerequisites

- [Choose Iron Web authority and memory-release invariants](02-memory-authority.md)
- [Choose the plugin configuration and capability contract](03-plugins-capabilities.md)
- [Choose task approvals, egress and standing grants](04-approval-egress.md)
