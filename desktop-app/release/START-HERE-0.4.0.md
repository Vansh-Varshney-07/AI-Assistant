# Wayfinder 0.4 — start here

1. Start Docker Desktop (Linux engine). Your existing managed Hermes/OpenShell installation and model provider are required.
2. Double-click the Wayfinder Windows executable beside this file. Python and the memory model are included.
3. In first-run setup: prepare the private database, verify the memory model, and check Hermes.
4. Review the displayed model/provider, enter a workspace name, accept the chat disclosure, and create your workspace.
5. Open Chat → New conversation. Give it a synthetic test code, ask for that code in a second message, then quit and reopen to check history.

Chat does not automatically publish facts to memory. In Memory, try proposing and rejecting a synthetic fact. A stored fact requires a separate exact-change approval.

This is an unsigned local portable build. It preserves a new per-user workspace and an app-owned persistent Docker volume. Existing development data is not migrated or reset. Allow about 1 GB of temporary space for extraction.

Google Calendar/Tasks, Gmail, Notion, hosted GitHub actions, fitness, scheduling and native desktop actions are not qualified in this release. W37, desktop capture and clipboard access remain disabled.

Verification passed: 304 backend fixture tests; 44 frontend tests; 18 actual packaged app/Hermes/history/restart checks; 9 actual portable-launcher checks; 29 package-integrity checks. One backend test was skipped and one native UI test excluded.
