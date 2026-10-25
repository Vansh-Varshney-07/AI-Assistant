"""
wayfinder/workers/W10_document_analyst/test_worker.py
──────────────────────────────────────────────────────
Offline contract tests for W10 Document Analyst.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import DocumentAnalysisReport, DocumentFinding


def make_report(**overrides) -> DocumentAnalysisReport:
    defaults = dict(
        analysis_id="doc-rep-001",
        query="What is the architecture of Wayfinder Atlas?",
        documents_consulted=[
            {"system": "notion", "item_id": "page-notion-001", "title": "Atlas Architecture"}
        ],
        findings=[
            DocumentFinding(
                statement="Atlas uses a verified tool registry",
                quote="Atlas enforces verified tool discovery through tools.jsonl",
                section="Section 2: Registry",
                document_id="page-notion-001",
                document_title="Atlas Architecture",
            )
        ],
        unsupported_claims=["Deployment to Kubernetes is planned for Q4"],
        partial=False,
        notes="",
    )
    defaults.update(overrides)
    return DocumentAnalysisReport(**defaults)


class TestDocumentAnalysisReportSchema:
    def test_valid_report_passes(self):
        rep = make_report()
        assert rep.validate() == []

    def test_empty_documents_consulted_fails(self):
        rep = make_report(documents_consulted=[])
        errors = rep.validate()
        assert any("documents_consulted" in e for e in errors)

    def test_finding_without_quote_fails(self):
        bad_finding = DocumentFinding(
            statement="Fabricated point",
            quote="",
            section="Section 1",
            document_id="doc-1",
            document_title="Doc",
        )
        rep = make_report(findings=[bad_finding])
        errors = rep.validate()
        assert any("cite both quote and document_id" in e for e in errors)

    def test_partial_document_flagged(self):
        rep = make_report(partial=True, notes="Document exceeded 100k chars; truncated.")
        assert rep.validate() == []
        assert rep.partial is True


class TestW10DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W10"
        assert "Document Analyst" in data["name"]
        assert "google.docs_read" in data["capabilities"]
        assert "google.docs_write" in data["approval_gated_capabilities"]
        assert "tavily_research" in data["denied_capabilities"]
        assert data["output_contract"] == "DocumentAnalysisReport"
