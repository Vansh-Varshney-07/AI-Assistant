# Productivity connector feasibility

Public primary-source research, checked 24 October 2026 (Asia/Calcutta). This is planning research: no accounts were connected, messages sent, integrations installed or runtime code changed. There is no research Git repository/remote in this workspace, so the context asset is recorded directly in the local Markdown tracker rather than a pushed research branch.

## Recommended boundary

Build separate connector capabilities for reading, drafting, creating, updating, deleting and sending. Provider authorization defines the maximum possible access; Iron Web policy and the user's action approval must narrow it further. A vector match can discover candidate tools, but must never grant credentials or bypass these checks. This is an architectural recommendation derived from the APIs' distinct permission models below.

Only the orchestrator reads or commits durable Iron Web memory. Connector workers return source objects and proposed task updates. Retain provider IDs, account IDs, timestamps and provenance separately from an LLM's inferred deadline or priority. An email asking someone to do something is evidence for a proposed task, not authorization to send mail or modify a calendar.

## Gmail: feasible for work intake

Requires a Google project with Gmail API and OAuth consent/client configuration plus the account holder's authorization. Start with `gmail.readonly` for extraction. `gmail.metadata` excludes bodies and therefore cannot support general body-based task extraction. Sending (`gmail.send`), draft management (`gmail.compose`) and mailbox modifications (`gmail.modify`) are separate escalation choices; compose also permits sending, so a draft-only application policy remains necessary. Readonly, metadata, compose and modify are restricted scopes; send is sensitive. Public distribution and server-side storage/transmission of restricted data create verification/security-assessment requirements described by Google. Do not assume sending Gmail contents to hosted Nemotron is exempt. [Gmail scope reference](https://developers.google.com/workspace/gmail/api/auth/scopes)

Use message/thread IDs to retain links to the original evidence and deduplicate intake. Persist a `historyId` cursor; partial sync uses `history.list`. An expired/unavailable cursor produces HTTP 404 and requires a bounded full resynchronization. History availability is not a permanent journal. [Gmail synchronization](https://developers.google.com/workspace/gmail/api/guides/sync)

Server push uses Cloud Pub/Sub and a mailbox `watch`; renew at least every seven days, with daily renewal recommended. Notifications trigger retrieval of changes rather than delivering complete email contents. For a desktop-only first version, Google's guide recommends polling synchronization for user-owned devices; this avoids requiring an inbound public desktop webhook. [Gmail push guide](https://developers.google.com/workspace/gmail/api/guides/push)

## WhatsApp Business: feasible with an explicit onboarding gate

Target Cloud API traffic for a registered business number. Meta's official collection identifies business portfolio, WhatsApp Business Account (WABA), business phone-number IDs and access tokens, and distinguishes `whatsapp_business_messaging` from `whatsapp_business_management`; portfolio operations may additionally need `business_management`. Meta supplies test numbers and webhook/sandbox material. Production onboarding, number eligibility and any advanced-access/app-review requirements must be checked against the chosen business/account path rather than assumed from a development token. [Meta-owned Cloud API collection](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api), [official developer hub](https://whatsappbusiness.com/developers/developer-hub/)

**Scope decision:** ingest messages and delivery/status events received through the connected business integration. Do not promise arbitrary personal WhatsApp history, all chats on a device, or historic Business App messages. A WABA/token integration does not establish that access. This is an inference from the business-asset integration model; any Business App coexistence/history-import path requires a separate, account-specific investigation. Avoid unofficial session scraping as the default connector.

The official messaging policy, updated 23 September 2026, requires opt-in for subsequent contact, respect for opt-outs and approved templates for business-initiated conversations. Free-form replies are permitted within the 24-hour customer service window, which opens/resets with each user message; outside it approved templates are required. Automation also needs a clear escalation path. Therefore approval is necessary but cannot override provider restrictions. [Current WhatsApp messaging policy](https://whatsappbusiness.com/policy/)

Treat incoming webhook objects as potentially repeated and retain provider message IDs; keep send receipts and status transitions in the workflow journal. Exact webhook retry timing was not verified from an accessible current Meta page and must not become a reliability assumption. Meta's developer overview returned HTTP 429, and its current platform terms redirected to a login/temporary-block page during this research. **Before production, verify current platform/AI-provider terms and eligibility for this exact business workflow.** The plan does not claim a general-purpose AI chatbot delivered over WhatsApp is approved. [Platform terms entry point](https://www.whatsapp.com/legal/business-solution-terms)

## Notion: feasible for selected notes and task records

An internal connection belongs to one workspace, is created by a workspace owner, and uses a static token; pages must be explicitly shared with it. Public connections use OAuth for multi-workspace installation; current documentation also describes user-scoped personal access tokens. Pin the API version: the current guide demonstrates `2026-03-11`, so older database-only assumptions need review. [Notion authorization](https://developers.notion.com/guides/get-started/authorization)

Grant read content for intake, insert content for approved new task pages, and update content only for approved edits. These are independent capabilities; sharing a parent exposes its children subject to capabilities. Model tasks with chosen data-source properties and page/block notes, rather than claiming access to every private workspace page. [Connection capabilities](https://developers.notion.com/reference/capabilities)

Integration webhooks need a public HTTPS endpoint; localhost is insufficient. Verify `X-Notion-Signature` against raw request bytes. Events identify objects to refetch; content changes may be aggregated and delayed, so they are not a keystroke log. [Notion webhooks](https://developers.notion.com/reference/webhooks)

Queue requests and honor `Retry-After`; limits depend on plan, workspace and endpoint. Crucially, a write can commit and still return 503. Current docs expose retry guidance and sometimes committed object/child IDs; reconcile those objects before retrying. Do not let a generic retry loop create duplicate tasks or note blocks. [Notion request limits and committed-write guidance](https://developers.notion.com/reference/request-limits)

## Google Calendar: feasible for approved scheduling

Use user OAuth with the API enabled. Availability can use free/busy scopes; event reading uses `calendar.events.readonly`. For initial writes, `calendar.app.created` allows an app-created secondary calendar and limits reach; broader event scopes are needed for existing calendars. Calendar authorization is separate from Gmail, and actual calendar permissions still matter. [Calendar scopes](https://developers.google.com/workspace/calendar/api/auth)

Persist `nextSyncToken`, handle pagination/deleted events and rebuild only the connector's calendar cache on HTTP 410. This must not wipe Iron Web memory or the workflow journal. [Incremental sync](https://developers.google.com/workspace/calendar/api/guides/sync)

Push watches are per resource/calendar, expire and need renewal; notifications contain headers rather than event bodies. Google explicitly says notifications are not fully reliable, requiring reconciliation. [Calendar push](https://developers.google.com/workspace/calendar/api/guides/push)

Preview the calendar, timezone, start/end, recurrence, attendees and notification behavior before approval. `sendUpdates` can email attendees. Client-supplied event IDs can support reconciliation, but Google warns collision detection is not guaranteed; retain action receipts and re-read uncertain outcomes. Recurring instances and their series have different identity semantics. [Event insertion reference](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert?hl=en), [event creation guide](https://developers.google.com/workspace/calendar/api/guides/create-events)

## Notepad: local file connector, not a Notion substitute

Windows Notepad edits text/Markdown files. Implement a user-selected folder/file adapter with canonical-path allowlists, encoding handling, file identity/hash checks and a preview before overwrite. Treat unsaved editor tabs separately; filesystem access cannot be assumed to retrieve unsaved UI content. This is a proposed integration boundary, not a claimed Notepad cloud API. [Microsoft Notepad documentation announcement](https://blogs.windows.com/windows-insider/2025/05/30/text-formatting-in-notepad-begin-rolling-out-to-windows-insiders/)

## GitHub: feasible with narrow repository access

Prefer a GitHub App installed on selected repositories. Permissions start empty and can separately cover Contents, Issues, Pull requests, statuses and deployments, with read/write levels. Editing Actions workflow files needs Workflows permission. User-token operations are additionally bounded by the user's rights. Do not implement “everything” as blanket repository/admin credentials. [GitHub App permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app), [App/OAuth permission comparison](https://docs.github.com/en/enterprise-cloud%40latest/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps)

Separate read/summarize from issue creation, comments, commits, pull requests, merge, workflow dispatch and settings changes. Verify webhook secrets, acknowledge promptly and deduplicate by `X-GitHub-Delivery`; redelivery retains that value. GitHub does not automatically retry failed webhook deliveries, so implement reconciliation and permitted redelivery. [Webhook best practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks), [failed delivery handling](https://docs.github.com/en/webhooks/using-webhooks/handling-failed-webhook-deliveries)

## Acceptance implications

Test account/space separation; revoked credentials; duplicated and missed events; stale sync cursors; changing source content after approval; ambiguous date/time/assignee extraction; untrusted message instructions; rate limits; and timeout-after-commit recovery. A proposed task needs a source link, inferred fields marked as such, and an exact reviewed action payload. Local data controls must describe what is retained in Iron Web versus provider accounts and hosted inference: deleting a local memory cannot retract an already-sent message or guarantee deletion of provider-held copies.
