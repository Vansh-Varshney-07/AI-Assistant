"""
wayfinder/workers/W11_data_analyst/test_worker.py
──────────────────────────────────────────────────
Offline contract tests for W11 Data Analyst.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import DataAnalysisReport


def make_data_report(**overrides) -> DataAnalysisReport:
    defaults = dict(
        analysis_id="data-rep-001",
        dataset_name="Monthly Revenue Metrics",
        schema_summary={"column_count": 3, "row_count": 10},
        quality_issues=[],
        deterministic_metrics={"mean_revenue": 14500.50, "total_revenue": 145005.00},
        findings=["Average monthly revenue is 14500.50 with a steady 4% MoM growth rate."],
        caveats=[],
    )
    defaults.update(overrides)
    return DataAnalysisReport(**defaults)


class TestDataAnalysisReportSchema:
    def test_valid_report_passes(self):
        rep = make_data_report()
        assert rep.validate() == []

    def test_empty_findings_fails(self):
        rep = make_data_report(findings=[])
        errors = rep.validate()
        assert any("findings" in e for e in errors)

    def test_quality_issues_without_caveats_fails(self):
        rep = make_data_report(
            quality_issues=[{"type": "formula_error", "column": "Profit", "value": "#DIV/0!"}],
            caveats=[],
        )
        errors = rep.validate()
        assert any("must include caveats" in e for e in errors)

    def test_quality_issues_with_caveats_passes(self):
        rep = make_data_report(
            quality_issues=[{"type": "formula_error", "column": "Profit", "value": "#DIV/0!"}],
            caveats=["Excluded 1 row with formula error #DIV/0! in Profit column"],
        )
        assert rep.validate() == []


class TestW11DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W11"
        assert "Data Analyst" in data["name"]
        assert "google.sheets_read" in data["capabilities"]
        assert "google.sheets_write" in data["approval_gated_capabilities"]
        assert data["output_contract"] == "DataAnalysisReport"
