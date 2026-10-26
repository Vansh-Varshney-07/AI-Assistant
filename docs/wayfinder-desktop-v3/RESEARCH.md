# Research and decision record

26 October 2026. Primary documentation and repository source inspection. This is a design recommendation, not a dependency install or compatibility certification.

## Desktop choice

- [Electron's application showcase](https://www.electronjs.org/apps) lists established applications including VS Code, Slack and Discord. This supports describing Electron as established; it is not a market-share study for AI assistants.
- [Current upstream Hermes Desktop package manifest](https://github.com/NousResearch/hermes-agent/blob/main/apps/desktop/package.json) uses Electron, React, TypeScript, Vite, Tailwind, React Query and assistant-ui. Current upstream source is moving and differs from an installed-version qualification. Pin a compatible revision before reuse.
- [Hermes Desktop Plugin SDK](https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk) documents contributions for panes, routes, navigation, themes and commands. This makes an extension assessment worthwhile. It also exposes broad host/gateway operations: extension availability alone does not prove Wayfinder's final-handler restrictions can govern the complete app.
- [Hermes Desktop documentation](https://hermes-agent.nousresearch.com/docs/user-guide/desktop) describes the shared agent/session/configuration model. Preserve useful continuity while testing Wayfinder's stricter scopes and memory access. Do not substitute the web dashboard, native plugin SDK and Python plugin SDK for one another; they are different interfaces.
- [Tauri's process model](https://v2.tauri.app/concept/process-model/) and [WebView documentation](https://v2.tauri.app/reference/webview-versions/) support its Rust-core/system-WebView alternative. Smaller packaging is a reason to evaluate it if measured requirements demand it, not a reason to discard the existing Hermes-aligned stack prematurely.

## Supporting frontend choices

- [electron-vite](https://electron-vite.org/guide/) supports modern desktop development with separate process builds. Reuse an adopted upstream host's own tooling instead if the extension route qualifies.
- [Vite](https://vite.dev/guide/) documents React/TypeScript scaffolds. A desktop React renderer does not need an SSR/application server merely to host its UI.
- [shadcn/ui component catalogue](https://ui.shadcn.com/docs/components) covers the sidebar, dialogs, forms and resizable surfaces required here. The Hermes SDK's native UI kit is preferred when extending that host.
- [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) supports asynchronous server-state presentation. It is not the authoritative workflow or scheduling engine.
- [Electron context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation) recommends narrow per-operation bridges; [renderer sandboxing](https://www.electronjs.org/docs/latest/tutorial/sandbox) explains the process boundary. Keep authoritative domain permissions in existing Python handlers too.
- [Playwright's Electron API](https://playwright.dev/docs/api/class-electron) is explicitly experimental. Use it with manual Windows packaged-app verification and component tests.

## Observed local integration facts

1. `wayfinder/api.py` is a loopback bearer-authenticated API that rejects browser Origin/fetch calls. Route renderer operations through a narrow main-process broker rather than weakening this check.
2. `wayfinder/service.py` states that general chat is local transcript storage. An actual Hermes chat-run binding is mandatory new R1 work.
3. `wayfinder/workers/hermes_runner.py` currently binds bounded W33/W35/W36 analysis. It is not a ready general-purpose chat facade.
4. `wayfinder/platform/service.py` supplies one fixed read workflow. Arbitrary workflow graphs remain a new qualification task.
5. `wayfinder/platform/google_read.py` supports Calendar/Tasks and Gmail message-reference reads. Live accounts, Gmail body retrieval and account writes are separate gates.
6. `memory_control.py`, `actions.py`, `git_connector.py`, `evaluation.py` and the file broker provide reusable approvals, receipts, reconciliation, artifact checks and grants. Expose their actual operation limits honestly.
7. Existing Tkinter UI is source evidence and a fallback during migration. No code or data was removed for this plan.

## Decisions

| ID | Decision | Revisit when |
|---|---|---|
| D1 | Electron + React + TypeScript for the planned desktop UX. | Measured resource/platform constraints make it unsuitable. |
| D2 | Assess supported Hermes Desktop extension reuse before implementing a standalone host. | Qualification establishes whether complete authoritative routing and required UX are possible. |
| D3 | Keep Python, Iron Web and managed Hermes as existing service/runtime layers. | A separately reviewed migration is justified by evidence. |
| D4 | R1 ships genuine chat; avoid a release made only of empty navigation pages. | R1 manual acceptance exposes missing essential behaviour. |
| D5 | Stable layout, gradually revealed features and cumulative acceptance. | User tests demonstrate a navigation problem. |
| D6 | Step-list workflow editing before a visual canvas. | Workflow complexity/user testing warrants graph editing. |
| D7 | Reuse Hermes scheduling/delegation where qualified; no duplicate general runtime. | Installed capability cannot satisfy a documented requirement. |
| D8 | Explicit review remains a trusted operation, independent of chat output. | Never broaden merely for convenience. |
| D9 | New planning files only; no app implementation, launch or environment changes. | User selects an implementation release. |

Unknowns to resolve in the implementation spike: installed Desktop SDK compatibility; Windows-to-WSL lifecycle and authenticated chat events; model streaming support; packaged Python ownership/launch; cold-start and idle-memory measurements; full numbered worker-name catalogue; and actual account/driver qualifications. These do not prevent designing a coherent UI, but must not be filled with invented working-state claims.
