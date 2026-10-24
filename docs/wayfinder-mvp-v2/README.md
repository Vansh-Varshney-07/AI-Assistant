# WAYFINDER MVP v2

**Current scope:** a minimal Windows personal AI app plus a persistent plain quick-chat window. No animal interface, desktop scanning/capture or always-on microphone.

Start with [the new master plan](PLAN.md), then use [the build/manual-test phases](PHASES.md) and [the memory-quality contract](MEMORY-QUALITY-CONTRACT.md).

- [Manual acceptance sheet](MANUAL-ACCEPTANCE.csv).
- [Phase signoff sheet](PHASE-SIGNOFF.csv).
- [Wayfinder decision map](.scratch/wayfinder-mvp-v2/map.md) and [open frontier](.scratch/wayfinder-mvp-v2/frontier.md).
- [Domain glossary](GLOSSARY.md).
- [Scope reconciliation](SCOPE-CHANGES.md).
- [Sources and existing-system basis](research/BASIS.md).
- [Synthetic manual inputs](fixtures/README.md).

The app lets a user chat, configure reviewed plugins/connections, create/edit/version workflows, inspect and control retained memory, manage reusable skills, approve changes and inspect runs. The quick window uses the same service and authority; it is not another agent or a desktop observer.

Tavily is the preferred suitable public-web route. Hermes executes agent work and integrations. NemoClaw manages the compatible runtime/configuration; OpenShell adds applicable execution restrictions. Wayfinder must implement its own workflow state, semantic capability matching, consent/approval and trusted execution contracts around these components. Existing Iron Web is reused and remains orchestrator-only.

The plan has three checkpoints: useful chat/web/memory by Phase 4; editable/reusable/scheduled workflows by Phase 8; accepted memory/security/recovery plus starter connectors and packaging by Phase 10. Connector breadth comes through tested adapters, not a promise that every service/account already works.

This is a planning bundle. No app feature, real account connection or new runtime test is completed by its creation. Every acceptance row starts Not run. Existing validation is historical evidence only. Open design tickets stay open; their recommendations are not human decisions made by an agent.

This bundle supersedes the earlier animal-first MVP/delivery scope. Prior files are preserved as history. The supplied master text is retained unmodified under `sources/` for traceability; latest user choices and PLAN.md determine the active scope.
