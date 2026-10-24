Title: Establish fitness, web and desktop feasibility
Parent: ../map.md
Labels: wayfinder:research
Type: research
Status: resolved
Mode: AFK
Assignee: Codex research agent — device and web capabilities
Blocked by: none
Context: ../research/fitness-web-desktop.md

## Question

Which official capabilities and restrictions shape fitness summaries across Apple Health/Android Health Connect/vendor apps, Tavily web access versus interactive browsing, and a small Windows animal overlay for chat, approvals, reminders and status? Identify required mobile bridges, permissions and connector limitations. Desktop scanning and screen capture were explicitly excluded by the user after this ticket was claimed. Recommend no medical interpretation.

## Comments

Claimed before investigation. Public primary sources only. Do not collect health data or capture the user's desktop. Findings belong in the linked context asset.

## Resolution comment

### Answer

The user wants general fitness integration: define a provider-neutral adapter SDK and support API, mobile-bridge and import modes rather than hardwire one app. Health Connect and HealthKit require mobile/device authorization paths; neither is a universal Windows cloud connector. Provider availability and migration status must be verified per adapter. Google Health source fetches differed during research, so the bundle does not assert universal onboarding closure or a verified shutdown date. Tavily supplies separate search/extract/crawl/map operations; interactive browser actions require a separate adapter. A native Windows animal overlay can provide the requested controls. User removed desktop capture/scanning from scope; no capture capability belongs in the current plan. Summaries should cover observed fitness/wellness activity and data coverage, without diagnosis.

Full constraints, design implications, official sources and acceptance gates: [Fitness, Tavily and Windows companion feasibility](../research/fitness-web-desktop.md).

### Status

Resolved by public primary-source research on 24 October 2026, with parent verification notes on conflicting Google Health fetches. No accounts, data collection, installation, application changes or capture were performed. Local research assets replace branch/push because no Git repository exists here. Remaining contract and approval choices belong to human decision tickets; choosing one particular fitness app is not required to plan the general SDK.
