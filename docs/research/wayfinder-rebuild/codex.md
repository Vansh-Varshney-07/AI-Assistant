# Codex desktop: bounded REA investigation

27 October 2026. Read-only installed-artifact analysis; Codex was not launched, modified or attached to. No account, conversation, clipboard or desktop capture was read. Wayfinder uses independently authored implementation and existing features only.

## Target and method

The correct target was OpenAI.Codex MSIX 26.1021.3705.0's `app/resources/app.asar`, 640129388 bytes, SHA-256 `04862a659c6a90fc50514d8c0b8016709d97dece58839726c57495ed72f1d9f0`. Its package identifies `openai-codex-electron`, product Codex, version 26.1021.31345. The initially discovered `Codex/bin/2993767bd1dfb009/codex.exe` was a worker CLI and supplied no desktop-UI evidence. That target error was corrected before drawing UI conclusions.

Used the cloned REA 6.8.0 script with Node 24.22.1, archive inventory, selected member extraction and hash verification, then actual bounded JavaScript semantic analysis. Raw vendor assets and evidence remain ignored under `.local/rea-research/codex-20261027/`; none are application assets.

| Analysis | Actual Evidence ID | Outcome |
| --- | --- | --- |
| Chat: seven selected JavaScript assets | `ev_aa63ecbbf8cd65077121da8a59434fbbe5e3e5f361eb290fab5c428b75f4bba9` | Exit 0; 100.25 seconds |
| Theme: seven selected JavaScript assets | `ev_bcb168656fcd5353d19726be31b101db40a625ef65c37e256c0b08562f715094` | Exit 0; 107.703 seconds; zero parse failures |
| Theme summary | `ev_68ff6308888547343131150f9783be3b97ebcb82e9d87dba673ba2893db7091c` | Bounded semantic summary |

Ten selected chat assets and nine selected theme assets matched their declared archive member hashes. Eight unrelated unpacked native members had integrity contradictions. The first analysis stopped on integrity; a documented read-only `record-and-continue` run preserved those contradictions. CSS was removed from JavaScript selection after a parser failure. Selected UI hashes were independently verified. These checks do not authenticate the entire installation or establish why native hashes differed. Approximately 16900 files and imported relationships remained outside selected scope; semantic graphs contain unresolved relationships.

## Findings and Wayfinder decisions

Two shipped theme families exist: Codex base uses white/light neutral ink and a blue accent; the ChatGPT family uses near-white/neutral ink, with monochrome primary controls and subdued secondary controls. These are static declarations, not proof of the user's active theme. Adopt the neutral surface hierarchy and semantic focus/error/success colors; do not present either family as the universal Codex default. Use one Wayfinder token source for light and dark.

`codex-composer-adapter-dfdbf299b26d.js`, adapter `vr`, byte 18081, separates history loading, response progress, local submit start/error, draft resolution and stopping. Adopt independent editing/submission/history/execution states. Keep editing available during generation; Wayfinder does not automatically queue follow-ups.

`pending-auto-scroll-controller-de59c71c13d0.js`, exported `Te`, byte 19370, contains interaction cancellation, eligibility/visibility checks, size stabilization and cleanup. Most of this chunk concerns advertising: this does not prove a universal transcript-follow policy. Independently implement explicit follow-latest state and saved reading position, with a Latest recovery action; copy no ad behavior or timing constant.

`composer-host-48ffae0009ed.js` is a sketch/editor host. Save/discard/keep-editing logic cannot be claimed as normal chat draft persistence. `composer-placement-state-53ad45baa9de.js` concerns pinned advertising, not general composer layout. Neither feature is added.

`composer-approval-request-card-e5b1b58d9fde.js`, component `z`, byte 1689, separates review content, reason, action groups, denial and loading/disabled handling. Adopt readable accessible review surfaces. Broader standing/conversation approvals and approval shortcuts are excluded; Wayfinder retains exact-action enforcement in trusted handlers.

Theme modules expose semantic color generation, separate UI/content/code font roles, bounded reading widths, flex/min-size layout rules and centralized theme application. Reuse principles, not proprietary implementation. The .25rem spacing unit is 4px only with a 16px root. Static widths and variables are not measured live geometry.

## Evidence limits and verification

This research demonstrates declarations and bounded code paths only, not installed runtime behavior, security enforcement, account integration or provider performance. Wayfinder's own unit, rendered-fixture and packaged tests must establish its behavior separately. Official product context: [Codex app introduction](https://openai.com/index/introducing-the-codex-app/). Local artifact evidence supplies the implementation observations above.
