# Memory-space validation

Final automated suite: **204 passed, 3 optional tests deselected** in 136.66 seconds. New space boundary tests: **17 passed**. Ruff and JavaScript syntax checks passed.

Live run: `spaces_1023_133934`. **21/21 passed** with real BGE embeddings and the exact requested Nemotron models. All records retained.

| Check | Result |
|---|---|
| lighta create empty space | Pass |
| lighta dual-store write | Pass |
| lightb create empty space | Pass |
| lightb dual-store write | Pass |
| light same request ID stays separate | Pass |
| spaces_1023_133934_light_a isolated model answer | Pass |
| spaces_1023_133934_light_b isolated model answer | Pass |
| ultraa create empty space | Pass |
| ultraa dual-store write | Pass |
| ultrab create empty space | Pass |
| ultrab dual-store write | Pass |
| ultra same request ID stays separate | Pass |
| spaces_1023_133934_ultra_a isolated model answer | Pass |
| spaces_1023_133934_ultra_b isolated model answer | Pass |
| new ID starts empty after other writes | Pass |
| unscoped inventory fails closed | Pass |
| spaces_1023_133934_light_a survives server restart | Pass |
| spaces_1023_133934_light_b survives server restart | Pass |
| spaces_1023_133934_ultra_a survives server restart | Pass |
| spaces_1023_133934_ultra_b survives server restart | Pass |
| empty space survives restart | Pass |

Automated boundaries covered: invalid/missing/unknown IDs; contradictory facts under the same subject and predicate; semantic retrieval and exact recall; request-ID reuse and local replay; cross-space correction rejection; reserved scope rejection; graph-only source ownership; existing namespace discovery and old receipt replay; persistent empty spaces; concurrent requests; model context exclusion; and HTTP token/scoped inventory rules.

UI checks: created a named space; switched to an existing populated space; asked the same question in A and B and observed only the correct respective test code; returned to My next experiment and observed an empty inventory and cleared displayed evidence. The selected ID also survived browser reload.

The live run includes four model-derived source records across four spaces. Restart checks stopped the actual server cleanly, started it again against the same stores, and verified exact source IDs and empty-space persistence. The separate first-launch report records outbound connection failures from the initial child-process launch; the final documented PowerShell launch completed the passing checks.

See memory-spaces-guide.md for use, API examples, reproduction commands and the remaining authentication/device-sync work.
