Title: Choose Tavily-first research and model routing policy
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 02, 03, 04

## Question

When should chat use Tavily search/extract/crawl/map, local documents, private service APIs or an optional browser adapter? Specify disclosure, source coverage, partial failures, limits and Lightning/Ultra/provider routing including auxiliary calls.

## Proposed direction — not a resolved decision

Tavily is the preferred suitable public-web path. Retain service/workspace-specific operations and budgets; never send private sessions/memory through a public scrape route merely because it is connected.

## Comments

Charted for the new MVP; not worked or approved as a technical design. Claim before working. Record the user's actual decision and evidence on resolution; do not answer for the human.

## Prerequisites

- [Choose Iron Web authority and memory-release invariants](02-memory-authority.md)
- [Choose the plugin configuration and capability contract](03-plugins-capabilities.md)
- [Choose task approvals, egress and standing grants](04-approval-egress.md)
