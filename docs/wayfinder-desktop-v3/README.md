# Wayfinder desktop design package

Start with [PLAN.md](PLAN.md). This is a new phased design proposal requested on 26 October 2026, not an implemented desktop release.

- [Interactive offline preview](preview.html): switch proposed releases R1–R7, navigate their planned surfaces and inspect plan/source/review examples. It issues no network request, stores no data and invokes no runtime.
- [Visual concept](assets/workspace-concept.png), [exact SVG wireframe](assets/workspace.svg), and [release ladder](assets/releases.svg).
- [Mermaid flowcharts](FLOWS.md), [worker coverage](WORKER-SURFACES.md), [acceptance cases](ACCEPTANCE.csv), and [research/decisions](RESEARCH.md).

Validation performed: both SVGs parse; preview JavaScript passes Node syntax checking; local document links resolve; 42 uniquely identified acceptance rows cover R1–R7 and all remain Not run. These are artifact checks, not usability, application, model or backend test results. No Electron application was installed or launched, no backend was changed, and no existing planning files were overwritten.
