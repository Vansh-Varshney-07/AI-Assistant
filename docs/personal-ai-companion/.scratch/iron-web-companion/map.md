Title: Iron Web desktop companion and delegated workflows
Labels: wayfinder:map
Status: charted — human decisions open

## Destination

A reviewable product and architecture plan for an animal desktop companion with remembering chat, work and personal scheduling, weekly fitness summaries, web/GitHub integrations, reusable skills and user-controlled actions. The plan must preserve orchestrator-only Iron Web access, give workers bounded context, and define tool discovery separately from execution permission.

## Notes

- Planning only. Creating this map does not connect accounts, capture the desktop, schedule jobs, send messages or authorize implementation.
- Existing source: `D:\Opencode_\memory_system`. Existing validation reports are historical evidence, not a new test run in this planning session.
- This portable planning workspace uses the local-Markdown tracker convention. Each decision has its own child issue; native dependencies are unavailable, so `Blocked by` lines express them.
- The user explicitly invoked Wayfinder. Consult Wayfinder, grilling, domain-modeling and research skills when continuing. Resolve no more than one non-research ticket in a session; human decisions require the human's response.
- Existing user requirements are constraints, not newly resolved tickets: orchestrator-only memory access; workers receive relevant context; ask before applying tasks; independent memory IDs; persistent memory; reusable skills; tool metadata and semantic discovery; all listed feature areas stay in scope for the overall product.
- User confirmed 24 October 2026: first release is one Windows device with local storage; narrowly approved recurring jobs are allowed; desktop scanning and screen capture are excluded for now. The animal popup remains in scope.
- Neither source nor this planning workspace has Git metadata. Research is captured in linked local assets; research branches cannot be pushed without an identified Git repository and remote. Do not initialize or publish a repository just to satisfy the research convention.
- To bind future maps to a hosted issue tracker, run `/setup-matt-pocock-skills` in the intended project.
- Foundation Research update: [source-page integration](research/foundation-report-integration.md) adds a research-and-follow-through hackathon slice, Nebius inference validation, sandbox compatibility/fallback, disclosure and cost controls, stronger recovery gates and submission evidence. Existing human decisions remain open. The earlier no-Git observation was true at charting; the source now contains Git metadata, but this update creates no commit or tracker publication.
- Manual delivery view: [phase-by-phase plan](../../PHASE-BY-PHASE-PLAN.md) adds testable increments, a synthetic fixture kit, individual acceptance cases and phase signoff. This is a build/handoff plan, not a resolution of the open human decision tickets or a claim that future features pass tests.

## Decisions so far

Research findings resolved during charting; implementation recommendations remain open decisions:

- [Establish Hermes isolation and extension boundaries](issues/01-hermes-boundaries.md): Hermes provides useful extension points, but custom memory access and approval enforcement need an explicit trusted boundary.
- [Establish productivity connector feasibility](issues/02-productivity-connectors.md): Named productivity APIs are usable with bounded permissions; WhatsApp eligibility, event delivery and uncertain-write recovery need explicit gates.
- [Establish fitness, web and desktop feasibility](issues/03-fitness-web-desktop.md): Fitness needs provider adapters/import/bridges; Tavily is research access; the animal UI remains and screen capture is excluded.

## Not yet specified

- Provider-specific fitness adapters and onboarding details will grow behind the general SDK; the user explicitly wants a general system, not a single-app choice.
- Specialized connectors beyond the named applications; “everything” becomes a versioned connector backlog as actual use cases appear.
- Detailed animal artwork, animation and notification style, pending the companion interaction prototype; desktop capture is outside this map.

## Out of scope

- Implementing the product or modifying the validated memory engine in this planning session.
- Desktop scanning, screen capture, screen recording and saving desktop imagery: explicitly removed by the user for this plan on 24 October 2026.
- Connecting real accounts, requesting OAuth grants, reading private messages or fitness data, or capturing screens while making this plan.
- Treating vector similarity or possession of a memory-space ID as authorization.
- Claiming that data already sent to a third-party service can always be erased by this application.

## Scope boundary for this map

Online/multi-user deployment and cross-device synchronization are later efforts after the local release. Preserve identity boundaries now; do not silently add their implementation to this destination.

[Open decision frontier and dependency graph](frontier.md) · [Full proposed product plan](../../PLAN.md) · [Domain glossary](../../GLOSSARY.md)
