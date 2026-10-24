Title: Choose the general fitness adapter contract
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 03, 07

## Question

Which provider-neutral records, capability discovery, connection modes and conformance rules let fitness apps be added without changing the core assistant? Define weekly aggregation, overlapping sources, late changes, revocation and unsupported-provider fallback.

## Recommended direction — not a resolved decision

A normalized adapter SDK with cloud API, mobile bridge and file import modes; deterministic aggregation and coverage flags; keep raw measurements outside long-term fact memory and retain only approved goals/summaries/provenance.

## Resolution evidence

An adapter contract and test matrix validated with at least two synthetic provider shapes and an import format. User explicitly wants general fitness integration, not a single-app product.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Establish fitness, web and desktop feasibility](03-fitness-web-desktop.md)
- [Choose retention, deletion and outbound data controls](07-data-control.md)
