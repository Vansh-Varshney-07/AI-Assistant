# Desktop connections 0.4.1

Connections now supports user-triggered Google Workspace, Tavily and Notion reads. Account writes, automatic account access from chat, scheduling, fitness and W37 remain unavailable.

## Reuse and new integration

- Google extends the existing `GoogleRead` grant boundary and installed `google-auth` AuthorizedSession.
- Notion reuses `NotionAdapter` search/page normalization. `BoundedNotion` adds the missing constrained transport: fixed endpoints, no redirects, read-only operations and response/time budgets.
- Tavily uses the installed Hermes 0.21.3 `TavilyWebSearchProvider` inside the existing OpenShell sandbox. Fresh isolated Hermes profiles do not enable global plugins, so this specific bundled provider is loaded directly. Search invokes no LLM.
- Electron 45 safeStorage provides Windows account encryption. The new vault and owned-stdio bootstrap connect local credentials to the packaged backend. No replacement agent framework, parser, memory store or scheduler was added.

## Interfaces and enforcement

`connections-v1.bin` stores a version-one encrypted bundle. The private `connections_configure` host operation receives it through app-owned stdio only; it is absent from the authenticated HTTP API and preload methods. No secret enters renderer results, worker prompts, Iron Web, the application database or the executable.

Named methods provide connection status/checks, Google grant/read/revoke and external grant/read/revoke. Grants bind owner, space, task, resource/intent and expiry. Rotation invalidates grants and withholds in-flight results. External reads have two concurrent slots, three results, a 40 KB display budget and 120-second grants. Google retains its existing bounded exact-resource grants. Source text is escaped and cannot mint permissions.

Only NVIDIA `nvidia/nemotron-3.5-lightning-30b-a3b` and `nvidia/nemotron-3-ultra-550b-a55b` are allowed for generative inference, through `integrate.api.nvidia.com`. Managed Hermes remains the model credential source. Gemini keys are ignored. Automatic vision fallback is rejected. Local BGE memory embeddings are unchanged.

This laptop's OpenShell policy needed one additional rule for `/opt/hermes/.venv/bin/python`: HTTPS `POST /search` at `api.tavily.com`. No other Tavily endpoint or desktop permission was enabled. Other installations must configure this same narrow route if denied.

## Supported reads

| Source | Connection behavior |
| --- | --- |
| Calendar | Selected calendar, default next 24 hours |
| Tasks | Selected task list |
| Gmail | Selected label, headers and short snippets; no message bodies |
| Drive | Files in an exact folder, default root |
| Docs | Exact document ID, identity/title metadata |
| Sheets | Exact spreadsheet ID, title/sheet metadata; no cell data |
| Contacts | Bounded connected-account contacts |
| Tavily | Explicit public query, up to three sources |
| Notion | Search shared pages, explicitly open a bounded excerpt |

Results stay in the current view with no automatic memory publication or model disclosure. Live checks expire after five minutes and reset on restart. Local disconnect removes that provider from the encrypted vault and invalidates app grants. Revoke OAuth or API keys at the provider separately if desired.

## Manual acceptance

1. Quit the older app and open `Wayfinder-0.4.1-Windows-x64.exe`. Keep Docker Desktop and the existing managed Hermes/OpenShell runtime running. Fresh onboarding checks the bundled CPU memory model, private database and displayed NVIDIA model before chat consent.
2. Open **Connections**. Import your local `.env` or Google token JSON if not already imported. Referenced Google tokens must stay within the selected project folder. Never paste keys into chat.
3. Run all three live checks. Imported credentials and verified provider access have separate badges.
4. Read Calendar/Tasks/Gmail, select Drive/Contacts, and search Tavily/Notion. Open a shared Notion page explicitly. Docs/Sheets require an accessible exact ID; suitable Drive results offer inspection buttons.
5. Restart: imported credentials persist while live checks return to pending. Disconnect and verify reads stop; import again to reconnect.

## Verification

Synthetic contracts cover cross-space/task access, expiry, revocation, rotation during reads, field/response bounds, document/message identity, private bootstrap exclusion, encryption failures, HTML escaping and model-policy rejection. `Test-Backend.ps1` uses a disposable database and includes connection contracts.

`scripts/verify-connections.mjs <empty-profile> <report.json> <local-credential-file>` tests a hidden packaged app, real Windows encryption, fresh onboarding, live provider reads, synthetic chat and restart. Reports contain check results/counts, never account content. Cleanup targets only labelled test-owned database resources. This does not prove native mouse, file-picker, Windows dialog or W37 behavior.

Keep account-linked paths and live reports in ignored private storage. The portable app contains public code/models, and still requires the existing Docker/Hermes runtime; it does not install those systems automatically.
