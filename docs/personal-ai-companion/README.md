# Iron Web companion planning bundle

Created with the explicitly invoked Wayfinder skill on 24 October 2026. This bundle is a local Markdown issue tracker and product plan; it does not implement features or authorize account access.

Start with [Product and architecture plan](PLAN.md).

For building and testing incrementally, use the [Phase-by-phase build and manual test plan](PHASE-BY-PHASE-PLAN.md), [synthetic test kit](manual-test-kit/README.md), [manual acceptance sheet](manual-acceptance.csv) and [phase signoff sheet](phase-signoff.csv). Each handoff supplies a usable increment, exact run instructions, expected observations, actual evidence and a return path. All test statuses begin Not run.

Update: the 30-page **Personal AI Hackathon Foundation Research** PDF is incorporated into the [foundation integration record](.scratch/iron-web-companion/research/foundation-report-integration.md). It prioritizes a cited research brief, approved durable decision and one controlled follow-up as the hackathon slice, while preserving the broader product roadmap. No proposed feature or PDF test is represented as newly implemented or passed.

Continue planning through [Iron Web desktop companion and delegated workflows](.scratch/iron-web-companion/map.md), its [open frontier and dependency graph](.scratch/iron-web-companion/frontier.md), and the [domain glossary](GLOSSARY.md).

The map has **16 decision tickets**: **3 research tickets resolved**, **13 human decisions open**. Two are available first:

- [Choose the orchestrator-only memory contract](.scratch/iron-web-companion/issues/04-memory-contract.md).
- [Choose tool discovery and capability enforcement](.scratch/iron-web-companion/issues/05-tool-routing.md).

Use `/wayfinder` with the map or a named ticket path to continue. Claim a ticket before working it; human decisions need the user's response. Charting did not silently resolve the design proposals. Research recommendations are inputs to those decisions.

## Confirmed boundaries

- Windows and local storage first.
- Only the orchestrator accesses Iron Web; workers get selected context.
- Preview plans and exact actions; allow explicitly bounded, revocable recurring grants.
- General fitness adapter framework with provider-specific API/mobile/import paths.
- Animal popup for chat, approvals, reminders and status.
- Desktop scanning, screen capture and recording excluded at the user's request.

## Included features

Work intake from Gmail and WhatsApp Business; weekly fitness summaries; remembering chat and proposed voice support; general tasks/notes with Notion, saved local notes and Google Calendar; Tavily web research; selected GitHub operations; persistent memory; reusable reviewed skills; data inspection/export/forget and outbound-data controls.

The proposed build sequence is trusted memory/worker boundaries → controlled tool execution and approvals → first complete user workflow → productivity breadth and general fitness adapters → research/skills/UX extensions. Individual components can proceed in parallel only after their prerequisite decisions and boundary tests pass. Online/multi-user/device-sync implementation follows the local release.

## Research assets

- [Existing Iron Web baseline](.scratch/iron-web-companion/research/iron-web-baseline.md).
- [Hermes isolation and extension boundaries](.scratch/iron-web-companion/research/hermes-boundaries.md).
- [Productivity connector feasibility](.scratch/iron-web-companion/research/productivity-connectors.md).
- [Fitness, Tavily and Windows companion feasibility](.scratch/iron-web-companion/research/fitness-web-desktop.md).

Facts use public primary-source references. Connector availability and Hermes contracts must be rechecked against pinned versions before implementation. No services were connected or tasks scheduled. Previous memory-system test counts are historical evidence, not tests of this proposed product.

## Tracker convention

Wayfinder's canonical map is under `.scratch/iron-web-companion/`, with one child file per ticket. `Parent`, `Labels`, `Type`, `Status`, `Assignee`, and `Blocked by` fields carry local tracker state. Human-facing links use ticket names. Git metadata and a remote tracker were absent, so research was saved as local assets rather than pushed branches. `/setup-matt-pocock-skills` can configure a hosted issue tracker later.
