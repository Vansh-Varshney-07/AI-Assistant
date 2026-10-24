# Nemotron workbench repairs and validation

Date: 23 October 2026. Target: `D:\Opencode_\memory_system`.

The requested models are exactly:

- `nvidia/nemotron-3.5-lightning-30b-a3b`
- `nvidia/nemotron-3-ultra-550b-a55b`

Both were verified against the authenticated NVIDIA model catalog and called through the existing NVIDIA account. No credential is included in these documents. Only explicitly labelled synthetic testing namespaces were used for live validation.

## Start and use

The delivered dashboard is running at http://127.0.0.1:3352. Stop its current process with **Stop workbench** before starting another owner of embedded Qdrant.

```powershell
Set-Location 'D:\Opencode_\memory_system'
docker compose up -d --pull never falkordb
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\workbench_server.py --nvidia --key-file 'D:\Opencode_\reserchpaper\.env'
```

The key can instead be supplied through `NVIDIA_API_KEY`, omitting `--key-file`. Only that credential is read from the optional existing file. Without `--nvidia`, the original evidence-only mode remains available and makes no hosted calls. The existing virtual environment is reused.

Select either exact model in **Response / extraction model**. Use **Store prompt + retrieve first** to submit raw source text: when a model is selected it first extracts validated claims and writes them through the existing engine. Check the user-source confirmation box when intentionally asserting accepted facts; corrections require confirmation. Writes show actual storage receipts and claims. Use **Retrieve only** for questions: the selected model generates an answer from actual engine evidence with separate, validated source-citation buttons. **Recall a declared field** is available for explicit field tests. Fresh conversation preserves durable records.

Selected-model prompt text, scoped field vocabulary and relevant evidence are sent to NVIDIA. BGE embeddings, FalkorDB and Qdrant stay local. No external application, new database, embedding model or reranker was connected or substituted.

## Reproduced failures and repairs

| Failure observed | Repair |
| --- | --- |
| Earlier model returned narrative/code instead of the required JSON | Nemotron JSON-schema constrained decoding with thinking disabled for structured output. Whole-object parsing, duplicate-key/nonfinite rejection, completion checks, local validation and at most one repair attempt. Embedded JSON examples inside prose are rejected. |
| Model extracted routing namespace as a fact | Each extracted claim requires a nonempty verbatim quote from the user source; execution metadata cannot supply that quote. Source text and execution context are separated. |
| Inconsistent attribute names prevented conflicts and changes | Extraction sees the actual existing scoped field catalog, reuses existing predicates, and cannot apply a change to an unknown field. No fuzzy renaming of accepted evidence is performed. |
| Preference assigned wrong kind; reschedule retained old current claim | Enum-constrained claim kinds/actions and validation that explicit preference/rescheduling evidence is represented with the corresponding existing lifecycle contract. No replacement value is hardcoded. |
| Unrelated disputed memories contaminated a query's status | Model selects existing field names only, then the adapter calls the engine's existing exact `recall()` API. Original semantic candidates remain visible separately. Answer generation uses current field evidence. |
| Model omitted or invented source identifiers | Answer schema constrains citations to actual returned memory IDs and preserves the engine evidence status. Disputes require citations to both sides. The UI renders separate source buttons rather than depending on IDs embedded in prose. |
| NVIDIA rejected JSON-schema `uniqueItems` | Removed this unsupported grammar keyword; local validation/deduplication remains. The actual sanitized HTTP 400 explained the failure. A regression test protects this compatibility boundary. |
| A retry could produce different extraction for the same source event | Stored extraction/model/request digest in the existing source metadata. An identical retry replays the same immutable write without another model call; changed input under the same request ID is rejected. |
| Every request inspected unrelated namespaces | Source inspection for execution is limited to the selected namespace. Full unfiltered inventory remains available. Unrelated-record failures no longer block a selected namespace. |
| Browser rounded the INT64 validity sentinel | Large integers are represented as decimal strings on the HTTP wire; stored Python/backend values remain exact. Manual browser JSON rejects unsafe integers instead of rounding them silently. |

Extraction and routing are model-assisted adapters over the existing engine. They do not replace its ranking, temporal rules, graph publication, compensation, source immutability or correction algorithm. The actual extraction attempts, claims, routed fields, memory IDs, generated responses and timings are recorded in the live evidence.

## Validation evidence

`nemotron-report.md`, `nemotron-results.csv`, `nemotron-evidence.json` and `nemotron-records.json` record the latest complete two-model run. Each model receives the eight original scenarios plus a duplicate-event replay check. Every question has a new session ID and no conversation history. Corrections, conflicts and date changes are checked against actual stored claims and current recall; persistence restarts the actual server process using the same stores. Values supplied to the models are source prompts and stored evidence, not expected answers.

Earlier runs are preserved in `docs/nemotron-validation-before-schema/` and `docs/nemotron-validation-schema-rejected/`. Their stored namespaces remain retained and clearly distinct from the final run. These records are deliberate evidence of the failures encountered, not production facts.

Reproduce the live comparison, with the workbench running:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' .\scripts\validate_nemotron.py
```

This creates new test namespaces, makes real NVIDIA requests and cleanly restarts the server twice. It preserves test records. The default report directory is `docs/nemotron-validation`; copy it before another run if preserving an earlier report. Its test namespace IDs are always unique.

Run architecture and focused regressions:

```powershell
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest -q
& 'D:\Opencode_\reserchpaper\.venv\Scripts\python.exe' -m pytest tests/test_hosted_boundaries.py tests/test_hosted_routing.py tests/test_workbench.py -q
```

The ordinary suite uses deterministic test embeddings and real isolated test storage. The separate live comparison uses the real cached BGE model, real persistent stores and actual NVIDIA inference. These are different forms of evidence and are reported separately.

## Files and reversibility

Added `memory/shared/hosted.py`, `tests/test_hosted_boundaries.py`, `tests/test_hosted_routing.py`, `scripts/validate_nemotron.py`, and this report. Modified the existing optional hosted interpreter, shared-service interpretation context, workbench adapter/server, HTML and JavaScript. README and the manual guide point to the new startup procedure. Pre-repair copies of modified code are under ignored `data/repair_backup_20261023/`. No original memory records were deleted, no destructive migration was run, and no key file was modified.

## Operational limits

Provider outages, quota/rate limits and a semantically incorrect model response can still occur. Validation rejects malformed/unacceptable output without a semantic write and reports the failed stage. The source quote prevents unsupported metadata extraction but is not a mathematical proof that every extracted value is true. Passing scenarios establish the observed behavior, not that future failures are impossible. The UI is loopback-only and makes no production-security claim. The default unconfigured evidence-only path still does not interpret arbitrary free text into semantic claims; use an explicitly selected enabled model for that capability.

## Provider references

The exact hosted IDs and template settings were checked against NVIDIA's model pages and documentation: [Nemotron Lightning](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b), [Nemotron Ultra deployment/reference](https://docs.nvidia.com/nim/large-language-models/2.0.6/day-0/get-started-nemotron-3-ultra.html), and [Ultra structured-output limitations](https://docs.nvidia.com/dynamo/v1.5.1/recipes/nemotron-3-ultra). The authenticated API catalog and live requests remain the evidence of account-specific availability.
