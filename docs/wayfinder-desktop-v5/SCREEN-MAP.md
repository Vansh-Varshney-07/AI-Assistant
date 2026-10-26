# New interface → existing features → release gates

Proposed mapping. `workbench/index.html`, `app.js`, `style.css` and the Stitch reference screens at the frozen GitHub commit are the visual source. Existing `desktop-app` forms/bridge are functional reuse candidates, not permission to retain an unrelated presentation. The production client is one Electron/React application over the authenticated service, not an iframe around the workbench server.

## Screen map

| GitHub screen / control | Integrated behavior | Existing service / missing adapter | Inclusion and failure behavior |
|---|---|---|---|
| Brand/sidebar/title bar | Preserve grouped visual hierarchy, active route and local app identity. Actual minimize/maximize/close are host intents. | Existing Electron host; typed window intents if absent. | Every milestone. No fake host/admin/version identity or decorative close button. |
| Command portal | Owned space selector, runtime component state, current feature context and command palette. | AppService spaces; host runtime descriptor; service-backed manifest. | No arbitrary command/shell palette. Unknown route/version denied. |
| Home prompt | Ordinary bounded chat with provider/model disclosure, actual attempts and stop/recovery. | Missing canonical chat admission/history/events around existing Hermes execution. | R1 only after live chat qualification. Never default to `store` or W35. I1 explains unavailable chat rather than echoing. |
| Home summary cards | Real counts of permitted current runs, reviews and selected sources with observation times. | Existing scoped snapshot/read facades, hardened with service-owned pagination. | I1 for included functions; no static 8-connected-services or sample task metrics. |
| Today/planner | Selected read-only calendar range, Google task projections and visibly separate local task list. | Existing Google fixed read adapters; missing account-generation/projection/WorkItem facades. | R3. No fake daily schedule, automatic optimization execution or two-way sync. |
| Notion workspace | Preserve as a design reference; omit production nav or show an explicit deferred connection description in Advanced catalogue. | Existing Notion metadata/adapter alone is not this app's qualified account/disclosure path. | Deferred from core; no live Notion editor, write, iframe or imported token by implication. |
| Workflow canvas | Reuse card/step/timeline visual language for a bounded linear list; show typed inputs, versions and budget. | Existing fixed read workflow and WorkerHub; missing versioned template/root authority adapter. | I1 shows only actual fixed recipe runs. R4 allows ≤6 linear steps; no arbitrary DAG import or run-all button. |
| Activity/worker monitor | Actual run/step/attempt timeline; definition catalogue separate from live jobs. Human-readable role and evidence details. | Existing worker/workflow/action records; upstream definitions; versioned inventory facade. | I1 actual completed functions. R6 configuration controls only after qualification. Role count is not running-agent count. |
| Connections | Distinct configured/authenticated/qualified/authorized/healthy states; selected account and resources, last observation and safe setup/recovery. | Existing runtime/Google setup status; missing stable account/generation and product projection lifecycle. | R3 reads after consent/test. No static green cards for GitHub/Notion/Google/NVIDIA based on metadata. |
| Permissions/security | Exact scoped proposals, trusted review request, revoke/expiry, receipts and read-only reconciliation; readable policy descriptions tied to actual operation support. | Existing MemoryControl/ActionGate/Git connector/audits; upstream ApprovalService stays non-authoritative for production effects. | I1 included paths. No generic policy toggle that broadens tools or approves a worker. |
| Memory/knowledge | Owned source inventory, current/historical scoped recall, conflict/unknown status, explicit change events and evidence inspector. | Existing AppService/Iron Web/ContextGateway/MemoryControl. Full forget/restore barrier remains missing. | I1 labels only completed events. Core R2 requires privacy-complete forget and neural evidence. No default auto-store/chat-as-memory. |
| Selected documents | Explicit trusted picker, scope/expiry/revoke, supported extraction, W35 analysis and fixed memory comparison. | Existing FileBroker, WorkerHub, HermesBridge and fixed PlatformService recipe. | I1 one qualified UTF-8 source ≤2 MiB; new formats/multi-file require separate qualification. |
| Runs and reviews | Durable status, historical answer, provenance, stop, original-attempt checking, supported explicit read retry and separate artifact clearing. | Existing workflow/evaluation/audit and action APIs; new chat lifecycle under C03/C04. | Real statuses only. Clearing is not forgetting facts or undoing effects. No Retry for uncertain writes. |
| Local Git / Projects | Preserve separately declared branch review; later qualified bounded repository reads/draft review. | Existing exact branch connector; missing safe status/diff adapter. | Existing branch module is optional. R7 core is read-only and must be independently qualified. No commit/push/merge/hook/test execution from UI. |
| Skills/roles | Show actual definitions, aliases, effective tools, schemas, installed binding/version, evidence, dependencies and disabled reasons. | Atlas, upstream 16 definitions plus local infrastructure; missing full binding publish/rollback integration. | Read-only catalogue first; R6 edits are versioned/reviewed. Unknown ID stays unresolved. |
| Settings | Actual component health, selected runtime/data root, compatible model profiles, reading size/theme, explicitly supported privacy/retention/recovery settings. | Existing settings/status; missing typed health/lifecycle facades where observed. | No arbitrary executable/path/model configuration from renderer; no automatic service install/reset. |
| Telemetry strip | Measured run latency/dispatch counts and available component health, each stamped. | Existing workflow metrics; host-measured UI performance if added. | Unknown tokens/cost/CPU/RAM display Unknown/Not measured. Remove random simulation. |
| Quick search | Keyboard-accessible route and permitted record search from the same inclusion manifest. | Named app intents and scoped search/read interfaces. | A source result cannot be an executable deep link or implicit privileged intent. |
| Quick chat/summon | Future shared-runtime text view with opt-in hotkey and one composing lease. | Missing shared-window/draft/notification lifecycle. | R5 after C19. Replace current fake summon with deferred explanation; no pet agent. |
| Pet/widget | Retain design artefact only. | No core dependency. | Deferred. No screen monitoring, clipboard reads, native action or always-on-top activation. |
| Activity/fitness CSV | Preserve existing diagnostic data adapter if explicitly included in the internal parity variant; no live fitness card. | Existing canonical local CSV read. | Fitness remains deferred; a CSV fixture does not qualify a vendor connection. |

## Functional paths to preserve during the visual port

| Function group | Existing named intents / APIs | Port acceptance |
|---|---|---|
| Spaces | list/create owned spaces; authenticated source/recall | Switching clears invalid current state and does not reroute late results. |
| Memory changes | preview/propose/result/decide/revoke/reconcile/audit through main-owned review | Same exact digest/scope/expiry; no renderer approval shortcut. |
| Local files | trusted picker, grant/search/revoke, W35 start/result/cancel/forget | Preserve revoke access and actual evidence even when navigation changes. |
| Fixed comparison | context → existing W35 → freshness/hash/runtime validation | No second model/agent loop; stale result withheld. |
| Run inspection | scoped snapshot, actual jobs, audit, artifact checks, bounded explicit read retry | Preserve original linked attempt and unknown outcome; no hidden effect replay. |
| Local branch module | selected ordinary repo, exact branch/ref/HEAD, proposal/review/receipt/reconciliation | No new Git command surface; existing final handler remains authoritative. |
| Capabilities | installed runtime inspection and Atlas candidates | Discovery stays non-executable and fixture/live states remain distinct. |
| Settings | existing persisted reading size and conservative connection state | Theme/font controls alter presentation only, never authority. |

## UI states, not invented success

For each destination specify initial loading, no configured resource, genuinely empty result, operation unavailable, denied, stale, partial, offline, executing, terminal success, failure and uncertainty. Status is text plus icon, never color alone. Keep recovery actions scoped and operation-specific.

Connection loss keeps permitted historical data visibly stale. It cannot create a default memory space, substitute an account, display a fabricated assistant reply or seed demo records. A missing worker definition is not resolved with a frontend hardcoded worker. A supplied definition is not an installed executable binding.

## Design and interaction acceptance

Map each reference screen to components/tokens and a rendered comparison at the required viewport sizes/themes. Check actual content lengths, long filenames, 47-role inventory and a dense timeline without forcing unreadably small typography. Run keyboard/IME/focus checks on the actual rendered view, then packaged Windows checks for Electron frame controls/native review dialogs. These are future acceptance tasks; no UI test is being run by producing this map.
