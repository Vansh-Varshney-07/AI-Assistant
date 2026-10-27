"""
wayfinder/workers/W01_intent_analyst/tests.py
---------------------------------------------
Offline contract tests for W01 Intent Analyst.
No Hermes, no live tools, no network.
Run: .venv/Scripts/pytest wayfinder/workers/W01_intent_analyst/tests.py -v
"""
import pytest
from wayfinder.workers.W01_intent_analyst.schemas import (
    ActionType, IntentOutput, Urgency
)
from wayfinder.workers.W01_intent_analyst.fixtures import (
    SUCCESS_CLEAR_RESEARCH, SUCCESS_SCHEDULE_TODAY, SUCCESS_COMMUNICATE,
    CLARIFICATION_AMBIGUOUS, CLARIFICATION_LOW_CONFIDENCE, ALL_FIXTURES
)


class TestIntentOutputSchema:
    def test_all_fixtures_pass_validation(self):
        for fixture in ALL_FIXTURES:
            errors = fixture.validate()
            assert errors == [], f"{fixture.intent_id} failed: {errors}"

    def test_action_type_from_allowed_enum(self):
        for fixture in ALL_FIXTURES:
            assert fixture.action_type in ActionType

    def test_urgency_from_allowed_enum(self):
        for fixture in ALL_FIXTURES:
            assert fixture.urgency in Urgency

    def test_confidence_in_range(self):
        for fixture in ALL_FIXTURES:
            assert 0.0 <= fixture.confidence <= 1.0

    def test_subject_entities_is_list(self):
        for fixture in ALL_FIXTURES:
            assert isinstance(fixture.subject_entities, list)

    def test_ambiguities_is_list(self):
        for fixture in ALL_FIXTURES:
            assert isinstance(fixture.ambiguities, list)


class TestClarificationInvariants:
    def test_non_empty_ambiguities_forces_clarification(self):
        assert CLARIFICATION_AMBIGUOUS.requires_clarification is True
        assert len(CLARIFICATION_AMBIGUOUS.ambiguities) > 0

    def test_low_confidence_forces_clarification(self):
        assert CLARIFICATION_LOW_CONFIDENCE.requires_clarification is True
        assert CLARIFICATION_LOW_CONFIDENCE.confidence < 0.6

    def test_clear_intent_no_clarification_needed(self):
        assert SUCCESS_CLEAR_RESEARCH.requires_clarification is False
        assert SUCCESS_CLEAR_RESEARCH.ambiguities == []
        assert SUCCESS_CLEAR_RESEARCH.confidence >= 0.6

    def test_invalid_confidence_rejected(self):
        with pytest.raises((AssertionError, ValueError)):
            IntentOutput(
                intent_id="bad",
                raw_input="test",
                primary_goal="test goal",
                action_type=ActionType.RESEARCH,
                subject_entities=[],
                urgency=Urgency.UNSPECIFIED,
                ambiguities=[],
                requires_clarification=False,
                confidence=1.5,  # invalid
            )


class TestSuccessFixtures:
    def test_research_fixture(self):
        f = SUCCESS_CLEAR_RESEARCH
        assert f.action_type == ActionType.RESEARCH
        assert "Python" in f.subject_entities
        assert f.confidence > 0.8

    def test_schedule_fixture(self):
        f = SUCCESS_SCHEDULE_TODAY
        assert f.action_type == ActionType.SCHEDULE
        assert f.urgency == Urgency.TODAY
        assert "calendar" in f.subject_entities

    def test_communicate_fixture(self):
        f = SUCCESS_COMMUNICATE
        assert f.action_type == ActionType.COMMUNICATE
        assert "Rahul" in f.subject_entities
