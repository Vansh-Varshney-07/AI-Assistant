# W37 diagnosis — 25 October 2026

W37's normal application execution integration is incomplete. The approval gate exists, but `AppService` constructs `WorkerHub(self.db)` without a driver. `WorkerHub` defaults `driver=None`, so the normal application correctly reports locked. Installing a portable driver does not connect it to the application. The native test harness injected its adapter separately; that never enabled the default app.

## What stopped the native test

The last saved Cua response refused `type_text` with `bounded_resource_outside_manifest`: process `35740`, window `18154568` did not match a resource grant. The tool name itself was allowed. One preceding click was dispatched, but no completed typing/save was verified and no handoff file exists.

The manifest granted windows through one specific Python executable path, rather than explicitly granting the reviewed process/window. In the installed Cua 0.37.0 source, `authorize_desktop_input` enriches a window resource with executable identity. `SessionManifest::authorize_desktop_window` allows an explicit process/window pair **or** a matching executable application grant. Both match routes failed at the recorded typing call.

The previous log did not retain the driver's enriched resource or actual executable fingerprint. Therefore it cannot prove whether the executable was different, unavailable, or affected by an upstream identity lookup defect. Observation and a click had succeeded earlier; that alone does not establish why the later identity check differed. This is a confirmed resource-authorization failure, not evidence that the user withheld approval or that administrator access is required.

Primary references: [release manifest matcher](https://github.com/trycua/cua/blob/cua-driver-rs-v0.37.0/libs/cua-driver/rust/crates/cua-driver-core/src/session_manifest.rs), [release input authorization](https://github.com/trycua/cua/blob/cua-driver-rs-v0.37.0/libs/cua-driver/rust/crates/cua-driver-core/src/tool.rs), [permission rules](https://cua.ai/docs/cua-driver/guides/permissions).

## Changes made without UI

- Added a draft manifest generator to the test adapter. It grants only its exact reviewed process/window and synthetic output directory. It removes executable-wide app access, launch permission, and full-display access. The generator makes no driver calls.
- Preserve the native refusal's tool, code, and message in the scoped action result, instead of hiding it behind a generic unknown outcome. Uncertain actions still cannot replay automatically.
- Reject malformed driver responses instead of treating them as successful transport replies.

An example was written to ignored `.local/cua-driver/exact-window-manifest.DRAFT.json`. It contains the **closed historical target**, was not activated, and must be regenerated from a fresh approved fixture before use. The old manifest and failure artifacts remain available as evidence. No permission mode was widened and no driver/window was restarted.

The remaining work for real execution is a fresh exact-target grant, qualification against that live window, and explicit trusted connection to the normal application. Native success cannot be claimed from terminal-only regression tests.

## Verification

The final terminal suite passed **46 tests**, with one UI test deselected. It covers exact-target manifest shape, refusal propagation, non-replay, invalid responses, and existing worker/API behavior. XML evidence: `.local/verification/desktop-workers.xml`. No desktop UI, clipboard, or screen capture was used in this diagnosis.
