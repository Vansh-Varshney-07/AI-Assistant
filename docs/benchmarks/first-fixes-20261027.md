# First benchmark fixes, 27 October 2026

Implemented reader context/prompt changes and a fresh conversation-scoped DMR
path. Existing result directories and application defaults remain historical
artifacts. No new public benchmark improvement is claimed.

## DMR findings and repair

The retained 100-question DMR cohort has 500 session documents. All 100 gold
IDs point to session 4. The originating converter,
`D:/Opencode_/reserchpaper/scripts/build_dmr_benchmark.py`, constructs each
query's gold ID using `session_index` after its document loop. This selects
the final session without examining the question's evidence. All gold IDs
exist in the corpus, so this is an annotation-construction problem rather
than a missing-ID problem.

Of 1,000 archived top-10 results per condition, 905 vector results and 865
hybrid/reranked results belong to another conversation. These counts describe
the retained outputs, not a fresh retrieval experiment.

`scripts/benchmark_data.py` now adapts the raw MSC JSONL directly. It separates
question/answer text from history, preserves each session, and never invents
gold evidence from the last session. Reviewed annotations can be supplied with
the source SHA-256, reviewer, rationale, and explicit document IDs. References
to another conversation or source revision fail validation. Unannotated
questions can be retrieved but their evidence metrics stay null.

`scripts/run_dmr_benchmark.py` runs both vector and hybrid conditions through
the current engine. Each search receives the question's full history document
whitelist **before candidate selection**; gold IDs do not define the scope.
It rejects returned foreign memories, retains retrieval failures, uses a new
isolated store/graph, and records source/configuration/code provenance. The
graph it owns is cleaned up; diagnostic Qdrant files remain in the new output
directory. No extraction or external inference API is used.

Choose question IDs from a separate development split. `dev-ids.json` is an
explicit JSON list such as `["dmr:0100:qa"]`; verify disjointness from the
frozen test cohort before choosing real IDs. Do not derive this list from
observed test performance.

```powershell
# Prepare versioned inputs; do not access models or databases.
& '.local/benchmarks/.venv/Scripts/python.exe' scripts/run_dmr_benchmark.py `
  --source 'D:/Opencode_/reserchpaper/datasets/dmr/msc_self_instruct.jsonl' `
  --case-ids dev-ids.json --output .local/benchmarks/dmr-dev-prepared

# Add --run to execute real retrieval in a NEW output directory.
# Add --evidence reviewed-evidence.json only after evidence review.
```

Reviewed annotation format (the hash must be the actual raw source hash):

```json
{
  "source_sha256": "<sha256>",
  "annotations": {
    "dmr:0100:qa": {
      "document_ids": ["dmr:0100:session:0"],
      "reviewer": "<reviewer>",
      "rationale": "<why this session supports the question's answer>"
    }
  }
}
```

This example is a schema, not a gold annotation. The source A/B fields provide
an answer/question pair, not an explicit evidence label. Validated real gold
annotations still need to be authored/recovered before reporting corrected
DMR recall. The external legacy converter has not been edited.

These DMR conversations contain only five sessions each. After correct
conversation scoping, Recall@5 and Recall@10 are trivial when all sessions are
returned. Record candidate count and emphasize Recall@1/MRR, with reviewed
evidence. A higher scoped Recall@5 alone is not evidence of better ranking.

## Reader replay

`scripts/collect_paper_tables.py` now defaults to:

| Setting | Old protocol | New default |
|---|---|---|
| Retrieved documents | 5, hardcoded | 10, `--top-k-documents` |
| Evidence token cap | 768 | 1,800, `--context-tokens` |
| Prompt | Short-answer prompt already present | `--reader-prompt concise` adds a brief-answer format and dated-evidence rule |
| Output cap | 48 tokens | 48 tokens |

Both retrieval conditions receive identical reader settings. The real reader's
tokenizer enforces the evidence budget. Context still uses equal per-document
shares; long-session truncation remains a limitation. The dated-evidence rule
uses dates only when present; it does not treat retrieval order as chronology.

The complete prompt and top-k now enter checkpoint validation alongside model,
runtime, seed, output cap, source hashes, context cap and exclusions. A new
protocol cannot reuse old generated answers. Legacy caches are accepted only
under matching legacy settings. Tables describe the saved protocol instead of
hardcoding 768 tokens.

To reproduce the original reader settings explicitly, use
`--top-k-documents 5 --context-tokens 768 --reader-prompt legacy`.
For a changed protocol, use a fresh output directory:

```powershell
& '.local/benchmarks/.venv/Scripts/python.exe' scripts/collect_paper_tables.py `
  --run-local-qa --skip-gpu `
  --top-k-documents 10 --context-tokens 1800 --reader-prompt concise `
  --output .local/benchmarks/reader-protocol-v2
```

This command replays the **existing frozen test rankings**; it does not repair
DMR retrieval or provide a development tuning split. Reserve it for a final,
predeclared comparison after development. To attribute effects, use separate
development runs changing top-k, token cap and prompt individually. Do not
interpret `--qa-limit` as a development split: it takes a prefix of the same
frozen cohort.

## Verification and remaining work

- Eight offline adapter tests pass, including source-hash validation, foreign
  evidence rejection, per-condition search scoping, and null unannotated metrics.
- Two offline reader regression tests pass. They exercise paired context
  preparation, top-10 inclusion, token caps, cache resumption without duplicate
  generation, and rejection when reader settings change.
- Collector self-tests pass for paired statistics and missingness.
- The adapter validates all 500 real source questions and 2,500 session
  documents without manufacturing evidence labels. A full collector check
  recomputed all 597 archived records into a separate ignored directory,
  including the new DMR annotation warning; it generated no new answers.
- A real CPU engine test with two conflicting synthetic conversations passed
  both vector and reranked hybrid retrieval; all returned memories stayed in
  the appropriate conversation. These are fixture checks, not benchmark scores.

The current engine already requests 100 vector candidates and reranks the
whole surviving candidate pool. An assumed top-10 reranking ceiling does not
describe this implementation. Keep pool-size experiments separate from these
fixes. BM25/RRF, embedding upgrades, session expansion, hosted readers and real
DMR annotation review are subsequent work.

The installed FastEmbed registry exposes `BAAI/bge-base-en-v1.5` (768 dimensions)
and `BAAI/bge-large-en-v1.5` (1,024 dimensions), but not `BAAI/bge-m3`. Model
changes require a separate compatible store and re-embedding; changing only
the model name while retaining a 384-dimensional collection is insufficient.
