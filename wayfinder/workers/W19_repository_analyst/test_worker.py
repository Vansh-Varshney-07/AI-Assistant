"""
wayfinder/workers/W19_repository_analyst/tests.py
-------------------------------------------------
Offline contract tests for W19 Repository Analyst.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import RepositoryInsight


def make_insight(**overrides) -> RepositoryInsight:
    defaults = dict(
        analysis_id="test-w19-001",
        repo_path="wayfinder",
        language="Python",
        key_modules=["wayfinder.atlas", "wayfinder.workers", "wayfinder.providers"],
        entry_points=["wayfinder/atlas/indexing/build_index.py"],
        dependencies=["pyyaml", "pydantic", "pytest"],
        architectural_notes="Modular agent architecture using Atlas tool registry and capability routing.",
        test_coverage_notes="Unit tests present under tests/ and worker subdirectories.",
        security_notes="Credentials separated into .env and secrets/ directory.",
    )
    defaults.update(overrides)
    return RepositoryInsight(**defaults)


class TestRepositoryInsightSchema:
    def test_valid_insight_passes(self):
        insight = make_insight()
        assert insight.validate() == []

    def test_empty_key_modules_fails(self):
        insight = make_insight(key_modules=[])
        errors = insight.validate()
        assert any("key_modules" in e for e in errors)

    def test_empty_architectural_notes_fails(self):
        insight = make_insight(architectural_notes="")
        errors = insight.validate()
        assert any("architectural_notes" in e for e in errors)

    def test_optional_security_notes(self):
        insight = make_insight(security_notes="")
        assert insight.validate() == []


class TestW19DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        def_path = Path(__file__).parent / "definition.yaml"
        assert def_path.exists()
        with open(def_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W19"
        assert "Repository Analyst" in data["name"]
        assert "filesystem.read_file" in data["capabilities"]
        assert "filesystem.patch_file" in data["denied_capabilities"]
        assert data["output_contract"] == "RepositoryInsight"
