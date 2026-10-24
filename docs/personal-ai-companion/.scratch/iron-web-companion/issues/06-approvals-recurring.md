Title: Choose interactive approvals and recurring grants
Parent: ../map.md
Labels: wayfinder:prototype
Type: prototype
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 04, 05

## Question

What exact plan preview, action preview and standing-grant contract implements ask-before-applying while allowing the user's narrowly preapproved recurring jobs? Decide approval consumption, expiry, revocation, absent-user behavior, changed inputs and uncertain outcomes.

## Recommended direction — not a resolved decision

Show a plan before tools and the exact payload/diff before effects; bind single actions to reviewed content and context; recurring grants specify accounts, data, operations, destination, schedule, limits and expiry. No broad cron autoapproval.

## Resolution evidence

A small non-executing review-panel prototype and user response to accept/reject/edit, changed recipient, expired grant and weekly-summary scenarios.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Choose the orchestrator-only memory contract](04-memory-contract.md)
- [Choose tool discovery and capability enforcement](05-tool-routing.md)
