# Fitness, Tavily and Windows companion feasibility

Verified against public primary documentation on 24 October 2026. This is planning research; no accounts, real health records, installation or desktop capture were used. Research is kept as local assets because this working folder has no Git repository; there is no research branch or push.

## Scope and decision

Target Windows and local storage first. The animal popup can host chat, approvals, reminders and workflow status. **Desktop scanning and screen capture were explicitly removed from this plan by the user.**

Build fitness summaries behind interchangeable adapters. The user explicitly wants a general system, so define common records, capability discovery and API/mobile/import adapter conformance first; do not hardwire the product to one chosen app or promise that one desktop connector can read every fitness application. Add Tavily as a separately permissioned remote web research adapter. The native overlay is a presentation client, with no independent memory access.

## Fitness access paths

### Android Health Connect

Health Connect is an Android on-device store, not a general cloud endpoint for a Windows program. It requires Android 9 or later with Google Play services; Android 14 includes it in the system, whereas earlier supported versions use the Health Connect application. Work profiles are not supported. **Design implication:** a direct Health Connect integration needs an Android companion/bridge that reads only approved types and pairs with the Windows service. Existing applications must actually supply the relevant records; installing the bridge does not recover arbitrary vendor-private data. [Availability](https://developer.android.com/health-and-fitness/health-connect/availability), [SDK setup](https://developer.android.com/health-and-fitness/health-connect/get-started)

The normal cross-application history window is 30 days before permission grant, with extra permission needed for older history. Background reads require an additional grant. The official reading guide recommends aggregation for cumulative types such as steps to avoid double counting multiple sources. **Plan:** request read-only steps, workouts and optionally sleep first; keep permissions by metric, use source-aware aggregation, and record sync coverage and gaps. Do not treat a week with absent data as zero activity. [Reading and history restrictions](https://developer.android.com/health-and-fitness/health-connect/read-data)

### Apple Health / HealthKit

HealthKit exposes fine-grained, per-type read/write authorization in an Apple application. A Windows-only process cannot substitute for that on-device integration. Apple documents that an application cannot distinguish denied reading from full access through read-authorization status, and users can limit access to recent history. **Plan:** an Apple-device bridge or explicit export/import, read-only requests, and a visible “data unavailable or incomplete” state. Never infer “no workouts happened” from an empty query. [HealthKit authorization](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data), [HealthKit capability configuration](https://developer.apple.com/documentation/xcode/configuring-healthkit-access)

### Google Fit, Google Health, and vendors

Do not start a new Google Fit connector: Google says new registrations stopped on 1 May 2024 and Fit APIs are being deprecated in 2026. It recommends Health Connect for mobile-first Android and Google Health API for cloud integrations. [Google Fit overview](https://developers.google.com/fit/overview)

Google Health is a candidate cloud-adapter path, but exact migration dates and project eligibility need implementation-time verification. **Verification discrepancy:** the research attempt reported an onboarding restriction and migration notices, while the parent agent's independent current fetch of the homepage displayed new-developer codelabs and did not show those restrictions. The bundle therefore does not assert that onboarding is universally closed or give a verified shutdown date. Validate the actual developer project, permissions and current migration guide before promising an adapter. [Google Health homepage](https://developers.google.com/health), [Google Health overview](https://developers.google.com/health/about)

Vendor access varies. Garmin currently documents personal access to one's own data using a personal API key and pull requests, while business access has application/tier constraints; Starter lacks historical data. Samsung Health Data SDK operates through the Android Samsung Health app and requires compatible versions and a real device; it does not support emulators. **Design implication:** each adapter advertises its verified provider/device capabilities and onboarding requirements; prefer official APIs over password/session scraping. The general SDK does not require choosing one user's device as its architecture. [Garmin program](https://developer.garmin.com/gc-developer-program/overview/), [Samsung Health Data SDK](https://developer.samsung.com/health/data/overview.html)

### Weekly summary contract

Recommended output: period and timezone, available days, recorded steps, workout count/duration, optional sleep aggregates, comparison with the user's own stated goal, source links/IDs, and gaps. Use deterministic arithmetic before asking a model to explain it. Keep normalization versions and source record IDs so a reimport or late sync does not double count. Clearly distinguish measurements, user-entered goals and generated prose. This is product design, not an API guarantee.

The initial worker should summarize fitness and wellness observations, without diagnosing conditions, proposing treatment or interpreting an isolated health measurement as a medical finding. Samsung explicitly restricts its SDK data to fitness/wellness rather than diagnosis/treatment. [Samsung usage restriction](https://developer.samsung.com/health/data/overview.html)

The bridge/import adapter writes a controlled ingestion queue. The orchestrator approves retention in Iron Web and sends the fitness worker a task-specific packet. Raw timeseries should remain in a structured local health-data area; Iron Web can retain approved goals, provenance and weekly summaries. Health records must not automatically appear in work-email or GitHub context.

## Tavily capability boundary

Register separate operations rather than a broad “browser” permission:

| Capability | Actual purpose | Suggested metadata |
|---|---|---|
| Search | Discover current relevant sources | `web.search`, remote, read |
| Extract | Read content from specified URLs | `web.extract`, remote, read |
| Crawl | Follow links and extract multiple pages | `web.crawl`, remote, read, bounded pages/depth |
| Map | Discover URLs/site structure | `web.map`, remote, read |

The official endpoints describe these distinct operations and offer domains, paths, limits or extraction controls as appropriate. [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search), [Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract), [Crawl](https://docs.tavily.com/documentation/api-reference/endpoint/crawl), [Map](https://docs.tavily.com/documentation/api-reference/endpoint/map)

These documented APIs are a research/content layer. They do not constitute an interactive browser session for signing into an account, clicking application buttons or submitting forms. That would require a separately authorized browser automation adapter, outside the current Tavily capability. This distinction is inferred from the documented API contracts, not a claim that all interactive sites can be extracted successfully. [Tavily overview](https://docs.tavily.com/)

Tavily requests transmit queries/URLs to a remote provider. Treat that as a distinct egress grant: strip personal/health secrets, constrain domains and crawl limits, enforce credit/time budgets, and return cited material as untrusted evidence. Credits differ by operation/depth; crawling combines mapping and extraction costs. Do not let vector similarity alone authorize a matching tool. Similarity proposes candidates; policy, scopes and the user's approval grant determine execution. [Credits](https://docs.tavily.com/documentation/api-credits)

## Windows animal popup

A small native Windows companion is feasible. Windows App SDK exposes top-level window sizing/positioning and always-on-top behavior. Multiple always-on-top windows can still overlap according to activation; do not promise the pet always appears above every surface. The illustrated animal is UI content, not a new privileged agent. [Windowing overview](https://learn.microsoft.com/en-us/windows/apps/develop/ui/windowing-overview), [Always-on-top behavior](https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.windowing.overlappedpresenter.isalwaysontop?view=windows-app-sdk-1.8)

Recommended controls: expand chat, show active space, review proposed action, approve once, approve narrowly scoped recurring job, revoke, pause jobs, dismiss/minimize, and quit. Keep approvals in a normal readable panel rather than requiring interaction with a tiny animal. Native client sends requests to the local orchestrator broker; workers receive neither Iron Web credentials nor arbitrary local API access.

## Acceptance gates before building these integrations

1. Prove the provider-neutral contract with multiple synthetic provider shapes and an import path; certify each real provider/phone bridge separately, including deletion/reimport behavior, before advertising its coverage.
2. Demonstrate weekly arithmetic with missing days, overlapping sources, revoked access, late updates and timezone changes.
3. Demonstrate Tavily budget limits, blocked sensitive queries, untrusted page instructions and a no-match tool request.
4. Demonstrate popup approval rejection/expiry/revocation and a recurring job whose grant cannot expand its data, destination or operation.
5. Keep desktop scanning/capture absent from this effort.
