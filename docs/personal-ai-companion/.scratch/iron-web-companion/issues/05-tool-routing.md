Title: Choose tool discovery and capability enforcement
Parent: ../map.md
Labels: wayfinder:grilling
Type: grilling
Status: open
Mode: HITL
Assignee: unassigned
Blocked by: 01

## Question

How will structured work intent and reviewed tool metadata produce a vector/lexical candidate list while keeping permission deterministic? Decide catalog fields, eligibility filtering, schema exposure, no-match behavior, MCP inheritance and the trusted gateway boundary.

## Recommended direction — not a resolved decision

Extend Hermes discovery with a separate versioned tool-vector catalog; grant only eligible operations; enforce arguments and policy inside gateway handlers so middleware failure cannot permit execution.

## Resolution evidence

An agreed catalog/intent/grant/execution contract plus read-versus-send, poisoned-description and no-match examples.

## Comments

Charted, not worked. Claim before investigation. Human-in-the-loop decisions require the user's response; do not answer on their behalf.

## Prerequisites

- [Establish Hermes isolation and extension boundaries](01-hermes-boundaries.md)
