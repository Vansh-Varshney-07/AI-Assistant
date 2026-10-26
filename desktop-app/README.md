# Wayfinder desktop · 0.3.0

The GitHub UI, existing scoped backend and consolidated task-profile layer share one application runtime. [How to test](../docs/platform/TESTING-APP.md) · [current implementation/results](../docs/platform/CONSOLIDATED-IMPLEMENTATION.md).

From the current checkout root, `Start-Wayfinder.ps1 -Demo` launches the new UI with synthetic input, an isolated app profile/runtime and disposable database. Keep the terminal open until you quit. This does not reset normal Iron Web data. `Test-Wayfinder.ps1` runs terminal/headless regression by default; additional modes are documented in the guide.

M00 routes tasks; eight profiles and six app presets are versioned metadata. A01/A05/A06 have the selected UTF-8 file variant via one existing W35/Hermes job. A07 opens the existing Memory view. No new agent loop, scheduler or memory engine was added. Account-backed presets, broad development execution, full forgetting and ordinary general chat remain unqualified. W37 and Fitness stay disabled.

The unsigned Windows development folder is `release/win-unpacked`; keep it intact. It requires this source checkout, compatible existing Python, FalkorDB/cached embeddings and the managed Hermes setup for tasks. No runtime data or credentials are copied or installed automatically. Google OAuth helper dependencies are prepared locally, while Desktop client/consent remain human steps. Codex account connections are not Wayfinder product authorization.
