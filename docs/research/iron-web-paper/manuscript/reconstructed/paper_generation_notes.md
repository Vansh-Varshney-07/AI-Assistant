# Paper generation notes

New manuscript: `Iron_Web_Complete_Research_Paper.docx`. The Markdown sibling is an editable text source; the Word document contains the figure and formatted tables. The accompanying PDF is produced with installed Microsoft Word and inspected after rendering.

## Scope and format

This is the requested complete paper, with all ten numbered sections, an approximately 200-word abstract (200 whitespace-delimited words), three keywords, architecture diagram, two evidence-backed tables, numbered references, and a reproducibility appendix. It is an architecture and implementation study with preliminary engineering validation. Body text is 15-point Times New Roman, retaining the earlier request for 1.5-times editing text. References and tables are 12 point. The latest complete-manuscript structure takes precedence over forcing the expanded editing copy into the earlier nine-page layout. This is an editing manuscript, not a claim of conformance to a specific IEEE conference template.

Original backup remains untouched at `../Iron_Web_Research_Paper_9_Page_Editing_Draft.docx`; SHA-256 `a47c2819f40da69d200cfe027763785ed0487cb70972f8f252517de30ea0c33f`. No application implementation was changed for this revision. Existing unrelated working-tree changes were preserved.

## Missing evidence and provisional material

- No eligible controlled head-to-head public benchmark, held-out conversational experiment, matched graph ablation, or causal reliability effect size is available.
- Full historical resolved configurations, seeds/repetition policies, reader token budgets, and provider/hardware manifests are missing. The declared GPU is user-reported.
- Named `regression.xml`, `startup-memory-tests.xml`, `phase02-tests.xml`, `real-embedding-smoke.json`, and `memory-spaces-live-evidence.json` are absent from the accessible project. `.local/tests-relocation-20261024` was inaccessible in the audit.
- Shared-service context/work execution is implemented but is not exercised by retained hosted runs. End-to-end stale acceptance and false-block rates remain Not measured.
- Storage scaling, robust tail latency, full token/cost accounting, crash coverage, and adversarial behavior remain unmeasured.
- R3 includes an incompatible copied CSV and stale report. The negative partial JSON is retained; the copied summary is excluded from quantitative attribution.
- Proposed comparisons in Methodology and Future Work are explicitly unexecuted. Author, affiliation, email, funding and acknowledgment fields are editable metadata requiring the authors' completion. No invented results or unfinished result placeholders occur.
- A sanitized public artifact package has not been released. The internal report reference points to real local artifacts, not a peer-reviewed public publication.

## Citation verification

All twelve entries were checked against primary publication/version records, official standards, author-institution metadata, or actual local artifacts. No critical citation identity check remains unresolved. Verification scope is recorded individually in `reference_verification.json`. The author-hosted full text of the 1986 temporal-database paper timed out; only the verified institutional metadata/abstract supports the general temporal-dimension precedent. Hindsight is cited only for its documented conceptual distinction, not an unverified numerical result. Zep's official record and supplied v1 PDF were used when its versioned web record did not load. Preprint versions retain their actual version years rather than inventing conference pages.

## Rebuilding and rendering

Run `build_complete_paper.py` with the bundled dependency Python; it imports only document/data libraries and the pure manuscript-content module. It verifies all 202 audited file hashes before building. It must not import the earlier `build_manuscript.py`, which writes the original draft at import time. The document skill's standard renderer requires LibreOffice, unavailable on this host; installed Word provides local PDF export via `render_with_word.ps1`. PDF pages are rasterized with PDFium for visual inspection. Rendering uses no inference service and opens no memory store.

The paragraph-level mapping and table source records remain in `paper_claim_map.json`. Final page count, checks, hashes, and render inspection are recorded in `generation_manifest.json`.

## Final document verification

The final Word export has **nine pages**. All nine rendered pages were visually inspected. Every mapped body paragraph survives PDF extraction; both tables match the audited source values, all twelve references follow first-citation order, and the original draft hash remains unchanged.
