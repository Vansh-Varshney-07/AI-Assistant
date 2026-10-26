# Proposed contract amendments before R1 implementation

This is a review recommendation, not an applied backend/API/schema change. It closes specific ambiguities found by the stress review. Stable interface names are to be versioned by the existing service owner; worker-owned prompt/result contracts remain separate.

## 1. Runtime and data ownership

- Persist a stable runtime identity and app-data root independent of executable location, portable-app moves and renderer windows. Do not generate a new production data root at every launch.
- A descriptor identifies runtime ID, instance generation, API/schema versions, process identity/start time, transport, and whether this app owns the service lifecycle. It contains no renderer-accessible bearer secret.
- A new owned child passes credentials through a trusted host-only bootstrap channel such as an inherited pipe. Attaching to an existing runtime requires an explicitly paired credential and proof of the intended service; a responding port is insufficient.
- Only one process owns a selected Qdrant/journal/application runtime. Electron windows use it as clients. Handle a simultaneous second launch by authenticated attach/focus or an explicit owner error, not an empty replacement database.
- Separate closing a view, disconnecting the UI, cancelling Wayfinder work, stopping an owned service and stopping a shared Hermes runtime. Default Quit must not kill unrelated shared work. R5 background authorization is a later explicit contract.
- Negotiate API/schema compatibility before enabling writes. Unsupported versions open a clear recovery view, not a best-effort writer. Schema migration ownership and recovery begin in R1.

## 2. Canonical chat and request acceptance

- Application conversation records are the authoritative display transcript. Define whether/how a bounded selected history is sent to Hermes and whether a compatible Hermes session is used; never silently combine two independent histories.
- R1 chat has no inherited broad toolsets, implicit global memory, secret/plugin configuration or arbitrary session search. Existing managed-provider credentials stay in their trusted runtime. R2 adds only the scoped gateway evidence flow.
- A start command binds a client request ID and canonical payload hash to server-authenticated owner, space, conversation, task, provider/model policy, input and artifact references. The renderer cannot assert owner identity or mint permission.
- Acknowledge acceptance only after the user message and run/attempt identity are committed together. Before calling Hermes, commit the dispatch reservation. Crash after reservation produces interrupted/unconfirmed state rather than an automatic second dispatch.
- Identical command delivery returns the same attempt; changed immutable input under that ID is rejected. An explicit permitted chat retry has a new attempt ID, reference to its predecessor and a fresh read scope/budget. It never inherits a previous action approval.
- Local “Sending” UI feedback is not the server's durable acceptance receipt. Make the distinction observable after a timeout or restart.

## 3. Events, reconnect and cancellation

Proposed envelope fields: contract version, runtime ID/instance generation, run ID, attempt ID, conversation ID, space/task binding, sequence, event type and bounded payload. Treat IDs as opaque strings and large counters as decimal strings rather than JavaScript Numbers. Host authentication supplies owner authority.

- Persist enough terminal state/snapshot information to recover the actual run. Define bounded retention for deltas; expired cursors return a snapshot/resume position rather than an endless empty stream.
- Deduplicate by event identity and apply only permitted transitions. Bounded out-of-order buffering requests a snapshot when a gap cannot be repaired. A duplicate final does not append another assistant message.
- Route events by their immutable run/conversation/space, never the currently selected view. Late old-window responses must not replace new-window state.
- Distinguish queued/running/stop-requested/completed/cancelled/failed/interrupted. A user click alone is not upstream cancellation confirmation. Once cancellation is authoritative, late completion cannot resurrect the attempt.
- If provider work cannot be interrupted, explain that delivery stopped while upstream completion/cost may still occur. Do not immediately release all budget/concurrency accounting on a purely local stop signal.
- Reconnect and automatic query retries observe state. They do not resend start/action commands under a fresh identity.

## 4. Rendering and disclosure

- Render sanitized Markdown without active model-supplied HTML/scripts. Explicit policy governs remote images, external links, attachments, Mermaid/SVG and downloaded artifacts.
- Resolve citations through backend-issued scoped source references. Opening a link does not become a generic file/URL/shell bridge. Display historical/unavailable/changed-source states and request a fresh permitted grant where required.
- Preload exposes a small per-operation API; main validates sender/frame and schema; final Python handlers validate authority and resources. Renderer gets neither bearer tokens nor generic authenticated HTTP/IPC forwarding.
- Approval cards are backed by actual trusted proposal records, not model-rendered buttons or text. Exact target, parameters, scope, account identity and expiry must be readable; edited proposals need a new review.
- Explain selected provider disclosure at setup and enforce allowed data classes at each request. Local-file read permission does not silently permit an outbound upload to a different model/provider.

## 5. First-release manifest and acceptance

Pin a manifest for R1: Chat, basic Runs, Settings, actual text inference, ordinary transcript persistence, supported cancellation semantics and startup/recovery states. Files/memory/Google/tasks/review actions are absent until their defined release, including inspector content and shortcuts.

Add the affected cases from [SUPPLEMENTAL-CASES.csv](SUPPLEMENTAL-CASES.csv) to mandatory R1 acceptance. Correct preview phase gating, navigation drawer, inspector toggle, IME handling and focus visibility before treating it as an interaction reference.

Required launch evidence includes the actual selected host/runtime version matrix and a packaged Windows app, not a Vite development screenshot. Do not automatically upgrade Hermes, Node or system services merely because a moving upstream branch uses newer tooling. Scope any upgrade as a separate reviewed compatibility change.

The broad release ladder remains useful. These contracts narrow its first implementation rather than adding more features to R1.
