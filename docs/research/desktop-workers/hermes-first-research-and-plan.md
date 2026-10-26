# W33–W37: Hermes-first research and proposed implementation

Research date: 2026-10-25, Asia/Calcutta. Status: proposed; no workers or desktop permissions enabled by this research.

**Decision:** retain five logical worker identities, use Hermes for reasoning and worker lifecycle, reuse existing tools and parsers, and add only the application integration needed to enforce authorized inputs and actions. Do not create a second agent framework or five continuously running agents.

The latest user request introduces explicitly shared screenshot analysis. It supersedes the older `docs/personal-ai-companion/PLAN.md` exclusion of all screen capture for this proposed scope. It does not introduce background desktop monitoring.

## Evidence and limits

Read-only live inspection confirmed the `ai-assistant` sandbox is Ready, Hermes Agent reports version 0.21.3 and running, OpenShell is 0.0.116, and the selected route is `nvidia/nemotron-3.5-lightning-30b-a3b` through `nvidia-prod`. The status output explicitly said the upstream model invocation was not probed and the serving process was not checked in that field; its final agent status reported running. This research made no inference request.

A read-only AST inspection of installed `/opt/hermes` source found registered `delegate_task`, `read_file`, `search_files`, `vision_analyze`, and `computer_use` tools. The file toolset also includes `write_file` and `patch`; enabling that whole toolset does not establish a read-only worker. Computer-use schema includes capture, window listing and input actions. Source availability establishes neither tool enablement nor functioning dependencies. Source hashes are recorded in [runtime-evidence.json](runtime-evidence.json); the installed Git revision could not be recovered.

The installed delegation resolver inherits parent tools and has MCP-inheritance handling. Its child construction skips the normal memory preload. That is useful context reduction, but does not demonstrate filesystem, network, transcript or memory-service isolation. A trusted application must verify each worker's effective capabilities.

The project currently has:

- An implemented Windows companion and authenticated memory service, described in [the phase 0–2 architecture](../../wayfinder-phase-0-2/ARCHITECTURE.md). That architecture explicitly defers Hermes integration and worker isolation.
- Atlas discovery metadata in `wayfinder/atlas/registry/`. `file_discovery_worker` already exists; `document_analyst` already overlaps W35. Reuse and specialize those definitions rather than introducing duplicate workers with the same responsibility.
- A candidate flag in `wayfinder/atlas/indexing/retrieval.py` whose `is_executable` property checks only registry status. It must not be used as authorization.
- Memory-specific immutable proposals, digests and receipts in `wayfinder/service.py`. These are a reusable design pattern, not an existing desktop approval implementation.
- Newly merged Python dependency pins `hermes==0.10.0`, `nemoclaw==0.0.0a1`, and `openshell==0.1.5`. These differ from the managed operational installation. Package identity, distribution channel and compatibility must be verified before using those pins; a similar package name does not establish product identity. No dependencies were installed during this research.

## What Hermes already supplies

[Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation) provides fresh task conversations, child lifecycle and result delivery. Its model-facing interface does not provide arbitrary per-child tool selection. Completed-result persistence does not resume an interrupted child after a crash. Use bounded, on-demand runs and verify outcomes independently.

[Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) provide separate configuration, state and identity. They can help organize workers but do not create an OS security boundary. Avoid cloning the main assistant's credentials or memories into workers.

[Vision input](https://hermes-agent.nousresearch.com/docs/user-guide/features/vision) supports supplied images. The current model/provider path still needs a synthetic-image grounding test or an explicitly selected auxiliary vision route. Attached images can be saved under Hermes's home, so retention must cover Hermes copies and transcripts as well as UI attachments.

[Document extraction](https://hermes-agent.nousresearch.com/docs/user-guide/features/document-extraction) already supports several document formats through `read_file`, with optional converters for others. Test the installed parser and dependency paths on fixtures. Declare supported formats and truncation explicitly; prevent unreviewed lazy dependency installation in the worker lane.

[Computer use](https://hermes-agent.nousresearch.com/docs/user-guide/features/computer-use) supplies an existing desktop driver integration. Its target follows the bot's runtime/display placement, not the machine displaying a remote UI. The current Ubuntu/OpenShell placement therefore does not establish access to the Windows desktop. Evaluate and reuse the existing driver before considering any new automation backend.

[Hermes MCP integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) supports existing tool servers and explicit tool inclusion. The [reference filesystem server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) supports allowed directory roots and search/read operations, but also exposes mutations. Evaluate a pinned, read-only filtered deployment with OS-enforced read access before writing a custom filesystem implementation. Client tool filtering alone is insufficient when another path can reach the server's mutation tools.

[Hermes pets](https://hermes-agent.nousresearch.com/docs/user-guide/features/pets) already provide cosmetic sprites driven by activity and approval states. Evaluate Hermes Desktop's presentation against the intended floating Windows animal, quick chat, approvals and Iron Web controls. Reuse suitable assets/state integration where licensing permits. This does not prove its existing UI satisfies the complete Wayfinder UX. A [Desktop Plugin SDK](https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk) is another reuse option to evaluate before rebuilding UI features.

## Worker contracts

| ID and role | Hermes reuse | Input and output | Capability boundary |
|---|---|---|---|
| W33 Desktop Context Analyst | Image-aware Hermes job; use the existing vision route when verified | Explicitly shared crop plus question → observations, uncertainty and image-region references | Supplied image only; no independent capture, clipboard reading or window enumeration |
| W34 File Discovery Worker | Reuse current role; existing scoped search tool or reference filesystem MCP | Authorized directory grant and query → bounded metadata/file references | Search/list/metadata within approved roots; do not read every matching document |
| W35 Local File Analyst | Restricted variant of current document analyst; existing extraction | Authorized file reference/version or supplied extracted content → source-linked summary and parser warnings | Read selected artifacts; no default web, broad memory, writes or arbitrary execution |
| W36 Desktop Action Planner | Hermes reasoning with schema-validated output | Request, selected observations and allowed action schemas → reviewable bounded plan | No action execution; uncertain target or missing context returns a clarification request through the controller |
| W37 Desktop Action Worker | Existing Hermes computer-use integration/driver behind the authoritative gate | Approved immutable plan plus scoped observation permission → action receipts and verified outcome | Only the approved task, app/window, actions, payload and lifetime; no raw alternate route around the gate |

The worker IDs are routing and audit identities. W34 often needs deterministic search rather than another model call; W37 should have little discretion once its action sequence is approved. A simple file question need not activate all five roles.

## Red-council review

Three independent reviewers examined reuse/minimality, Windows/privacy boundaries, and reliability/UX. This is an adversarial design review, not a claim of empirical certification or separate model diversity.

| Objection | Resolution adopted | Remaining proof |
|---|---|---|
| Five prompts can inherit the same powerful tools | Preserve five contracts; run only needed Hermes jobs and verify effective tool exposure | Negative tests against terminal, code execution, MCP, browser and delegation bypasses |
| A sandbox desktop is not the Windows desktop | Treat the Windows transport/driver connection as an explicit integration boundary | Harmless fixture workflow in the intended Windows session |
| A screenshot analyst can become a screen scraper | W33 receives the selected image, without capture capability | No idle capture; no access outside the shared artifact |
| A generic click approval does not bind the intended effect | Bind approved target, exact payload, preconditions and observation scope in Wayfinder's action handler | Zero effects for changed, expired, revoked and cross-task grants |
| Authorization middleware can fail open | Enforce grants inside the final tool handler/broker and remove raw alternatives | Inject handler/middleware failures and confirm no action dispatch |
| A success summary may be wrong, or a crash may hide an already completed click | Verify postconditions; record uncertain outcomes and reconcile before retries | Crash before/after effects and duplicate-delivery tests |
| Five persistent agents are excessive | Use on-demand jobs; deterministic paths where sufficient | Measure latency and quality before adding autonomy or services |

The middleware concern is explicit in [Hermes's contract](https://hermes-agent.nousresearch.com/docs/developer-guide/middleware): failures can continue down the base execution path. Middleware remains useful for routing and telemetry, but cannot be the sole approval barrier.

Installed computer-use code keys approvals by action and mode, such as `cua:<action>:<mode>`. That is not the proposed exact operation contract. A bounded driver manifest can add restrictions but must be checked against the installed version and does not replace target/payload validation.

## Proposed integration

```text
Animal / quick-chat UI
        |
Wayfinder controller and trusted grant/action service
        |                         |
Hermes reasoning jobs       Existing Windows-capable driver
W33 / W35 / W36             behind scoped file/action adapters
        |                         |
Structured findings        W34 discovery / W37 approved effects
        +---------- verified results ----------+
```

The exact transport is a compatibility decision: prefer a supported plugin or MCP adapter and an existing driver endpoint. If the installed Hermes integration cannot reach Windows through an enforceable narrow channel, time-box an isolated Windows-side Hermes/driver trial. Do not expose the entire Windows home, arbitrary PowerShell, or a generic execution proxy to make it work. An unavailable Windows action remains unavailable rather than falling back to unrestricted execution.

Grant validation belongs where actual file opening or desktop input occurs. Workers cannot mint grants. Restrict administrative APIs and raw driver access to the trusted service, with per-job identity and scope. OpenShell controls apply to Linux sandbox execution; a bridge outside that sandbox requires its own host enforcement. [OpenShell 0.0.116 overview](https://docs.nvidia.com/openshell/v0.0.116/about/overview).

Proposed desktop approval fields: owner, memory space, task, machine/session, application/process/window identity, ordered actions and exact parameters, expected document/state, permitted observations, expiry, nonce and immutable digest. Revalidate the relevant target before each effect. Approve a meaningful bounded batch rather than every mouse movement or an open-ended goal. Material changes require a new proposal.

W33 sharing authorizes one selected image. W37 may need fresh feedback observations; the UI must include the specific app/window or region and task lifetime in its execution grant. There is no silent conversion from one screenshot into continuous observation permission.

File access must validate the resource actually opened, including Windows reparse points/junctions, traversal, case behavior, device/UNC paths and changes between discovery and read. Initially avoid following reparse points. Return versioned references and bounded content; filenames and directory listings are also scoped data.

Keep Iron Web authority with the controller. Worker findings are proposals or task outputs, not automatic memory writes. Do not supply main memory credentials, raw stores or unrelated conversations to desktop workers.

## Implementation order and acceptance gates

1. **Runtime compatibility and provenance.** Record exact managed image/source fingerprint, tool schemas, effective enabled tools and model routes. Resolve mismatched dependency pins. Check whether trusted tool narrowing and supported transport work in the installed build. No product upgrade is assumed.
2. **Read-only file slice, W34/W35.** Reuse the existing roles and a scoped filesystem implementation. Start with text/Markdown and formats whose installed parsers pass fixtures; add PDF/Office after extraction checks. Gate: zero outside-root reads or writes, version-change detection and explicit partial/unsupported results.
3. **Selected-image slice, W33.** Build attach/crop/preview handoff and reuse Hermes vision. Start with synthetic images. Gate: accurate grounding through the real provider path, visible uncertainty for ambiguous details, no additional observation tools, and tested image/transcript retention behavior. File and image slices are independently testable.
4. **Plan-only slice, W36.** Define allowed action schemas and review cards. Gate: schema-valid plans with exact targets, payload, observation needs and completion criteria; no execution on missing context or approval.
5. **One bounded Windows workflow, W37.** Use an existing ordinary-integrity test window and fixture data. Approve typing a fixed string and saving a new fixture file inside a test directory, with no overwrite. Gate: correct destination/content independently verified; cancellation blocks subsequent actions; modified grants and stale/replaced windows produce zero effects.
6. **Recovery and UI integration.** Exercise rejection, expiry, revocation, cross-space/cross-task input, prompt injection in files/images, duplicate delivery, driver failure and crash around an effect. Show queued/running/awaiting approval/stopped/failed/completed/outcome unknown. Never blindly replay send/delete/submit after uncertainty. Only then broaden supported actions.

Reuse the existing companion and memory patterns while evaluating Hermes's pet/UI options. This work should not become an unrelated UI migration, memory replacement or generic workflow-engine project.

## Proposed ADR

**Choice:** Hermes runtime plus bounded tool adapters and application-enforced grants.

**Alternatives:** five unrestricted default delegates (simple but insufficient separation); five permanent profiles (state overhead without OS isolation); a new custom agent runtime (duplicates Hermes); tool-only automation for everything (insufficient interpretation for images and planning).

**Trade-off:** a small amount of host integration and grant enforcement remains necessary. Reusing Hermes does not transfer Windows privacy or exact-action authorization to the model. Prefer existing compatible servers/drivers over new implementations; add code only for gaps demonstrated by the compatibility trial.

**Revisit triggers:** native Hermes controls prove equivalent scope enforcement; its desktop UI satisfies the companion requirements; measured task complexity justifies more autonomous workers; the current managed runtime cannot support a narrow Windows connection.

Research did not activate workers, install packages, alter runtime configuration, capture the desktop, read personal documents or invoke model inference. Product implementation remains the next proposed step.
