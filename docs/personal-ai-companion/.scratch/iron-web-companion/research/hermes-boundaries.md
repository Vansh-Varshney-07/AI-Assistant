# Hermes isolation and Iron Web integration boundaries

Research date: 24 October 2026. Public primary documentation and current `NousResearch/hermes-agent` main source inspected; Hermes is evolving, so pin a release/commit and repeat the acceptance checks before implementation. No Hermes installation, private connector, or live account was inspected or changed. This is an integration decision, not an implementation claim.

## Decision

Use Hermes as the agent runtime, with an Iron Web adapter owned by the orchestrator. Workers receive immutable task context and narrowly granted toolsets. Keep durable workflow state and user approvals in a separate trusted execution service. Vector similarity proposes tools; deterministic policy grants their use. For Windows/local first, initially give workers broker tools only; unrestricted host terminal/file tools defeat the intended boundary.

## Current official behavior

### Delegation is conversation isolation

`delegate_task` starts a fresh child conversation; goal/context carry the assignment and only the final summary returns to the parent. Project instruction files are an exception: workspace context can be injected. Enabled toolsets are inherited, including `execute_code`; the usual child blocks cover built-in memory, clarification, messaging and scheduling. The working directory is shared by default. Optional Git worktrees separate edits, not OS authority. [Delegation guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)

Current construction explicitly sets `skip_memory=True` and `skip_context_files=True`; the focused prompt is built separately with workspace context. The blocklist names the built-in `memory` tool; it is not a universal denial of every memory-shaped custom tool. Narrowed child toolsets can have parent MCP toolsets appended when `delegation.inherit_mcp_toolsets` is true, its current default. [Child construction](https://github.com/NousResearch/hermes-agent/blob/main/tools/delegate_tool.py), [toolset resolver](https://github.com/NousResearch/hermes-agent/blob/main/tools/delegate_tool_toolsets.py), [configuration](https://github.com/NousResearch/hermes-agent/blob/main/tools/delegate_tool_config.py)

`_init_memory` skips external-provider initialization when `skip_memory` is true. This supports orchestrator-only native provider integration, but is not filesystem/network protection against other inherited tools. [Initialization source](https://github.com/NousResearch/hermes-agent/blob/main/agent/agent_init.py)

The public plugin lifecycle API supports narrowing through `allowed_toolsets`, bounded serialized handles, result/status/cancel/steer operations and parent ownership checks. It currently rejects per-tool blocks, working-directory overrides and per-launch timeouts; after process restart reconnect cannot resurrect the child. Use explicit narrow toolsets, not unsupported request fields. [Subagent lifecycle API](https://hermes-agent.nousresearch.com/docs/developer-guide/subagent-lifecycle-api)

### Iron Web has a native extension route

Hermes supports one external memory provider, additive to its built-in stores. It can inject/prefetch context, synchronize completed turns, mirror native writes and handle session-end events. Automatic hooks may receive transcripts containing tool output; enabling a provider does not itself implement consent-aware Iron Web writes. [Provider behavior](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers)

A standalone plugin implements `MemoryProvider`, registers it and optionally exposes tools. Initialization provides profile/session identities and runtime context such as primary, subagent or cron. Provider state must bind to the supplied profile, use new instances rather than shared global mutable state, and use context-preserving background threads. These are particularly relevant to future concurrent users. Optional lifecycle hooks include prefetch, turn sync, session-end, pre-compression and memory-write notifications. [Provider plugin contract](https://hermes-agent.nousresearch.com/docs/developer-guide/memory-provider-plugin), [interface source](https://github.com/NousResearch/hermes-agent/blob/main/agent/memory_provider.py)

### Discovery already exists; vector routing would be our addition

Hermes Tool Search progressively exposes deferred MCP/plugin schemas through search, describe and call. Its current ranking is BM25 over names, descriptions, sources and parameter names, with stemming; it is not vector retrieval. The catalog is limited to the session's granted toolsets. Calling through the bridge retains underlying tool hooks, checks and approvals. Core tools generally remain directly exposed. [Tool Search](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-search)

### Approval settings are narrower than our product promise

Hermes dangerous-command approvals cover qualifying shell commands, not a universal requirement to approve every connector action. Manual mode prompts for dangerous commands. Cron and unattended modes default to deny at that gate; setting cron mode to approve is broad autoapproval, not a per-job grant. File write roots cover specific file tools, while local terminal still has the OS user's access. Containers also do not replace connector-level approval. [Security guide](https://hermes-agent.nousresearch.com/docs/user-guide/security)

Scheduled jobs run fresh sessions, can attach skills and deliver results; creation can be paused for review. The scheduler depends on a running gateway. Those properties are useful scheduling primitives, not proof of authorization for each proposed operation. [Cron guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)

Plugin middleware can shape/wrap tool execution, but exceptions are documented as fail-open. A policy implemented only by raising from middleware could therefore permit the base execution path. Put the decisive check inside the trusted tool handler/broker. [Middleware contract](https://hermes-agent.nousresearch.com/docs/developer-guide/middleware)

### Skills are reusable procedures

Hermes skills are discoverable knowledge documents and supporting files. Agent-created skills can be changed automatically; `skills.write_approval` stages all skill-management writes for review. [Skills guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) Built-in memory has a separate write-approval gate; disabling native stores and disabling the memory toolset have different effects on external providers. [Memory guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)

## Inferences and integration proposal

**Access boundary.** Register Iron Web through a primary-only provider; refuse unknown/non-primary contexts by default. Map authenticated owner/device/profile to `memory_space_id` server-side. A model-supplied ID is a selector, never authorization. Disable native user/profile memory if Iron Web must be the sole durable knowledge authority. Give worker launchers only role-specific broker toolsets; exclude Iron Web MCP/plugin tools, session search, arbitrary code/terminal/files and generic network clients. Inspect the resolved tool list, including MCP inheritance, before launch. For workers needing shell access later, use a distinct OS/container boundary without host memory mounts, credentials or direct store networking.

**Context exchange.** Issue a packet with workflow/task/agent/snapshot IDs, selected evidence/source IDs, constraints, expiry and output schema. Results contain findings, source references and proposed memory mutations. Only the orchestrator validates and commits proposals. Worker scratch state expires; workflows/checkpoints/action receipts persist separately. Reject malformed/schema-invalid results even if Hermes labels the child completed. Do not claim exactly-once external actions: reconcile provider receipts before uncertain retries.

**Tool matching.** Embed a separate tool catalog with tool ID/version, capability verbs (`search`, `fetch`, `scrape`, `draft`, `send`), service, input/output schema, account scope, read/write effect, data classifications and approval policy. Resolve a structured intent, retrieve candidates, then filter by owner, worker role, workflow grant, destination and available connection. Semantic relevance never grants permission. Unknown/ambiguous intents stop for clarification. The broker rechecks actual arguments and token expiry at execution, including calls made through discovery bridges or skills.

**Consent and narrow recurring jobs.** Present a concrete action preview before changes or external sends. An approval binds exact parameters, identity, memory space, destination, allowed tools, content/version digest, expiry and retry policy. A user can preapprove a narrow recurring job with a time window, bounded accounts/resources, output destination and allowed action types. Each run checks that grant; changed scope pauses for review. Keep cron dangerous-command mode deny; do not substitute global cron autoapproval or YOLO for the grant. Scheduled orchestrator runs get an explicitly authorized service identity, not automatic memory access merely because their platform is cron.

**Reusable skills.** Version reviewed procedures, required capabilities, schemas and tests separately from factual memories. Workers may load approved skills but cannot install/update them or gain credentials through skill environment declarations. A skill selects procedure, never expands a capability grant. Enable skill-write approval and review changes centrally.

## Acceptance gates before connecting accounts

1. Worker cannot discover/call Iron Web, read its files, reach its endpoint or access another space, including through bridges and terminal alternatives.
2. Concurrent orchestrators preserve owner/space/snapshot isolation across background provider hooks.
3. Denied, expired, modified or cross-space approvals cause zero external writes; middleware/plugin failure cannot bypass the broker.
4. A narrow recurring grant permits only its exact job; changed recipients, new tools or wider accounts pause it.
5. Restart preserves workflow state and consent receipts without silently reexecuting uncertain external effects.
6. Proposed worker memories/skills cannot commit without the orchestrator's policy decision.

## Tracker exception

Neither the chat workspace nor standalone Iron Web directory has Git metadata. This research therefore lives in the local Markdown tracker; no throwaway branch or push was possible. No remote issue, runtime change or account connection was created.
