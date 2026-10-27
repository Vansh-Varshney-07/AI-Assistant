# Wayfinder 0.4.1: try the connected app

Quit the older Wayfinder build, then open `Wayfinder-0.4.1-Windows-x64.exe`.
Keep Docker Desktop and your existing managed Hermes/OpenShell runtime running.
The backend and CPU memory model are bundled; a development checkout or Python environment is not needed.

Your existing Google, Tavily and Notion credentials have already been imported into the normal app profile and encrypted for your Windows account. Original `.env` and token files were preserved. No credentials are inside this executable.

1. If first-run setup appears, verify memory, database and the displayed NVIDIA model; give chat consent and create your workspace.
2. Open Connections and run the Google, Tavily and Notion live checks. Imported and live-verified badges are separate; checks reset after restart.
3. Read Calendar/Tasks/Gmail, select Drive/Contacts, or search Tavily/Notion. Open one shared Notion page explicitly. Docs/Sheets inspection requires an accessible exact ID and shows metadata only.
4. Restart and confirm connections remain imported. Disconnect removes that local connection; importing your local `.env` reconnects it. No account write, message send or automatic memory publication occurs.

Generative inference is restricted to NVIDIA Nemotron Lightning and Ultra. Account reads are not automatically supplied to chat. Scheduling, fitness and W37 are unavailable. These are hidden app/runtime checks; native mouse, Windows dialogs and file-picker interaction were not tested.

Verification: 51 desktop tests, 44 connection/source contract checks, 304 broader backend regression tests, 35 packaged-app checks, 11 portable-launcher checks and 15 live API checks passed. One existing opt-in backend test was skipped.
