"""
wayfinder/workers/W12_knowledge_synthesizer/tests.py
-----------------------------------------------------
Offline contract tests for W12 Knowledge Synthesizer.
"""
import pytest
from wayfinder.workers.schemas import SynthesisReport, SourceReference


def make_report(**overrides) -> SynthesisReport:
    defaults = dict(
        report_id="test-w12-001",
        query="What are my DSA study priorities?",
        executive_summary=(
            "Based on your Notion DSA roadmap, priority topics are arrays, trees, "
            "and graphs. You are 60% through the Striver sheet."
        ),
        key_findings=[
            "Arrays and two-pointer patterns are marked incomplete",
            "Binary trees are 80% done",
            "Graph BFS/DFS has not been started",
        ],
        sources=[
            SourceReference(
                url="https://app.notion.com/p/DSA-Interview-Roadmap-58b3fd8a742947758ae3f9a23c5e73f1",
                title="DSA Interview Roadmap — Notion",
                excerpt="Arrays: 12/20 complete. Trees: 16/20 complete. Graphs: 0/15.",
            )
        ],
        confidence=0.82,
        unresolved_questions=[],
        knowledge_gaps=[],
    )
    defaults.update(overrides)
    return SynthesisReport(**defaults)


class TestKnowledgeSynthesizerContract:
    def test_valid_report_passes(self):
        report = make_report()
        assert report.validate() == []

    def test_notion_url_in_sources(self):
        report = make_report()
        notion_sources = [s for s in report.sources if "notion.com" in s.url]
        assert len(notion_sources) > 0, "Knowledge synthesizer should reference Notion URLs"

    def test_low_confidence_requires_unresolved(self):
        report = make_report(confidence=0.42, unresolved_questions=[])
        errors = report.validate()
        assert any("unresolved" in e for e in errors)

    def test_knowledge_gaps_documented(self):
        report = make_report(
            knowledge_gaps=["Agent/MCP Roadmap Notion page not shared with integration"],
        )
        assert report.validate() == []
        assert len(report.knowledge_gaps) > 0

    def test_no_fabricated_sources(self):
        report = make_report()
        # All sources should be from a real known integration (notion.com or docs.google.com)
        for s in report.sources:
            is_known = (
                "notion.com" in s.url
                or "docs.google.com" in s.url
                or "drive.google.com" in s.url
            )
            assert is_known, f"Source URL looks fabricated: {s.url}"

    def test_empty_summary_fails(self):
        report = make_report(executive_summary="")
        assert any("executive_summary" in e for e in report.validate())
