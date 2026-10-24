# Basis, evidence and limits

Revision date: 24 October 2026. This note distinguishes source facts from proposed integration. No private accounts, model credentials, live app tests or runtime policy changes were used.

## Inputs

- Latest user request: minimal configurable main app, persistent plain quick-chat window, general chatbot/tool behavior, Hermes integrations, NemoClaw runtime configuration, Tavily where appropriate, highest-priority persistent memory, reusable skills and controlled execution.
- [Supplied master plan](../sources/SUPPLIED-MASTER-PLAN.md), read in full. Latest user choices supersede its animal/capture scope and delayed-UI ordering.
- Earlier Iron Web code inspection, design/research artifacts and 30-page foundation PDF. Their prior test counts are historical, not certification of this proposed product. The source repository currently has Git metadata; old notes saying it did not are preserved as dated history.

## Fresh primary-source checks in this revision

Hermes documents progressive tool search/describe/call; deferred underlying calls still pass the real tool's execution checks. The vector matching extension must integrate with the controlled capability path. [Tool Search](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-search)

Hermes delegation uses fresh child context with inherited tool access; workspace instruction context is an exception. Durable completed-result delivery does not resume an executing child after a process crash. These facts justify explicit worker access restrictions and separate workflow recovery. [Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)

Tavily Search and Extract expose distinct APIs. Extract can return successful and failed URLs in one response, so the app must inspect both rather than equate HTTP success with complete retrieval. [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search), [Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract)

## Reused primary references requiring pinned-runtime validation

The earlier same-day research reviewed NVIDIA's description of NemoClaw as management/lifecycle integration for Hermes on OpenShell, and OpenShell's execution controls. Fresh fetches of these pages returned cache/status failures during this revision. The plan therefore treats them as version-sensitive integration inputs, not newly tested installed capabilities. Recheck the selected versions, supported topology, managed tool transports, provider route and actual denial behavior before enabling workers.

- [NemoClaw ecosystem](https://docs.nvidia.com/nemoclaw/user-guide/hermes/about/ecosystem).
- [NemoClaw platform support](https://docs.nvidia.com/nemoclaw/user-guide/hermes/reference/platform-support).
- [OpenShell architecture](https://docs.nvidia.com/openshell/about/architecture).
- [Hermes memory-provider contract](https://hermes-agent.nousresearch.com/docs/developer-guide/memory-provider-plugin).
- [Hermes middleware contract](https://hermes-agent.nousresearch.com/docs/developer-guide/middleware).

The application gateway—not prompt text or assumed middleware failure behavior—must enforce approvals. A shared worker sandbox or inherited plugin list is not accepted as proof of orchestrator-only memory. This is a proposed integration requirement.

## Existing Iron Web reuse boundary

Relevant source under `D:\Opencode_\memory_system` includes `memory/engine.py`, lifecycle modules, `memory/spaces.py`, `memory/workbench.py`, shared service/journal, context compiler/contracts, tests and operations scripts. Reuse working memory and receipt primitives. Inventory the current behavior before implementing this plan; no current test suite was run merely to create it.

The old direct workbench is a local developer tool, not the app's worker authorization boundary. The generic workflow scope must not assume retained travel-specific context contracts already support all domains. The PDF's journal-as-authority recommendation remains a real architecture/migration decision.

## Claims deliberately not made

No universal compatibility with every daily-life app; no permanent uptime while Windows sleeps; no guaranteed perfect semantic recall; no competitor feature parity; no automatically certified sandbox; no new Nebius account/model availability or pricing check; no erasure guarantee for third-party copies already transmitted. The design provides explicit settings, measurable gates and honest unsupported/degraded states instead.
