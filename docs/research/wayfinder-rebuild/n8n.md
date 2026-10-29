# n8n workflow/editor reference: actual REA investigation

Research date: 27 October 2026. Purpose: improve Wayfinder's planned workflow and run UX without importing n8n's execution engine, scheduler, agent framework, credential system or integration catalogue. No n8n application, server, workflow or target JavaScript was executed.

## Published artifact and provenance

The official npm package metadata identifies `n8n-io/n8n` as its repository. The `n8n-editor-ui` **latest dist-tag was 2.16.2**, while published `n8n@2.45.4` explicitly depends on **`n8n-editor-ui@2.45.4`**. This investigation acquired that exact matching editor version instead of assuming the latest tag represented the current server's UI.

- [Exact editor metadata](https://registry.npmjs.org/n8n-editor-ui/2.45.4)
- [Published server dependency metadata](https://registry.npmjs.org/n8n/2.45.4)
- Distribution: `https://registry.npmjs.org/n8n-editor-ui/-/n8n-editor-ui-2.45.4.tgz`, 12,794,063 bytes, 649 archive members.
- SHA-256: `dc3e47f087550cea801d1ca94b9c39ca9e24d4691b9c95b042a19bc5e9ce514a`.
- The downloaded bytes matched the registry's published SHA-512 integrity value. This is package-integrity checking, not an independent verification of npm signature/attestation chains.
- Static extracted-directory identity reported by REA: `ecb40090dd98a9fc70daf3d89dd929e0b4d61aa2b2ead701be98a07c2ee5a514`.

Extraction checked destination containment and rejected links/non-file/non-directory members. It installed no dependencies and ran no package lifecycle scripts. Download, inventory, acquisition records and raw evidence remain in ignored `.local/rea-research/expansion/n8n/`.

## Actual REA operations

Used the already-built cloned REA 6.8.0 with the isolated Node 24.22.1 runtime. Its static analysis selected package metadata, HTML, executions list/preview, workflow history, JSON/table data views, test-run details and the node canvas chunk. Exact selected paths are preserved in `selected-sources.json`; command arguments and all stdout/stderr/exit/timing records are retained.

| Operation | Actual result | Evidence ID |
| --- | --- | --- |
| `analyze-javascript-application` with nine selected paths, 512 MiB worker heap, 18,000 retained semantic nodes overall / 4,000 per source, 90 s per-source deadline | Exit 0 in 96.62 s. Seven JS files parsed; 253,592 text bytes; 72,862 AST nodes visited; 749 structural findings; zero parse failures. Retained semantics/source coverage are partial. | `ev_4ad6cf3ec5aac821fa16ea46996bd5f6dd8dd43fdf5bed4bd6d07c7ac2a3661e` |
| `trace-javascript-semantics`, exact recovered retry function, callers / `calls` relations | Exit 0. One seed, one traversed function, no resolved caller relation, 362 relevant unknowns. This did not establish the complete UI-to-run path. | `ev_688905eb6435fe5099432c9e41f2a29f38c48959819defc4a51e93ca787a2119` |
| Narrowed `analyze-javascript-application` on package metadata and the 21,872-byte execution-preview chunk, 20,000-node total/per-file limits | Exit 0 in 29.17 s. No retention truncation in the focused semantic graph, but dynamic/unsupported relationships remain partial. This was a corrected narrow question, not an unchanged whole-app replay. | `ev_e0d0458137b71d51af89e49a2e949a65438b6416b770af976c69b3577d80f827` |
| Focused retry-function caller trace | Exit 0. One seed, one function, zero resolved caller relations, one relevant unknown. No full callback-to-backend execution flow is claimed. | `ev_aed626d5e1e165482112e949ad1ee537582d6ed71858ea5633f40008a5fcd58b` |

The first analysis leaves 365 relevant inventoried files outside selection; imports do not implicitly expand analysis scope. REA's zero Electron window/IPC counts are expected for a web editor and are not a security assessment. The exact retry seed is `jsrg_node_f8b677501a529476c674d0205e44f13d5336ebf4db12e34eb3606175aff6e899` in the first semantic graph. The focused graph must be queried using its own returned node identity, not a fabricated cross-graph ID.

## Recovered UX patterns and authority

The following interface explanations combine actual REA source/semantic observations with clearly labelled supplementary reads of the same shipped chunks. No browser interaction, backend request or provider effect was observed.

| Pattern in shipped editor code | Basis | Adaptation for Wayfinder |
| --- | --- | --- |
| Definition/history and execution instances are separate objects. | REA selected `WorkflowHistory-DG7DeVrq.js`, executions view/preview and `NodeView-DHFAd9m2.js`. Packaged code retains version IDs and separate preview/read-only state. | Store an immutable definition/version snapshot with every run. Editing a draft must not silently change an old run, receipt or approved payload. Show draft, version and run identity separately. |
| A run has its own action surface and lifecycle. | Executions preview emits distinct retry, stop and delete events; test-run detail maps running, done, failed and cancelled states. These are source-derived UI candidates, not proof cancellation stops a provider. | Reuse Wayfinder's current result/cancel/reconcile handlers, with honest stopping, completed, failed and uncertain states. Never equate a green canvas with a verified external effect. |
| Node/run data has structured inspection views. | Shipped JSON/table chunks and preview use execution data separately from editor configuration. | Provide step inputs, bounded outputs, provenance, warnings and errors beside the workflow, with advanced raw evidence behind Details. Show unknown cost/tokens as unknown. |
| Historical execution and current draft can diverge. | Executions/history chunks include workflow version fields and distinct current/original-version retry labels. | Display the version and data each new attempt will use. Wayfinder must not copy generic effect replay: only explicitly eligible read steps can retry, using fresh scopes; uncertain effects require reconciliation. |
| Sensitive execution data has a redaction state. | Packaged preview checks `redactionInfo`, `isRedacted` and `canReveal`. REA does not prove backend enforcement. | Return already-redacted evidence from trusted Wayfinder services. No secret may be sent to React and merely hidden by CSS or a collapsed panel. Any reveal feature requires an actual scoped handler; otherwise do not offer it. |
| The canvas distinguishes read-only execution preview from editing. | Packaged NodeView and preview properties express read-only/production-preview modes. Exact visual appearance was not observed. | Begin with a reliable ordered-step/recipe view over qualified operations; add an editable graph only after the trusted workflow contract supports it. Avoid a decorative canvas whose controls have no backend behavior. |

The official [execution documentation](https://docs.n8n.io/build/understand-workflows/understand-executions/view-all-executions.md) distinguishes original/current-version retries and warns that a failed node can repeat already handled items. Its [execution-mode documentation](https://docs.n8n.io/build/understand-workflows/understand-executions/types-of-executions.md) distinguishes manual, partial and production execution and pinned test data. Its [debugging guide](https://docs.n8n.io/build/understand-workflows/understand-executions/debug-executions.md) describes loading historical data for inspection/re-run. These documented concepts support explicit test/live modes, not permission to execute Wayfinder effects without approval.

## Atomic implementation suggestions for the parent plan

1. **Workflow contract first:** versioned definition, scoped input references, supported worker/tool binding, dependency validation, constraints and immutable run identity. Test invalid IDs/types, cycles, unavailable bindings and cross-space references before enabling a builder.
2. **Read-only recipe runner:** connect existing Hermes execution and trusted workflow services. Test real selected-file/memory recipes with synthetic data, dependency ordering, cancellation, restart and duplicate submission. Do not create a second agent loop.
3. **Run inspector:** expose step state, bounded inputs/outputs, source evidence and actionable errors. Test truncated/empty/denied responses and late results after a space change.
4. **Test/live distinction:** labelled synthetic fixtures and saved observations cannot become live provider results or effects. Test that test data cannot mint grants or approval receipts.
5. **Version-aware recovery:** immutable prior results, explicit fresh read attempt, retry lineage and safe reconciliation for uncertain effects. Test changed definitions/payloads, stale grants and duplicate delivery before enabling recovery UI.
6. **Qualified editing last:** list/step editor first, graph interaction only where supported; saving/publishing must be distinct from running. Test unsaved changes, invalid connections and keyboard-only navigation. Preserve audit evidence when a definition is removed rather than copying a reference's deletion semantics.

Keep Wayfinder's existing Hermes runtime, Atlas selection, Iron Web gateway, owned process bridge and final-handler authorization. The patterns above justify UI and interface improvements, not adopting n8n's engine, credential store, recurrence system, integrations or arbitrary code nodes.

## Remaining limits

Neither analysis recovered a complete caller path from the Vue callback into a backend operation. The focused pass narrowed uncertainty but did not erase it. Most package files, backend handlers, permissions enforcement, credentials, actual rendering, accessibility, running workflows and external effects were not tested. The inspector/editor recommendations remain proposed Wayfinder work that requires its own phase tests.
