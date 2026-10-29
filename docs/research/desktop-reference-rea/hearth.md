# Hearth: actual REA static artifact investigation

Date: 27 October 2026. REA: locally built `rea-agents` 6.8.0; isolated Node 24.22.1. No Hearth application, installer, Python module, browser, screen or clipboard operation was executed.

## Two distinct public artifacts

Both files came from the publisher's [v0.7.5-preview release](https://github.com/0pen-Sourcer/Hearth/releases/tag/v0.7.5-preview), and their SHA-256 values matched the GitHub asset metadata:

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| `Hearth-Setup-Lite-v0.7.5-preview.exe` | 665,266,475 | `e89b9846f45d475a85b057bfed89120d53d333c89517efd272fc84110956c325` |
| `hearth-code-0.7.5-preview.zip` | 133,843,814 | `ef156d6c42c6cc02d6f8f80ebb6b28ec6569cae8eb0cd0b4d9fbef7e178b045b` |

The installed 7-Zip could not unpack the installer. It was not run to get past that limitation. The separate published code-distribution ZIP contains 3,931 members. Ordinary ZIP inspection and checked extraction selected only `hearth/ui.html`, `web.py`, `tools.py`, `redact.py` and `headless.py`. No dependency code was imported. Correspondence between those ZIP members and the installer's embedded application bytes is **not established**.

Acquisition and selected-extraction records are under `.local/rea-research/artifacts/Hearth/` and `.local/rea-research/extracted/hearth/`.

## Actual REA analysis and trace

The CLI commands use the isolated Node executable with `rea/scripts/rea.mjs`; each appended `--format json` and exited 0. Original JSON/stderr/exit records remain under `.local/rea-research/results/hearth/`.

| Step | Actual outcome | Evidence ID |
| --- | --- | --- |
| `inspect-desktop-application <artifacts/Hearth>` | Header/directory observations of supplied distributions, not an installed application's behavior; four entries examined, one file probed, 324 bytes read. | `ev_59e0d3948ca17b5165d88da052df230ce1817420fa21e0e2056ddae3967e2987` |
| `analyze-javascript-application <extracted/hearth> --source-path hearth/ui.html --max-heap-mb 512 --analysis-timeout-ms 90000 --max-semantic-nodes 10000 --max-semantic-nodes-per-file 10000` | Read 722,789-byte HTML. Explicitly reported that its inline JS body was not analyzed. Exit 0 therefore did not answer the permission-flow question. | `ev_27eb05b9aba0336d86c31efe39a520e3473047471cd8a46b8e4b4e0937cc20af` |
| `analyze-javascript-application <derived/hearth-inline> --source-path inline-1.js --max-heap-mb 512 --analysis-timeout-ms 90000 --max-semantic-nodes 10000 --max-semantic-nodes-per-file 10000` | Parsed one exact extracted JS body; 58,621 AST nodes visited, 70 structural findings, no parse failures. Semantic retention reached 10,000 nodes: partial coverage, 9,327 relations and 12,016 unknown records. | `ev_15eba3bfafe4783b92d557d0a68b7be5bf1d7c5a05baba2a5c406039f191e204` |
| `trace-javascript-semantics <permission-trace-input.json>` | Caller query against retained `sendPermDecision` function identity, restricted to `calls`. Found one seed, 10 traversed nodes, 9 relations, 7 functions and 2 relevant unknowns; query coverage partial. | `ev_ec2aa1ce9f892f32dc46350a43ce7bc68d7ff5dc72d3a458369c5b32d728f91a` |

The trace input embeds the original authenticated application Evidence; it does not reopen or execute the UI. The seed was `jsrg_node_3b864e422ca6934aec6dbaf86fd242f1ee9a1ff0da6ba0da3431019ecc2c9cab`.

### Derived-script provenance

The HTML SHA-256 is `bdb7f8a5fcfb00b61580089d705dbba890e90a0a76e70247c081340eab6c6bc1`. Its one nonempty inline script was extracted using REA's installed `parse5` dependency and exact `sourceCodeLocation` offsets, without rewriting. The body spans UTF-16 offsets 206568–721506, begins at HTML line 4375, and hashes to `431cb8fc8f93cce3c93610c4f597943b53725a09f6b87cab1cc1c32fbb7f3105`.

The derivation manifest maps these identities under `.local/rea-research/derived/hearth-inline/derivation.json`. The derived directory's root digest is not the ZIP digest or installer digest. The initial HTML role labelled `electron-renderer` is a static classification inference, not proof that Hearth runs an Electron renderer.

## Permission interaction recovered

**REA static trace plus exact published code inspection:** `sendPermDecision` has caller sites for the permission-strip buttons, close/deny, numbered choices, voice-text interpretations, and an Enter-key default. Relevant original HTML lines are 4815–4843, obtained by mapping derived script locations back to the HTML. The Enter path passes `allow`; choices also include persistent `always` and `never`. These are static call candidates, not observed live interactions.

**Published source inspection, not a Python REA execution:** the HTML event handler at line 7643 passes `permission_request` data into `showInlinePermission`. That function (around line 4694) fills the tool/argument preview, then `sendPermDecision` (around line 4733) POSTs the decision to `/api/permission`. The argument summary is truncated to 160 characters, and the tooltip receives that same shortened string; it cannot be relied on as a complete exact-payload review.

In `web.py`, `_make_permission_check` (around line 430) creates a per-request queue, emits `permission_request`, waits up to 180 seconds and preserves timeout as a distinct outcome. Persistent per-tool allow/deny decisions and a settings-driven automatic-approval path are also present. These are file-derived facts from the published code ZIP; the Python handler was neither executed nor decompiled by REA, and deployment enforcement remains unverified.

The same source has loopback Host-header checks alongside permissive CORS response headers. This is a reason to retain Wayfinder's authenticated bridge, validated senders and final scoped handlers rather than transplant this web transport. No exploit, runtime security verdict or complete origin/CSRF audit is asserted.

## Adaptation to existing Wayfinder features

- Reuse the understandable attention pattern: one clear pending-decision surface near the work, with a readable target summary and source-backed details.
- Retain Wayfinder's trusted main-process confirmation and exact immutable proposal. A renderer strip must not approve effects on its own.
- Keep complete payload/target review available. Do not copy a 160-character security preview as the only review or tooltip.
- Keep Cancel as the safe initial/default choice. Do not adopt Enter-to-approve, voice approval, persistent tool-wide allow rules or automatic-approval mode.
- Reuse the useful timeout distinction: unanswered/expired is separate from rejected and completed. Completion still requires a verified receipt; canceling a client stream is not proof a server action stopped.
- Keep the original task boundary, source scopes, expiry/revocation and uncertain-outcome reconciliation. No new shell, voice, computer-control or memory feature is introduced.

## Remaining unknowns

Semantic coverage is partial and the caller trace has two relevant unknowns. Python transport/enforcement was inspected as source only. The installer could not be unpacked with available tools, so the analyzed UI's identity with installed bytes is unknown. Native UI, visual layout, keyboard focus, live provider behavior, actual requests and action outcomes were not tested. This is a supported static investigation, not proof Hearth is secure or that Wayfinder's proposed adaptation already works.
