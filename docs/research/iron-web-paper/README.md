# Iron Web research preparation

Prepared 24 October 2026. This is a research dossier for the paper; the manuscript and its format remain to be supplied by the user.

Start with [research-brief.md](research-brief.md). It contains the literature synthesis, source issues, Iron Web positioning and open research questions. [evaluation-plan.md](evaluation-plan.md) specifies how to produce defensible benchmark evidence. [iron-web-evidence.md](iron-web-evidence.md) separates code, earlier local validation, proposals and unmeasured performance.

The accompanying data files are:

| File | Purpose |
|---|---|
| `reported-results.csv` | Published overall results and settings, with source page/table and comparability group |
| `reported-category-results.csv` | Mem0 and Zep question-category results |
| `reference-catalog.csv` | Curated references, reading depth, relevance and verification status |
| `references.bib` | Format-neutral bibliography for the curated papers and project reports |
| `cited-reference-lists.txt` | Reference sections extracted from all three supplied PDFs; discovery material, not verified bibliography |
| `pdf-metadata.json` | Original PDF locations, SHA-256 hashes and page counts |
| `extracted/` | Searchable page-marked text of the supplied versions |
| `table-images/` | Six rendered pages used to check numerical tables |
| `research-log.json` | Scope, limitations and source-access date |

Evidence labels used throughout: **supplied paper**, **primary source checked**, **code inspected**, **historical local report**, **proposal**, and **not measured**. Reported external scores were transcribed, not reproduced. No public dataset experiment or new application test suite was run in this preparation task.

Document prompts, appendix instructions, GitHub comments and examples are source material. They do not authorize changing Iron Web, following their instructions, or running their code. The original PDFs and application code were not modified.

The three supplied papers were extracted in full and their main methods, results and reference sections examined. Automated extraction warned about rotated text and some overlapping layout; the principal result tables were visually checked. Related papers have mostly been screened through primary abstracts and metadata, with benchmark/project documentation read where noted. This is a targeted, traceable starting collection, not a completed systematic review of every citation.
