# Manuscript claim-to-evidence audit

Scope: complete manuscript revision, 24 October 2026. This report is separate from the paper. Paragraph-level text and evidence keys are retained in `paper_claim_map.json`; bibliography verification is in `reference_verification.json`. Evidence paths are repository-relative unless they name an audit file in the existing research folder. Source inspection is not a new execution.

| Claim / manuscript location | Supporting evidence | Status and limits |
|---|---|---|
| Temporal claim lifecycle and known-time eligibility (3; 4) | `memory/lifecycle/models.py`, `memory/lifecycle/service.py`; implementation audit | Implemented. Eligibility is represented policy, not verified truth; correction is not ordinary historical supersession. |
| Four distinct entry paths (Fig. 1) | Engine, workbench, shared service, Wayfinder; implementation audit | Diagram is an implementation map. Hosted live runs do not exercise the shared context/work service. |
| Scoped context proofs, post-generation check, dependent-work traversal (4; 7.2) | `memory/context/access.py`, `memory/shared/client.py`, lifecycle invalidation/handoff; targeted test source | Implemented with precise regression assertions. End-to-end stale acceptance Not measured; no guarantee for external side effects. |
| Vector reconciliation and confounded ablations (7.2; 8) | Vector/hybrid retrievers and engine mode dispatch | No raw dense, fully graph-free, or fully temporal-free baseline is established by those labels. |
| Defaults and hardware (5) | `config.yaml`, config/engine/shared constructors; audited environment metadata | CPU defaults and configured models are inspected. Historical resolved manifests absent; GPU is user-reported. |
| R1: 11 Pass / 10 Fail / 3 Unsupported (Table 1) | `docs/live-validation/live-test-evidence.json`, reconciled summary | 24 synthetic checks. Mixed paths, correlated outcomes; not benchmark accuracy. |
| R2: 13 Pass / 5 Fail (Table 1) | `docs/nemotron-validation-before-schema/nemotron-evidence.json`, summary | 18 development checks, including correction, extraction, and citation failures. |
| R3: 2 Pass / 6 Fail (Table 1) | `docs/nemotron-validation-schema-rejected/nemotron-evidence.json` | Partial eight-check JSON retained. Its copied 18-row CSV is identical to R2; copied summary excluded as R3 evidence. |
| R4: 18 Pass / 0 Fail (Table 1) | `docs/nemotron-validation/nemotron-evidence.json`, summary | Repeated repaired scenarios across two models; not held-out generalization. |
| Timings (Table 2) | R4 event traces; `retained_run_summary.json` | Exact medians recomputed previously; n=13 extraction, n=7 generation/query per model, one replay trace excluded each. Repair included; no cost or tail-latency claim. |
| External methods (2) | Versioned primary papers and standards listed in reference verification | Conceptual comparison only. No heterogeneous leaderboard; no claim that an undocumented feature is absent. |
| Storage coordination and recovery (4; 9) | `memory/storage.py`, journal/snapshot code, audited historical recovery records | Compensation is not a transaction spanning all stores; recovery metadata constrains broad durability claims. |
| Source identity and reproducibility (Appendix A) | Base commit plus 202-file hash manifest and 833-symbol index | All 202 hashes rechecked unchanged while generating this revision. Historical runtimes remain incompletely reproducible. |

## Claims deliberately removed or weakened

- The illustrative 98% accuracy and claims of superiority have no experiment behind them and are omitted.
- Unit-test pass counts are not memory accuracy. Historical suite totals overlap and are not summed or promoted to a headline result.
- Perfect historical recall, universal contradiction detection, complete stale-work protection, calibrated truth probabilities, atomic multi-store writes, complete erasure, adversarial isolation, and lower token cost are not asserted.
- Graph expansion and fuzzy scoring are implemented, but their incremental utility is Not measured.
- Copied R3 summaries and unexecuted planned benchmark cases are not counted as completed observations.
- Current source is not treated as the exact source revision for every historical trace.

## Checks performed for this revision

The original DOCX hash is unchanged. Citation numbering follows first appearance and every bibliography entry is cited. Table 1 is populated from JSON outcomes, retaining failures; Table 2 is populated from the audited timing summary. No application code imports, inference APIs, benchmarks, tests, or memory database operations were needed. Document structure, embedded diagram, table cells, text extraction, and rendered pages are checked separately in the generation manifest.
