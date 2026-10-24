Title: Choose the work-item model and sync ownership
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 02, 06, 07

## Question

How do obligations from Gmail and WhatsApp, local notes, Notion tasks and Calendar events map onto a common work item? Decide authoritative fields, edits from both sides, conflict handling, source updates, recurring instances and scheduler recovery.

## Recommended direction — not a resolved decision

Use a local structured work-item/journal model with explicit external IDs and per-field ownership; treat extracted dates/assignees as proposals; never infer agreement from an external edit without a defined rule.

## Resolution evidence

A source-of-truth and conflict matrix plus examples for changed deadlines, duplicated messages, edited Notion tasks, missed Calendar updates and uncertain committed writes.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Establish productivity connector feasibility](02-productivity-connectors.md)
- [Choose interactive approvals and recurring grants](06-approvals-recurring.md)
- [Choose retention, deletion and outbound data controls](07-data-control.md)
