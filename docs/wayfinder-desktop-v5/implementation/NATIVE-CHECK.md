# Proposed visible app-only acceptance check

**Outcome:** the user approved this bounded check on 26 October 2026. It stopped before any click, typing or native-dialog interaction: after an initial app-approval timeout, the helper returned content from outside the selected Wayfinder window. That content was not used for actions or saved into the project. The isolated app process and dedicated database were cleaned up. Native acceptance remains blocked by unreliable target capture; W37 remains disabled. The original proposal below is retained as the approved scope, not as evidence that its steps passed.

This check is prepared, **not authorized or run** under the current terminal-only constraint. It uses the existing 0.2.0 packaged Wayfinder app; no Cedar, W37 driver, software install or permission expansion is part of it.

1. Create a uniquely named disposable FalkorDB instance, synthetic runtime/profile and one small UTF-8 file. Launch only this package against those explicit test resources.
2. Show Wayfinder's own window. Any permitted snapshots cover that app and its child dialogs only; no full-desktop capture or unrelated app inspection.
3. Create a synthetic space. Open the document picker, select the generated file and inspect the bounded selection. Do not dispatch model analysis or read any other file. Revoke the selection and verify access is denied.
4. Propose `me.retention_days = 30` with a synthetic source statement. Open the trusted exact-change dialog, inspect its parameters and click Cancel. Verify rejected status and missing recall.
5. Make a fresh, identical synthetic proposal. Open its trusted dialog, approve once, and verify the service's completed receipt and recalled value 30. The effect is confined to disposable test storage.
6. Check keyboard access, Escape and focus restoration on the app's own dialogs; record what was actually observed. Do not claim a screen-reader/real-DPI/Git/native-desktop qualification from these checks.
7. Quit the test app, observe owned-process cleanup, and remove only the uniquely named test container. Keep redacted evidence and synthetic files in ignored test storage.

No Gmail/calendar/task account, external send/write, native desktop action, clipboard, shared runtime or original project state is used. Approval of this proposal would authorize only these app-only test interactions and app-window snapshots; W37 remains disabled.
