"""
wayfinder/workers/W13_calendar_analyst/test_worker.py
──────────────────────────────────────────────────────
Offline contract tests for W13 Calendar Analyst.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import CalendarAnalysis


def make_calendar_analysis(**overrides) -> CalendarAnalysis:
    defaults = dict(
        analysis_id="cal-001",
        query_window={"start": "2026-10-26T00:00:00+00:00", "end": "2026-10-26T23:59:59+00:00"},
        timezone_name="UTC",
        scheduled_events_count=3,
        conflicts=[],
        available_slots=[
            {"start": "2026-10-26T13:00:00+00:00", "end": "2026-10-26T15:00:00+00:00", "duration_minutes": 120}
        ],
        is_partial=False,
        notes="",
    )
    defaults.update(overrides)
    return CalendarAnalysis(**defaults)


class TestCalendarAnalysisSchema:
    def test_valid_analysis_passes(self):
        cal = make_calendar_analysis()
        assert cal.validate() == []

    def test_missing_timezone_fails(self):
        cal = make_calendar_analysis(timezone_name="")
        errors = cal.validate()
        assert any("timezone_name" in e for e in errors)

    def test_missing_window_boundary_fails(self):
        cal = make_calendar_analysis(query_window={"start": "2026-10-26T00:00:00Z"})
        errors = cal.validate()
        assert any("query_window" in e for e in errors)

    def test_partial_calendar_flagged(self):
        cal = make_calendar_analysis(is_partial=True, notes="Secondary work calendar unreachable")
        assert cal.validate() == []
        assert cal.is_partial is True


class TestW13DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W13"
        assert "Calendar Analyst" in data["name"]
        assert "google.calendar_read" in data["capabilities"]
        assert "google.calendar_write" in data["denied_capabilities"]
        assert data["output_contract"] == "CalendarAnalysis"
