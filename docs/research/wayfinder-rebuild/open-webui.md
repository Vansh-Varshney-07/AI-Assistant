# Open WebUI: chatbot and onboarding reference through actual REA

Research date: 27 October 2026. This is planning evidence. Open WebUI was not installed or run; its Python modules and JavaScript bundles were never imported or executed. No browser, desktop, account or model request was used.

## Target and provenance

Official PyPI metadata at [open-webui](https://pypi.org/project/open-webui/) identified version **0.12.4** and the wheel `open_webui-0.12.4-py3-none-any.whl`, 106,366,595 bytes. Downloaded SHA-256 matched the published value:

`02e9caba96234db3fa17a92e56163b3f7f2b8ca8227fa886b85c178d696483f6`

The wheel contains 6,013 members. Checked ZIP extraction selected 867 frontend text artifacts (JavaScript, JSON, HTML and CSS). This extraction preserves original member bytes and records source-member paths, SHA-256 and sizes in a derivation manifest. It is not an installation or a complete extraction of every wheel resource.

REA identified the extracted frontend-text directory as:

`9f2a837e86deae7af6cd7a2ba1287b8c2e0a411c9c68a52bc02973b3286d2cc3`

That directory identity is separate from the wheel identity.

## Actual REA operations

The locally built REA 6.8.0 CLI ran under the existing private Node 24.22.1 toolchain. The exact command is retained in `.local/rea-research/expansion/open-webui/command.json` and has this form:

```text
node rea/scripts/rea.mjs analyze-javascript-application <extracted frontend>
  --source-paths-json <selection.json> --max-heap-mb 512
  --max-semantic-nodes 12000 --max-semantic-nodes-per-file 4000
  --analysis-timeout-ms 60000 --format json --full-output
```

Six exact compiled sources were selected in this order: application entry; onboarding/auth route; completion API wrapper; task API wrapper; file preview component; and the 1,045,416-byte chat bundle. Their actual names are preserved in `selection.json`, rather than inferred from screenshots.

The invocation returned **exit 1 / provider_timeout** after 142.812 seconds overall. It reached the declared 60-second per-source deadline on the final large chat bundle. Five JavaScript files completed, one was skipped/incomplete, and there were zero parse failures. REA retained 3,675 structural findings and explicitly left 831 relevant files outside the caller-selected scope.

Authenticated partial analysis Evidence:

`ev_784d231960606b4d0c7a0c225c69d459c2c1cbc946b1d6c4c7f98c0c10ec7757`

The failed analysis was not replayed unchanged. Its complete error, partial Evidence, source selection and coverage were preserved. The graph also reached retained semantic-node limits; completion of a source's structural analysis does not imply complete semantic recovery.

A real `trace-javascript-semantics` query then reused this saved Evidence, selecting the `onboarding` property with forward influence. It exited zero and produced:

`ev_9641a19621bc2cbec940ba957ef6ed3c750fab1d9bcc54c4a73f59ba387bd90d`

The trace found seven property-slot seeds in six functions and one module, but zero retained traversed relations and 8,923 relevant unknowns. **It does not establish a complete onboarding control/data flow.** The successful query delivery must not be mistaken for successful full-flow reconstruction.

## Findings, evidence tier and Wayfinder implications

| Finding | Authority and limit | Apply to Wayfinder |
| --- | --- | --- |
| Completion requests have their own AbortController; task stopping is a separate POST operation keyed by task ID. | Inert packaged-code inspection corroborates completed REA analysis of `_app/immutable/chunks/DSkNELZd.js` and `FM7wIn-x.js`. Actual network effects and upstream cancellation were not observed. | Separate UI stop requested, server cancellation acknowledgement and final outcome. Reuse Wayfinder request/turn/run IDs; never equate aborting a client request with a verified stopped effect or zero billing. |
| API wrappers normalize errors and distinguish failed responses from successful JSON. | Packaged compiled wrappers contain explicit error extraction, `response.ok` checks and throwing paths. The backend was not executed. | Preserve meaningful provider/runtime/scope errors and partial results; do not replace failure with an empty answer or green completion. Offer a safe explicit next step. |
| First-run configuration changes the welcome/auth path and the main call to action. | Completed packaged onboarding route `_app/immutable/nodes/53.1SYwzS3k.js` checks configuration and `onboarding`; its button changes between account states. The REA semantic trace retains major unknowns. | Use a clear welcome followed by small dependency/model/space/consent steps, driven by actual Wayfinder checks. Do not copy Open WebUI's admin-account/signup/OAuth system. |
| The compiled chat has separate submit, stop, generation, task-ID and auto-scroll state/props. | Source-derived inspection of the large packaged chat chunk. This file's REA analysis did not finish, so its complete lifecycle is not claimed. | Preserve draft text on failure, visible stop state and stable scrolling; avoid replacing the entire conversation view on each progress update. Implement using Wayfinder's actual supported event/status interface. |
| Attach/search controls use permissions and model-capability conditions. | Packaged source includes `permissions.chat.file_upload`, model `capabilities`, and feature conditions; full chat-bundle semantic recovery is incomplete. This is not server-enforcement proof. | Use a shared availability matrix so unavailable actions are hidden or explained. Keep final permission/resource checks in Wayfinder's service; disabling a button is not authority enforcement. |
| Rich response presentation and response auto-scroll are product features. | [Official chat documentation](https://docs.openwebui.com/features/chat-conversations/chat-features/) describes code blocks, structured answers and auto-scroll preferences. This is documentation evidence, not a completed REA inspection of Markdown/citation rendering. | Add readable, safely rendered Markdown/code/tables and a jump-to-latest affordance where supported. Treat every source citation as requiring a real scoped evidence reference. No executable HTML, remote scripts or invented source badges. |

Official [quick-start documentation](https://docs.openwebui.com/getting-started/quick-start/) describes connecting a provider and beginning a conversation. Its runtime, storage, user administration, plugin system, model catalogue and deployment method are not proposed for Wayfinder. The reference is a set of interaction patterns, not an engine or dependency to adopt.

## Atomic implementation and test ideas

These are proposed Wayfinder changes/tests, not changes executed in this investigation:

1. Centralize the state labels for chat reservation/running/stopping/completed/interrupted/error; verify each maps to an actual service state and never invents a percentage.
2. Preserve a draft on failed send; test a delayed acknowledgement and reconnect against the original request ID with no duplicate dispatch.
3. Add safe Markdown/code/table presentation using an appropriate maintained renderer; test malicious HTML, dangerous URL protocols, long code blocks and source links that do not resolve to authorized evidence.
4. Keep “follow latest” separate from the user's scrolled position; test new output while reading older content and reduced-motion behavior.
5. Split onboarding into welcome, actual dependency checks, approved-model verification, space creation and explicit disclosure consent; test unavailable Docker/Hermes, partial setup, restart/resume and changed model identity.
6. Compute allowed controls from actual per-operation availability; test a present connector with an unavailable agent route, an expired capability check, and a forged UI invocation rejected by the final handler.

Keep Wayfinder's Hermes runtime, Iron Web, authenticated owned bridge, encrypted credential vault and exact-action service. Do not import browser-localStorage token patterns, arbitrary model/provider selection, multi-model fanout, voice, terminal execution, image generation, or an automatic knowledge-sync framework from Open WebUI.

## Remaining limits and retained material

No visual/layout/accessibility test, live chat request, account connection, stream cancellation or provider effect was performed. The large compiled chat source remains partially analyzed, and the onboarding semantic trace does not prove a full path. Source-derived and documented behavior stays labelled separately from actual REA observations.

The acquisition, extraction manifest, selected source list, complete original analysis/error/stdout/stderr, execution records, partial Evidence, packaged-code locations, trace request/result and compact index remain under ignored `.local/rea-research/expansion/open-webui/`. No Wayfinder application code or global tool configuration changed.
