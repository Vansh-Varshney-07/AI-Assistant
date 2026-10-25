"""
wayfinder/workers/W24_code_reviewer/tests.py
-------------------------------------------
Offline contract tests for W24 Code Reviewer.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import CodeReview, ReviewFinding, ReviewSeverity


def make_review(**overrides) -> CodeReview:
    defaults = dict(
        review_id="test-w24-001",
        diff_reference="git diff HEAD~1",
        summary="Clean addition of worker contract validation.",
        findings=[
            ReviewFinding(
                finding_id="f-01",
                severity=ReviewSeverity.INFO,
                file_path="wayfinder/workers/schemas.py",
                line_reference="L12",
                description="Consider grouping enums in a dedicated file if schema grows.",
                suggestion="Keep in schemas.py for now; extract if lines exceed 500.",
            )
        ],
        approved=True,
        blocking_issues=[],
    )
    defaults.update(overrides)
    return CodeReview(**defaults)


class TestCodeReviewSchema:
    def test_valid_approved_review_passes(self):
        review = make_review()
        assert review.validate() == []

    def test_approved_with_blocking_issues_fails(self):
        review = make_review(approved=True, blocking_issues=["Syntax error in module"])
        errors = review.validate()
        assert any("blocking_issues" in e for e in errors)

    def test_approved_with_critical_finding_fails(self):
        critical_finding = ReviewFinding(
            finding_id="f-crit",
            severity=ReviewSeverity.CRITICAL,
            file_path="auth.py",
            line_reference="L42",
            description="API key hardcoded in source file",
            suggestion="Move credential to environment variable",
        )
        review = make_review(approved=True, findings=[critical_finding])
        errors = review.validate()
        assert any("CRITICAL" in e for e in errors)

    def test_unapproved_with_critical_finding_passes(self):
        critical_finding = ReviewFinding(
            finding_id="f-crit",
            severity=ReviewSeverity.CRITICAL,
            file_path="auth.py",
            line_reference="L42",
            description="API key hardcoded in source file",
            suggestion="Move credential to environment variable",
        )
        review = make_review(
            approved=False,
            findings=[critical_finding],
            blocking_issues=["Hardcoded secret"],
        )
        assert review.validate() == []


class TestW24DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        def_path = Path(__file__).parent / "definition.yaml"
        assert def_path.exists()
        with open(def_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W24"
        assert "Code Reviewer" in data["name"]
        assert "filesystem.read_file" in data["capabilities"]
        assert "filesystem.patch_file" in data["denied_capabilities"]
        assert data["output_contract"] == "CodeReview"
