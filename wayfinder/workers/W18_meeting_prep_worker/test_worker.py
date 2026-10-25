"""
wayfinder/workers/W18_meeting_prep_worker/test_worker.py
────────────────────────────────────────────────────────
Offline contract tests for W18 Meeting Preparation Worker.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import MeetingBrief


def make_brief(**overrides) -> MeetingBrief:
    defaults = dict(
        brief_id="brief-001",
        meeting_id="meeting-cal-123",
        meeting_title="Wayfinder Architecture Review",
        start_time="2026-10-27T10:00:00Z",
        end_time="2026-10-27T11:00:00Z",
        attendees=["alice@example.com", "bob@example.com"],
        agenda=["1. Review tool verification", "2. Discuss worker schemas"],
        related_notes=["Reviewed Notion page 'Atlas Architecture'"],
        related_emails=["Thread: 'Q4 milestones alignment'"],
        open_tasks=["Finish W18 contract testing"],
        unresolved_questions=["Who will own the persistent commitment audit log?"],
        cited_sources=[{"system": "google_calendar", "id": "meeting-cal-123"}],
    )
    defaults.update(overrides)
    return MeetingBrief(**defaults)


class TestMeetingBriefSchema:
    def test_valid_brief_passes(self):
        brief = make_brief()
        assert brief.validate() == []

    def test_missing_title_fails(self):
        brief = make_brief(meeting_title="")
        errors = brief.validate()
        assert any("meeting_title" in e for e in errors)

    def test_missing_start_time_fails(self):
        brief = make_brief(start_time="")
        errors = brief.validate()
        assert any("start_time" in e for e in errors)


class TestW18DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W18"
        assert "Meeting Preparation Worker" in data["name"]
        assert "google.calendar_read" in data["capabilities"]
        assert "google.gmail_send" in data["denied_capabilities"]
        assert data["output_contract"] == "MeetingBrief"
