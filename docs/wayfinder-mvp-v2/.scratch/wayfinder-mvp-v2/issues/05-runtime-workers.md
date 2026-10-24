Title: Choose runtime profiles and worker enforcement
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 02, 03, 04

## Question

Which pinned Hermes/NemoClaw/OpenShell topology and effective identity/filesystem/network/tool restrictions establish worker isolation on the chosen Windows-local setup? Define the safe fallback and what runtime settings the app can change.

## Proposed direction — not a resolved decision

Trial actual allow/deny behavior before enabling workers. Only the orchestrator reaches memory; effective worker toolsets, alternate access paths and optional workspace executors require explicit restriction proof.

## Comments

Charted for the new MVP; not worked or approved as a technical design. Claim before working. Record the user's actual decision and evidence on resolution; do not answer for the human.

## Prerequisites

- [Choose Iron Web authority and memory-release invariants](02-memory-authority.md)
- [Choose the plugin configuration and capability contract](03-plugins-capabilities.md)
- [Choose task approvals, egress and standing grants](04-approval-egress.md)
