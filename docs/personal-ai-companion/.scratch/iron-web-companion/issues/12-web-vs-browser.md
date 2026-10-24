Title: Choose the web research and interactive browser boundary
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 03, 05, 06

## Question

Does the local release use Tavily research only, or also require interactive authenticated browser actions? Specify operation-level URL/domain, data egress, cost and page-count limits, and how untrusted content is handled.

## Recommended direction — not a resolved decision

Start with Tavily search/extract/crawl/map; keep interactive browser login/click/form operations as a separately approved adapter with distinct credentials and actions if required.

## Resolution evidence

A precise supported web capability list and reviewed examples; do not claim Tavily performs browser actions absent from its contract.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Establish fitness, web and desktop feasibility](03-fitness-web-desktop.md)
- [Choose tool discovery and capability enforcement](05-tool-routing.md)
- [Choose interactive approvals and recurring grants](06-approvals-recurring.md)
