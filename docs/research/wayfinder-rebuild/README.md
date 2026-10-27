# Research for the complete Wayfinder rebuild plan

Date: 27 October 2026. Planning evidence only. No Wayfinder product code or executable changed.

## Why these additional references

The [earlier six-product REA pass](../desktop-reference-rea/README.md) already investigated desktop interaction, personal context, memory visibility, agent workspaces and permission controls. Repeating those analyses would not resolve the main remaining gaps: usable chatbot/onboarding flows and workflow execution/debugging UI.

This pass therefore selected two focused references. Neither needs to contain every Wayfinder feature. Their published artifacts were downloaded and inspected with the actual locally built REA CLI, while their documentation establishes separately labelled product claims.

| Reference | Feature questions | Actual artifact and analysis outcome |
| --- | --- | --- |
| [Open WebUI](open-webui.md) | How are first-run setup, model readiness, composer controls, API errors, generation and cancellation represented? | Official PyPI 0.12.4 wheel, published SHA-256 verified. Actual REA parsed five selected compiled JS files before the final large chat bundle hit its 60 s per-source deadline. Authenticated partial Evidence retained; the onboarding query returned seven seeds but no resolved traversed relations. |
| [n8n editor](n8n.md) | How are workflow definitions, immutable versions, runs, node data, test modes, redaction and retry choices separated? | Matching official `n8n-editor-ui@2.45.4` npm artifact, published SHA-512 integrity verified. Two actual selected REA analyses completed, plus two caller queries. Both queries found the selected function but did not resolve its complete caller path. |

No Open WebUI/n8n application, server, workflow or target code was executed. There was no browser/desktop capture, account connection or native UI automation. REA and its owned static analysis workers executed; raw source targets did not. No global MCP, model or product configuration changed.

## Provenance and exact evidence

Open WebUI wheel SHA-256:

`02e9caba96234db3fa17a92e56163b3f7f2b8ca8227fa886b85c178d696483f6`

Its analysis retained partial Evidence `ev_784d231960606b4d0c7a0c225c69d459c2c1cbc946b1d6c4c7f98c0c10ec7757`. The onboarding query produced `ev_9641a19621bc2cbec940ba957ef6ed3c750fab1d9bcc54c4a73f59ba387bd90d`; successful query delivery is not a complete flow reconstruction.

n8n editor package SHA-256:

`dc3e47f087550cea801d1ca94b9c39ca9e24d4691b9c95b042a19bc5e9ce514a`

Broad analysis Evidence: `ev_4ad6cf3ec5aac821fa16ea46996bd5f6dd8dd43fdf5bed4bd6d07c7ac2a3661e`. Narrow execution-preview analysis: `ev_e0d0458137b71d51af89e49a2e949a65438b6416b770af976c69b3577d80f827`. Static/semantic source and retention limits remain explicit.

The n8n editor's npm `latest` tag was stale relative to the published server dependency. The investigation selected the server's exact matching editor dependency instead of treating the tag as proof of compatibility.

The compact [execution index](execution-index.json) preserves the researchers' actual command/result metadata. Full downloaded artifacts, derivation manifests, selections, stdout/stderr, errors, exit records and Evidence remain in ignored `.local/rea-research/expansion/`. REA version 6.8.0 was built from the existing ignored clone and used with the private Node 24.22.1 toolchain.

## Findings applied to the plan

1. **First run is a real state machine.** Use actual dependency/model/space/consent checks with resumable progress. Do not copy Open WebUI's user-administration or arbitrary provider system into Wayfinder.
2. **Cancellation has multiple boundaries.** Client abort, server stop request and final observed outcome are different states. Reuse Wayfinder's existing request/turn/run identities; do not turn a stopped spinner into a completion claim.
3. **Controls follow real capability.** Show only supported operation variants, explain unavailable ones and enforce permissions again in the final handler. A hidden or disabled button is not security enforcement.
4. **Workflow versions and runs differ.** Definition editing, synthetic testing, execution and historical inspection need separate service identities and UI states.
5. **Inspect data without expanding authority.** Bounded node inputs/outputs, provenance and redaction are useful. Revealing sensitive data or retrying an operation still needs the applicable service permission.
6. **Do not copy generic retry semantics.** A partially failed node may already have produced an effect. Wayfinder must reconcile uncertain outcomes and bind a fresh approved attempt when required.
7. **Use reference patterns through existing systems.** Hermes executes roles/tools, Iron Web owns memory, Atlas supplies discovery candidates and trusted Wayfinder services own scopes/approvals/auditing. No n8n/Open WebUI engine, scheduler, store, tool catalogue or credential mechanism is adopted.

The previous Handrail/Keel/Hearth package findings still apply: no plaintext credential fallback, no credential-bearing renderer settings and no Enter-to-approve or truncated exact review. Native CLAI UI and large minified reference paths remain unresolved where reported. Nothing in this research certifies future Wayfinder behavior.

## Project audit and visual references

The fresh [47-role audit](agent-readiness.md) and [readiness JSON](agent-readiness.json) distinguish definitions, deterministic service responsibilities, task adapters and qualified execution. All 16 dedicated definitions are merged, but only A01/A05/A06 currently have selected-file execution variants. A07 links the Memory UI and all six app presets remain unavailable. Manual provider reads are not autonomous agent bindings.

For icon/asset design, consult [Lucide React](https://lucide.dev/guide/react/), [icon accessibility](https://lucide.dev/how-to/accessibility) and the applicable [stock-image terms](https://unsplash.com/license) when selecting an image. Existing Lucide components and local fonts are reusable. Proposed original SVG illustrations and any selected stock artwork need provenance and local packaging; no reference product artwork is copied. These are documentation/design references, not additional REA analyses.

Other primary documentation reviewed: [Open WebUI setup](https://docs.openwebui.com/getting-started/quick-start/), [chat features](https://docs.openwebui.com/features/chat-conversations/chat-features/), [n8n execution modes](https://docs.n8n.io/build/understand-workflows/understand-executions/types-of-executions.md), [run history](https://docs.n8n.io/build/understand-workflows/understand-executions/view-all-executions.md), and installed-version-sensitive [Hermes delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation) and [scheduling](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron). No new runtime compatibility claim is made from online documentation alone.

## Deliverables

The implementation-facing result is the [master rebuild plan](../../platform/WAYFINDER-REBUILD-PLAN.md), [95-task atomic backlog](../../platform/WAYFINDER-REBUILD-TASKS.csv) and [phase test specification](../../platform/WAYFINDER-REBUILD-TESTS.md). Product implementation is not started; all backlog rows remain not started or conditional. The final user checkpoint is a versioned, verified EXE, with native/provider dependencies stated honestly.
