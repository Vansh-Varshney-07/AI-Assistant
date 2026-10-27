# Wayfinder desktop: revised delivery plan

Revision 4 · 26 October 2026 · design and offline checks only

Start with [PLAN.md](PLAN.md). This revision supersedes the v3 **desktop proposal**, not the existing backend, memory-quality contract or worker contracts. The earlier [stress review](../wayfinder-desktop-v3/audit/REPORT.md) remains an unchanged baseline.

This redesign is being checked in five cumulative batches. A finding can be addressed in the plan while implementation and live qualification remain unproved. No runtime/account/UI test is implied by these files.

- [Authoritative proposed contracts](CONTRACTS.md).
- [Release/capability manifest](manifest.json).
- [Finding-by-finding amendments](REMEDIATIONS.md) and [machine-readable ledger](REMEDIATIONS.csv).
- [New risks introduced by amendments](SECOND-ORDER.md).
- [Cumulative review record](review/REVIEW.md).
- [Offline preview](preview.html), [flowcharts](FLOWS.md), [acceptance cases](ACCEPTANCE.csv), [worker coverage](WORKER-SURFACES.md).

Only this new design directory is changed. No dependency installation, Git operation, account connection, background job, backend change, native automation or app launch is part of this redesign.
