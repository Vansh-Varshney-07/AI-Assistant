"""
wayfinder/workers/W06_result_validator/tests.py
-----------------------------------------------
Offline contract tests for W06 Result Validator.
"""
import pytest
from wayfinder.workers.schemas import ValidationResult, ValidationStatus


def make_result(**overrides) -> ValidationResult:
    defaults = dict(
        validation_id="test-w06-001",
        target_worker="W01_intent_analyst",
        target_output_id="test-w01-001",
        status=ValidationStatus.PASS,
        checks_passed=["schema_complete", "action_type_valid", "confidence_in_range"],
        checks_failed=[],
        corrective_actions=[],
        confidence=0.95,
    )
    defaults.update(overrides)
    return ValidationResult(**defaults)


class TestValidationResultSchema:
    def test_pass_result_valid(self):
        result = make_result()
        assert result.validate() == []

    def test_fail_without_corrective_action_invalid(self):
        result = make_result(
            status=ValidationStatus.FAIL,
            checks_failed=["primary_goal_empty"],
            corrective_actions=[],   # missing — invalid
        )
        errors = result.validate()
        assert any("corrective_action" in e for e in errors)

    def test_fail_with_corrective_action_valid(self):
        result = make_result(
            status=ValidationStatus.FAIL,
            checks_failed=["primary_goal_empty"],
            corrective_actions=["Re-run W01 with more context"],
            confidence=0.2,
        )
        assert result.validate() == []

    def test_partial_status_valid(self):
        result = make_result(
            status=ValidationStatus.PARTIAL,
            checks_passed=["schema_complete"],
            checks_failed=["confidence_below_threshold"],
            corrective_actions=["Increase context and retry"],
            confidence=0.65,
        )
        assert result.validate() == []

    def test_confidence_out_of_range(self):
        result = make_result(confidence=1.5)
        errors = result.validate()
        assert any("confidence" in e for e in errors)

    def test_links_to_target_worker(self):
        result = make_result(target_worker="W03_task_planner", target_output_id="plan-001")
        assert result.target_worker == "W03_task_planner"
