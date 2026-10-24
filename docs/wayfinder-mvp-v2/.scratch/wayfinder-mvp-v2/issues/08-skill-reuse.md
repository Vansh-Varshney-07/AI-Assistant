Title: Choose skill governance and workflow-template reuse
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 03, 04, 06

## Question

How are procedures and workflow templates discovered, proposed, reviewed, tested, versioned and rolled back while preserving capabilities and data scope? Decide required manifest fields and how a completed workflow suggests a skill.

## Proposed direction — not a resolved decision

Distinct skill/template/run identities, reviewed diffs and pinned versions. Loading a skill cannot install tools, obtain secrets or expand a grant.

## Comments

Charted for the new MVP; not worked or approved as a technical design. Claim before working. Record the user's actual decision and evidence on resolution; do not answer for the human.

## Prerequisites

- [Choose the plugin configuration and capability contract](03-plugins-capabilities.md)
- [Choose task approvals, egress and standing grants](04-approval-egress.md)
- [Choose workflow editing, validation and recovery semantics](06-workflow-contract.md)
