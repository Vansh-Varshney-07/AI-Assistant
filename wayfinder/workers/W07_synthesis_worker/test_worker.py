"""
wayfinder/workers/W07_synthesis_worker/tests.py
-----------------------------------------------
Offline contract tests for W07 Synthesis Worker.
"""
import pytest
from wayfinder.workers.schemas import SynthesisReport, SourceReference


def make_report(**overrides) -> SynthesisReport:
    defaults = dict(
        report_id="test-w07-001",
        query="Best async Python frameworks",
        executive_summary="asyncio remains the standard; FastAPI and Trio offer higher-level APIs.",
        key_findings=[
            "asyncio is built into Python 3.4+ and is the de-facto standard",
            "FastAPI builds on asyncio for HTTP with automatic OpenAPI docs",
            "Trio offers a cleaner structured concurrency model",
        ],
        sources=[
            SourceReference(
                url="https://docs.python.org/3/library/asyncio.html",
                title="asyncio - Python docs",
                excerpt="asyncio is a library to write concurrent code using the async/await syntax.",
            ),
            SourceReference(
                url="https://fastapi.tiangolo.com/",
                title="FastAPI",
                excerpt="FastAPI is a modern, fast web framework for building APIs with Python.",
            ),
        ],
        confidence=0.88,
        unresolved_questions=[],
        knowledge_gaps=[],
    )
    defaults.update(overrides)
    return SynthesisReport(**defaults)


class TestSynthesisReportSchema:
    def test_valid_report_passes(self):
        report = make_report()
        assert report.validate() == []

    def test_empty_summary_fails(self):
        report = make_report(executive_summary="")
        errors = report.validate()
        assert any("executive_summary" in e for e in errors)

    def test_empty_key_findings_fails(self):
        report = make_report(key_findings=[])
        errors = report.validate()
        assert any("key_findings" in e for e in errors)

    def test_low_confidence_without_unresolved_fails(self):
        report = make_report(confidence=0.35, unresolved_questions=[])
        errors = report.validate()
        assert any("unresolved" in e for e in errors)

    def test_low_confidence_with_unresolved_passes(self):
        report = make_report(
            confidence=0.35,
            unresolved_questions=["Could not find performance benchmarks"],
        )
        assert report.validate() == []

    def test_sources_have_required_fields(self):
        report = make_report()
        for s in report.sources:
            assert s.url
            assert s.title
            assert s.excerpt

    def test_knowledge_gaps_documented(self):
        report = make_report(
            knowledge_gaps=["No mobile framework comparisons found"],
            confidence=0.75,
        )
        assert report.validate() == []
        assert len(report.knowledge_gaps) == 1
