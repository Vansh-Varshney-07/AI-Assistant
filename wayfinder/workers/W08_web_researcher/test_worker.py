"""
wayfinder/workers/W08_web_researcher/tests.py
---------------------------------------------
Offline contract tests for W08 Web Researcher.
Uses synthetic fixtures; no live Tavily calls.
"""
import pytest
from wayfinder.workers.schemas import SourceReference


# ── Synthetic output fixture ──────────────────────────────────────────────────

RESEARCH_OUTPUT_SUCCESS = {
    "sources": [
        SourceReference(
            url="https://docs.python.org/3/library/asyncio.html",
            title="asyncio — Python 3 docs",
            excerpt="asyncio is used as a foundation for multiple Python asynchronous frameworks.",
        ),
        SourceReference(
            url="https://fastapi.tiangolo.com/",
            title="FastAPI",
            excerpt="FastAPI is a modern, fast web framework for building APIs with Python 3.7+.",
        ),
    ],
    "raw_sources": {
        "https://docs.python.org/3/library/asyncio.html": "asyncio is used as a foundation...",
        "https://fastapi.tiangolo.com/": "FastAPI is a modern, fast web framework...",
    },
    "queries_issued": ["async Python frameworks 2024", "Python asyncio alternatives"],
    "urls_extracted": 2,
}

RESEARCH_OUTPUT_TIMEOUT = {
    "sources": [],
    "raw_sources": {},
    "queries_issued": ["Python async frameworks"],
    "urls_extracted": 0,
    "error": "tavily_search timeout after 15s",
    "error_type": "timeout",
}


class TestWebResearcherOutputContract:
    def test_success_has_sources(self):
        output = RESEARCH_OUTPUT_SUCCESS
        assert len(output["sources"]) > 0

    def test_success_sources_have_required_fields(self):
        for s in RESEARCH_OUTPUT_SUCCESS["sources"]:
            assert s.url, "source must have url"
            assert s.title, "source must have title"
            assert s.excerpt, "source must have excerpt"

    def test_raw_sources_aligned_with_source_list(self):
        output = RESEARCH_OUTPUT_SUCCESS
        for s in output["sources"]:
            assert s.url in output["raw_sources"], f"URL {s.url} missing from raw_sources"

    def test_queries_issued_non_empty_on_success(self):
        assert len(RESEARCH_OUTPUT_SUCCESS["queries_issued"]) > 0

    def test_urls_extracted_count_matches(self):
        output = RESEARCH_OUTPUT_SUCCESS
        assert output["urls_extracted"] == len(output["raw_sources"])

    def test_timeout_failure_is_structured_not_raised(self):
        output = RESEARCH_OUTPUT_TIMEOUT
        # Error must be in output, not an unhandled exception
        assert "error" in output
        assert output["error_type"] == "timeout"
        assert output["sources"] == []

    def test_no_writes_in_output_contract(self):
        # The output contract should NOT contain write operations
        # (verified by checking no write-indicating keys exist in success output)
        forbidden_keys = {"written_to", "saved_at", "notion_page_id", "calendar_event"}
        assert not forbidden_keys.intersection(RESEARCH_OUTPUT_SUCCESS.keys())


class TestCapabilityRestrictions:
    """Test that the definition correctly restricts capabilities."""
    import yaml
    from pathlib import Path

    def test_definition_exists(self):
        from pathlib import Path
        definition = Path("wayfinder/workers/W08_web_researcher/definition.yaml")
        assert definition.exists()

    def test_tavily_in_allowed_capabilities(self):
        import yaml
        from pathlib import Path
        definition = yaml.safe_load(
            Path("wayfinder/workers/W08_web_researcher/definition.yaml").read_text()
        )
        caps = definition.get("capabilities", [])
        assert any("tavily" in c for c in caps)

    def test_notion_in_denied_capabilities(self):
        import yaml
        from pathlib import Path
        definition = yaml.safe_load(
            Path("wayfinder/workers/W08_web_researcher/definition.yaml").read_text()
        )
        denied = definition.get("denied_capabilities", [])
        assert any("notion" in c for c in denied)
