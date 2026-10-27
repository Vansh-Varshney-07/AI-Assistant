"""Reuse Atlas search, then intersect candidates with installed evidence and handlers."""

from wayfinder.atlas.indexing.retrieval import _keyword_search_jsonl

FILE_ANALYST = "wayfinder.files.analyze"


class CapabilityCatalog:
    def __init__(self, inspector, search=_keyword_search_jsonl):
        self.inspector, self.searcher = inspector, search

    def search(self, query):
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 1000:
            raise ValueError("Capability query requires 1–1000 characters.")
        qualified = bool(self.inspector.current().get("compatible"))
        rows = []
        for candidate in self.searcher(query, top_k=20):
            supported = candidate.id == FILE_ANALYST
            rows.append(
                dict(
                    tool_id=candidate.id,
                    name=candidate.name,
                    score=candidate.score,
                    schema_version="wayfinder.api/v2" if supported else None,
                    metadata_status=candidate.status,
                    discovered=True,
                    configured=supported,
                    qualified=supported and qualified,
                    available=supported and qualified,
                    reason=(
                        'Existing W35 handler; current isolated runtime inspection passed. A fresh scoped grant and disclosure are still required.'
                        if supported and qualified else
                        'Inspect the installed isolated Hermes binding before analysis.'
                        if supported else
                        'Atlas metadata has no qualified application handler for this operation.'
                    ),
                    availability="runtime_qualified"
                    if supported and qualified
                    else "unqualified",
                    configuration="existing_w35_binding"
                    if supported
                    else "no_qualified_binding",
                    required_permissions=[
                        "orchestrator",
                        "owner_space_task",
                        "read_only_file_grant",
                        "fresh_memory_context",
                    ]
                    if supported
                    else [],
                    executable=False,  # Discovery never grants authorization.
                )
            )
        return rows

    def select_read_only(self, query):
        candidates = self.search(query)
        selected = next(
            (row for row in candidates if row["tool_id"] == FILE_ANALYST), None
        )
        if not selected or selected["availability"] != "runtime_qualified":
            raise ValueError(
                "Atlas has no qualified handler for this read-only workflow."
            )
        return selected
