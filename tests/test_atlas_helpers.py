"""
tests/test_atlas_helpers.py
───────────────────────────
Unit tests for deterministic Wayfinder Atlas helper modules:
  - Calendar availability & conflicts
  - Document chunking & metadata
  - Data schema inspection & statistics
  - Schedule plan validation & scoring
  - Commitment extraction & deduplication
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

from wayfinder.atlas.helpers.calendar_helpers import (
    calculate_availability,
    detect_conflicts,
    parse_event_boundary,
)
from wayfinder.atlas.helpers.document_helpers import (
    chunk_document_with_citations,
    extract_document_metadata,
)
from wayfinder.atlas.helpers.data_helpers import (
    inspect_tabular_schema,
    validate_data_quality,
    calculate_column_stats,
)
from wayfinder.atlas.helpers.schedule_helpers import (
    validate_schedule_plan,
    score_schedule_candidate,
)
from wayfinder.atlas.helpers.commitment_helpers import (
    extract_commitments_from_text,
    deduplicate_commitments,
)


# ── 1. Calendar Helpers ────────────────────────────────────────────────────────

class TestCalendarHelpers:
    def test_parse_event_boundary_datetime(self):
        dt = parse_event_boundary({"dateTime": "2026-10-26T09:00:00Z"})
        assert dt.hour == 9
        assert dt.tzinfo is not None

    def test_parse_event_boundary_allday(self):
        dt_start = parse_event_boundary({"date": "2026-10-26"}, is_end=False)
        dt_end = parse_event_boundary({"date": "2026-10-26"}, is_end=True)
        assert dt_start.hour == 0
        assert dt_end.hour == 23

    def test_detect_conflicts(self):
        events = [
            {"id": "ev1", "summary": "Meeting A", "start": {"dateTime": "2026-10-26T10:00:00Z"}, "end": {"dateTime": "2026-10-26T11:00:00Z"}},
            {"id": "ev2", "summary": "Meeting B", "start": {"dateTime": "2026-10-26T10:30:00Z"}, "end": {"dateTime": "2026-10-26T11:30:00Z"}},
        ]
        conflicts = detect_conflicts(events)
        assert len(conflicts) == 1
        assert conflicts[0]["overlap_minutes"] == 30

    def test_calculate_availability(self):
        window_start = datetime(2026, 10, 26, 9, 0, tzinfo=timezone.utc)
        window_end = datetime(2026, 10, 26, 17, 0, tzinfo=timezone.utc)
        events = [
            {"summary": "Lunch", "start": {"dateTime": "2026-10-26T12:00:00Z"}, "end": {"dateTime": "2026-10-26T13:00:00Z"}}
        ]
        free_slots = calculate_availability(events, window_start, window_end, min_gap_minutes=30)
        assert len(free_slots) == 2
        assert free_slots[0]["duration_minutes"] == 180  # 9am to 12pm
        assert free_slots[1]["duration_minutes"] == 240  # 1pm to 5pm


# ── 2. Document Helpers ────────────────────────────────────────────────────────

class TestDocumentHelpers:
    def test_extract_document_metadata_existing(self, tmp_path):
        f = tmp_path / "sample.md"
        f.write_text("# Hello World\nSome text content.", encoding="utf-8")
        meta = extract_document_metadata(f)
        assert meta["exists"] is True
        assert meta["file_type"] == "md"
        assert meta["is_empty"] is False

    def test_extract_document_metadata_missing(self, tmp_path):
        meta = extract_document_metadata(tmp_path / "nonexistent.txt")
        assert meta["exists"] is False
        assert meta["is_empty"] is True

    def test_chunk_document_with_citations(self):
        doc = (
            "# Section One\n"
            "This is introduction text.\n\n"
            "## Section Two\n"
            "Detailed architectural description goes here with several sentences."
        )
        chunks = chunk_document_with_citations(doc, chunk_size=80, overlap=20, title="Architecture Doc")
        assert len(chunks) >= 2
        assert any(c["section"] == "Section Two" for c in chunks)
        assert chunks[0]["source"]["title"] == "Architecture Doc"


# ── 3. Data Helpers ────────────────────────────────────────────────────────────

class TestDataHelpers:
    def test_inspect_tabular_schema(self):
        headers = ["ID", "Name", "Revenue", "Active"]
        rows = [
            [1, "Alpha", "1500.50", "true"],
            [2, "Beta", "2300.00", "false"],
            [3, "Gamma", "#DIV/0!", "true"],
        ]
        schema = inspect_tabular_schema(headers, rows)
        assert schema["column_count"] == 4
        assert schema["row_count"] == 3
        rev_col = [c for c in schema["columns"] if c["name"] == "Revenue"][0]
        assert rev_col["formula_error_count"] == 1

    def test_validate_data_quality(self):
        headers = ["ColA", "ColB"]
        rows = [
            ["Val1", "Val2"],
            ["Val1", "Val2"], # duplicate
            ["Val3", "#REF!"], # formula error
        ]
        issues = validate_data_quality(headers, rows)
        types = [i["type"] for i in issues]
        assert "duplicate_row" in types
        assert "formula_error" in types

    def test_calculate_column_stats(self):
        rows = [
            ["Item 1", 10.0],
            ["Item 2", 20.0],
            ["Item 3", 30.0],
            ["Item 4", None],
        ]
        stats = calculate_column_stats(rows, col_index=1)
        assert stats["valid_count"] == 3
        assert stats["null_count"] == 1
        assert stats["mean"] == 20.0
        assert stats["min"] == 10.0
        assert stats["max"] == 30.0


# ── 4. Schedule Helpers ────────────────────────────────────────────────────────

class TestScheduleHelpers:
    def test_validate_schedule_plan_valid(self):
        slots = [
            {"task_title": "Write Report", "start": "2026-10-26T14:00:00+00:00", "end": "2026-10-26T15:00:00+00:00"}
        ]
        events = [
            {"summary": "Team Sync", "start": {"dateTime": "2026-10-26T10:00:00Z"}, "end": {"dateTime": "2026-10-26T11:00:00Z"}}
        ]
        violations = validate_schedule_plan(slots, events)
        assert violations == []

    def test_validate_schedule_plan_conflict_and_deadline(self):
        slots = [
            {
                "task_title": "Late Task",
                "start": "2026-10-26T16:00:00+00:00",
                "end": "2026-10-26T17:30:00+00:00",
                "deadline": "2026-10-26T17:00:00+00:00",
            }
        ]
        violations = validate_schedule_plan(slots, [])
        assert any("Deadline violation" in v for v in violations)

    def test_score_schedule_candidate(self):
        perfect_candidate = {"deadline_violations_count": 0, "high_priority_scheduled_count": 2, "fragmented_blocks_count": 0}
        bad_candidate = {"deadline_violations_count": 1, "high_priority_scheduled_count": 1, "fragmented_blocks_count": 2}
        assert score_schedule_candidate(perfect_candidate) > score_schedule_candidate(bad_candidate)


# ── 5. Commitment Helpers ──────────────────────────────────────────────────────

class TestCommitmentHelpers:
    def test_extract_commitments_confirmed(self):
        text = "Thanks for the notes. I will send the revised slides by Friday EOD."
        source = {"system": "gmail", "item_id": "msg-001"}
        comms = extract_commitments_from_text(text, source)
        assert len(comms) == 1
        assert "send the revised slides" in comms[0]["statement"]
        assert comms[0]["confidence"] >= 0.8
        assert comms[0]["is_tentative"] is False

    def test_extract_commitments_tentative(self):
        text = "I'll try to review the proposal before tomorrow."
        source = {"system": "gmail", "item_id": "msg-002"}
        comms = extract_commitments_from_text(text, source)
        assert len(comms) == 1
        assert comms[0]["is_tentative"] is True
        assert comms[0]["confidence"] < 0.7

    def test_deduplicate_commitments(self):
        existing = [{"commitment_id": "comm-ex-1", "statement": "send the revised slides"}]
        new_items = [
            {"statement": "send the revised slides"},
            {"statement": "deploy backend service"},
        ]
        novel, duplicates = deduplicate_commitments(existing, new_items)
        assert len(novel) == 1
        assert novel[0]["statement"] == "deploy backend service"
        assert len(duplicates) == 1
