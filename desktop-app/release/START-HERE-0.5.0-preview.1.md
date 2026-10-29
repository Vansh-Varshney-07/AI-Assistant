# Wayfinder 0.5.0-preview.1

Open `Wayfinder-0.5.0-preview.1-Windows-x64.exe` directly. It includes its Python backend and CPU memory model. Docker Desktop with a local Linux engine and the existing managed Hermes/OpenShell installation are still prerequisites.

This is the first rebuild checkpoint. It improves onboarding, chat formatting and reliability, colors/icons, connection-check expiry and per-turn execution isolation. Existing selected-document, memory, manual connection-read and local Git services remain available behind their existing permissions. Broader agent routing, provider task presets and the general workflow builder are still unfinished; an unqualified card cannot run a fallback task.

For a fresh profile, complete the three setup steps, review the exact displayed model, and create a space. Google, Notion and Tavily connections are optional. Start a chat from Home. Existing valid setup resumes through the same application profile.

Verified results: 64 frontend tests; 321 backend regression tests (one live test skipped, one native UI test excluded); 29 overlapping targeted contract/profile/chat checks; nine headless UI scenarios; 18 real packaged setup/chat/restart checks; and 11 checks on this portable EXE. All 3,007 extracted backend/source/model files matched staging.

Tests used synthetic data and isolated hidden profiles. Screenshots captured Wayfinder's own renderer. No Cedar window, OS mouse/keyboard input, clipboard read, whole-desktop capture or W37 action was used. Real chat tests used the configured approved Hermes model; provider-backed account tasks were not activated.

SHA-256: `f0e9f3643ab8ab7b7be98e80f766d3b08bedf754ee4b18b15e91565fec280b00`. The portable executable is unsigned. Its matching checksum and verification JSON are alongside it. Full phase status is in `docs/platform/REBUILD-CHECKPOINT-01.md` and the rebuild task ledger.
