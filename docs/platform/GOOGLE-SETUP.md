# Google connection setup — 26 October 2026

Selected by the user: **Google Calendar, Google Tasks and Gmail**. Fitness remains deferred. The current integration is read-only; Gmail access returns message references, not bodies or message dispatch.

## Prepared locally

- Installed **google-auth-oauthlib 1.5.0**, google-auth 2.62.0 and dependencies into ignored `.local/google-oauth`, without changing the shared Python environment. The package release and provenance were checked against [Google's PyPI release](https://pypi.org/project/google-auth-oauthlib/1.5.0/).
- Reused the repository's existing `scripts/auth_google.py`, replacing import-time login with an explicit command and a no-network `--check` option. Default paths are anchored to the repository, independent of the current directory.
- Narrowed the consent request to `calendar.readonly`, `tasks.readonly` and `gmail.readonly`, matching the selected providers. No worker prompt or task/result contract changed.
- The installed SDK handles state and PKCE. Its callback binds to `127.0.0.1`, uses an ephemeral port and waits at most five minutes. `open_browser=False` means the user opens the displayed consent link manually. Token exchange has a ten-second request timeout, refuses redirects and ignores environment proxy overrides. This reuses [the official installed-app flow](https://googleapis.dev/python/google-auth-oauthlib/latest/_modules/google_auth_oauthlib/flow.html).
- Existing token files are preserved. A new token is created exclusively only after all three requested scopes and an offline credential are returned. Tokens are never printed. Provider exceptions are sanitized.
- Created the empty, ignored `secrets/` directory. No real OAuth client or token is present. No browser, callback server or account request was started during preparation.

## Human steps

1. In your [Google Cloud project](https://console.cloud.google.com/), enable **Google Calendar API**, **Google Tasks API** and **Gmail API**. Configure the OAuth consent screen for your account; if using an external app in testing, add your account as a test user.
2. Under **Google Auth platform → Clients**, create an OAuth client of type **Desktop app**, then download its JSON. Save that file as:

   ```text
   C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant\secrets\credentials.json
   ```

   This must be a desktop OAuth client, rather than an API key or service-account key. Google's [credential setup guide](https://developers.google.com/workspace/guides/create-credentials) and [Python quickstart](https://developers.google.com/workspace/calendar/api/quickstart/python) explain the project/client setup. Do not paste the JSON or resulting token into chat.

3. Tell Codex when the client file is saved. Technical setup is already prepared. The consent command is:

   ```powershell
   & 'C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant\ops\Connect-Google.ps1'
   ```

   Open its displayed URL yourself, select the intended account, and grant the three read-only permissions. The browser redirects to the local callback. Successful consent stores private `secrets/token.json`; it does not read account data or establish a live-provider pass by itself.

## Checks and bounded account qualification

Local checks issue no account requests and start no browser or callback listener:

```powershell
& 'C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant\ops\Connect-Google.ps1' -Check
& 'C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant\ops\Test-GoogleConnection.ps1'
```

After consent, Codex can run:

```powershell
& 'C:\Users\User\.codex\worktrees\ui-backend-integration\AI assistant\ops\Test-GoogleConnection.ps1' -Live
```

That uses the authenticated application API and the real read adapters with a fresh temporary application store. It grants and revokes each exact resource: primary calendar for the next 24 hours, default task list, and Gmail `INBOX`. Each read is capped at **three items and one page**. It sends no messages, creates no events/tasks, invokes no model, opens no desktop UI, and accesses no live Iron Web store.

The qualification report saves **only counts, status and latency**, without event titles, task notes, message IDs, credentials or source content. Private report: `.local/verification/google-account-read.json`. Empty results can establish endpoint connectivity; they do not prove content accuracy. Failure remains explicitly unconfirmed, with no automatic write or retry.

To repair a missing helper later, `Connect-Google.ps1 -Prepare` installs the pinned optional dependencies locally and runs only the local setup check. It does not start consent.

## Evidence

Local checks confirm the OAuth helper is installed while both the real client file and token are absent. **41 focused tests passed** in 28.69 seconds, with no skips or failures. They cover scope selection, manual loopback consent settings, installed-SDK PKCE compatibility without network, token preservation, partial-consent rejection, invalid endpoints, error sanitization, bounded qualification and the existing source adapter boundaries. Results are recorded in `.local/verification/google-setup.xml`. Ruff and diff whitespace checks passed.

Live Google account qualification remains pending the human client-file and consent steps. W37 native desktop testing remains disabled.
