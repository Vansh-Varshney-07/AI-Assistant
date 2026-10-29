# Desktop references: actual REA investigation

Research date: 27 October 2026. Purpose: strengthen Wayfinder's UI/UX and security plan using actual REA execution, while retaining only Wayfinder's existing features.

This follows the earlier documentation/source study. That earlier study did not execute REA; this pass did. The two evidence tiers must not be confused.

## Tool preparation and method

1. Read the cloned REA README, repository instructions, `reverse-engineer-anything` skill and relevant CLI, JavaScript, artifact, evidence and recovery guides.
2. Used the actual ignored clone at commit `570abe95f`, package version 6.8.0. Installed its locked dependencies with lifecycle scripts disabled. Its documented `npm run build:cached` completed successfully.
3. Existing Node 22.19.0 and 24.19.0 did not satisfy REA's declared engine range. Downloaded the pinned portable Node 24.22.1 into ignored research storage and verified its official SHA-256. System Node, Codex MCP registration and model configuration were unchanged.
4. Restored REA's matching Windows native control manifest/addon from the integrity-verified `rea-agents@6.8.0` npm tarball, following its source-checkout recovery instructions. No disassembler or reference application was installed.
5. Acquired official public distribution artifacts, verified their published hashes, inventoried/extracted selected contents and invoked REA's real static CLI workflows. Existing 7-Zip performed ordinary archive extraction; those extraction operations are not mislabelled as REA analyses.
6. Retained original stdout, stderr, exit codes, source selections, artifact identity and complete or partial Evidence. Used actual REA feature/semantic traces where supported. Supplementary reads of packaged code are labelled separately from REA output.

No target installer, application, browser UI, Python module or JavaScript bundle was executed. No desktop capture, clipboard inspection, account connection, provider action or native UI automation occurred. Analysis tools and their owned workers did run.

## Results for all six references

| Reference and artifact | Actual REA work | Coverage and limitations | Report |
| --- | --- | --- | --- |
| AnythingLLM Desktop 1.19.0 Windows installer/ASAR | Main-bundle static analysis with preserved timeout Evidence; successful analysis of remaining assistant/preload/HTML files; preference-channel and assistant-module traces | Large main bundle timed out at its 120 s per-source deadline. Static facts were retained and reused. The remaining selection passed, but imported bridge/native ownership and most application files remain outside coverage. | [AnythingLLM](anythingllm.md) |
| CLAI 26.10.23 Windows installer/native executable | Desktop-directory, PE import/certificate/resource and Rust metadata inspection; native follow-up recorded in its report | Native artifact facts do not establish embedded frontend behavior or permission enforcement. No full native decompilation or runtime test. Previously reviewed source is a separate tier. | [CLAI](clai.md) |
| Keel 0.5.1 Windows ZIP/ASAR | Static main/preload/core analysis, preserved authenticated partial Evidence | Six JavaScript files completed; final minified renderer hit the 60 s per-source deadline. The failed call was not replayed unchanged. Complete renderer behavior remains unknown. | [Keel](keel.md) |
| Historical Khoj Desktop 1.33.1 installer/ASAR | Selected static analysis, saved-Evidence summary, file-picker and continue-conversation IPC traces | Historical companion app, not the current server/web UI. Four JavaScript files parsed. Most dependency files and an inline HTML body were outside analysis; IPC ownership remained ambiguous. | [Khoj](khoj.md) |
| Handrail 0.1.9 portable release/ASAR | Selected static analysis and exact setup-channel feature trace | Eight JavaScript files parsed; no parse failures. Selected coverage remains partial, and generic IPC pairing did not establish every sender/handler boundary. | [Handrail](handrail.md) |
| Hearth 0.7.5-preview Lite installer and separate published code ZIP | Desktop inventory; published UI HTML analysis; exact provenance-recorded inline-JS analysis; permission-handler semantic caller trace | Available extractor could not open the installer. UI/code ZIP identity with installed bytes is unknown. Inline semantic retention is partial. Python source inspection is supplementary and was not executed by REA. | [Hearth](hearth.md) |

Each report names the exact downloaded and extracted hashes, Evidence IDs, original command locations, derived-artifact provenance and unanswered questions. A zero exit code is an operation result, not a security approval or a complete reverse-engineering verdict. A timeout with partial Evidence is not reported as a passed full analysis.

Khoj's official download page returned 404; its historical publisher-hosted installer was identified through Microsoft's package manifest and checked against that manifest's hash. The publisher's [service notice](https://app.khoj.dev/) states that Khoj Cloud shut down on 15 April 2026. The prior live-cloud recommendation is therefore not current qualification.

## Changes this evidence makes to the Wayfinder plan

| Package finding | Design/security decision for existing Wayfinder features |
| --- | --- |
| Handrail's packaged storage has an OS-encryption-unavailable plaintext/base64 fallback. | Keep Wayfinder's vault fail-closed. Explain the import/encryption error and preserve previous credentials; no plaintext fallback. |
| Keel's packaged settings include credential fields, plain JSON persistence and a direct get-settings path; new-install defaults enable its cloud mode. | Keep secrets out of renderer settings. Display the actual approved provider/destination and disclosure scope. A desktop app must not imply every operation stays on-device. |
| Hearth's published permission UI can approve on Enter, includes persistent/voice choices, and truncates the argument preview and tooltip. | Keep Cancel as the safe default; complete exact payload/target review; main-owned one-time confirmation; service revalidation. Do not add persistent or voice approval. |
| AnythingLLM has a dedicated assistant conversation/preferences flow, including screenshot context in its packaged renderer. | Adapt conversation continuity and clear stop/error states to existing Chat. Keep the in-app palette; exclude screenshot context, global overlay and new background behavior. |
| Khoj's old companion has separate file-selection/conversation IPC and background synchronization code. | Clarify explicit source selection and return-to-result navigation. Keep selected reads and model disclosure separate; add no background sync or clipboard access. |
| CLAI's native imports/resources do not prove its visible permission policies are enforced on Windows. | Keep Wayfinder's existing managed sandbox and final-handler checks. A profile card, checkmark or import name is not evidence of authorization or containment. |

These are static observations and Wayfinder-specific design choices, not exploit demonstrations or universal judgments about the reference products. Generic parser counts such as zero sender-validation observations do not prove that custom sender checks are absent.

## Scope of the next implementation

The [Wayfinder adaptation plan](../../platform/UI-UX-SECURITY-ADAPTATION-PLAN.md) remains limited to existing Chat, Documents, Memory, supported profile variants, Runs, Connections, Local Git, Permissions and settings/runtime views. Its first changes should correct stale feature/connection language and expiring badges, then improve the complete selected-document flow and exact review presentation.

Borrow interaction structure, not authority or capability breadth. Hermes stays the runtime, Atlas the discovery layer, Iron Web the memory system and Wayfinder's trusted handlers the enforcement point. No app implementation, account scopes, global shortcuts, scheduler, new memory store or desktop action capability was changed in this investigation.

## Retention and reproduction

The ignored `.local/rea-research/` tree contains the portable toolchain, verified downloads, selected extracted artifacts, source/derivation manifests, raw analysis output, commands, errors, execution records and traces. The cloned `rea/` folder remains ignored. Research notes and the compact [execution index](execution-index.json) contain reviewable provenance without committing the large third-party packages or raw graphs.

The remaining limitations are concrete: full minified semantic recovery for timed-out sources, native CLAI UI/permission decompilation, Hearth installer-to-code identity, and all runtime visual/accessibility/provider behavior. They are not filled in with screenshots, model assumptions or source-only claims. Native interaction testing remains disabled until explicitly re-enabled by the user.
