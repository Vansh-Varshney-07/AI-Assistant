Title: Establish productivity connector feasibility
Parent: ../map.md
Labels: wayfinder:research
Type: research
Status: resolved
Mode: AFK
Assignee: Codex research agent — productivity connectors
Blocked by: none
Context: ../research/productivity-connectors.md

## Question

What do official Gmail, WhatsApp Business, Notion, Google Calendar and GitHub APIs permit for the requested workflows? Identify account prerequisites, read/write boundaries, OAuth or app scopes, event/sync mechanisms and material limitations that affect this plan. Distinguish business API messages from an arbitrary personal WhatsApp history and native Notepad files from a cloud notes API.

## Comments

Claimed before investigation. Public primary sources only. Do not connect accounts or install integrations. Findings belong in the linked context asset.

## Answer

Gmail intake, selected Notion notes/tasks, Calendar scheduling and scoped GitHub operations are feasible. Use separate read/write/send capabilities and an approval broker. Gmail readonly is a restricted OAuth scope; public/server-side processing introduces verification and security-assessment constraints. Notion capabilities and explicit page sharing bound access; current API version and uncertain committed-write responses need deliberate handling. Calendar/Gmail cursors and reconciliation are required; push is not a durable workflow ledger. GitHub Apps provide repository-scoped, granular permissions; failed webhooks require recovery rather than assumed automatic retry.

WhatsApp is scoped to the connected Business API account/number and delivered events; arbitrary personal-device history is not established. Current messaging windows/templates were verified from Meta's official policy. Production account onboarding, coexistence/history imports and current AI-provider/platform eligibility require explicit validation for the selected business path; inaccessible current terms were not guessed. Native Notepad should be an approved local-file adapter, separate from cloud Notion access.

Research and source links: [Productivity connector feasibility](../research/productivity-connectors.md). This was file-based public-source investigation; no repository/remote was available for a pushed research branch. No accounts connected and no messages, installations or runtime changes made.
