"""Tests for FileContextService (P06.01) and ActivityRecord (P06.05)."""
import pytest
from wayfinder.platform.file_context import FileContextService, FileContextExpired, MAX_CHARS
from wayfinder.platform.activity import ActivityRecord

# --- FileContextService ---

def test_register_and_get_excerpt(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("Hello world. " * 100)
    svc = FileContextService()
    entry = svc.register("f1", str(f))
    result = svc.get_excerpt("f1")
    assert result["sha256"] and len(result["sha256"]) == 64
    assert "excerpt" in result
    assert len(result["excerpt"]) <= MAX_CHARS

def test_large_file_truncated(tmp_path):
    f = tmp_path / "large.txt"
    f.write_text("x" * 10000)
    svc = FileContextService()
    entry = svc.register("f2", str(f))
    result = svc.get_excerpt("f2")
    assert result["truncated"] is True
    assert len(result["excerpt"]) == MAX_CHARS

def test_revoke_raises_expired(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("content")
    svc = FileContextService()
    svc.register("f3", str(f))
    svc.revoke("f3")
    with pytest.raises(FileContextExpired):
        svc.get_excerpt("f3")

def test_missing_file_raises(tmp_path):
    svc = FileContextService()
    with pytest.raises(FileNotFoundError):
        svc.register("f4", str(tmp_path / "nonexistent.txt"))

def test_unknown_id_raises():
    svc = FileContextService()
    with pytest.raises(KeyError):
        svc.get_excerpt("unknown")

def test_cleanup_expired(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("content")
    svc = FileContextService()
    svc.register("f5", str(f))
    svc.revoke("f5")
    removed = svc.cleanup_expired()
    assert removed == 1

# --- ActivityRecord validation ---

def test_activity_record_valid_steps():
    record = ActivityRecord(
        provider="apple_health",
        record_id="rec-1",
        revision=1,
        metric="steps",
        value=5000.0,
        unit="count",
        start_time="2026-01-01T08:00:00+00:00",
        end_time="2026-01-01T09:00:00+00:00",
        timezone="UTC",
    )
    assert record.value == 5000.0
    assert record.metric == "steps"

def test_activity_record_invalid_metric_unit_mismatch():
    with pytest.raises(ValueError, match="do not match"):
        ActivityRecord(
            provider="apple_health",
            record_id="rec-2",
            revision=1,
            metric="steps",
            value=5000.0,
            unit="minute",
            start_time="2026-01-01T08:00:00+00:00",
            end_time="2026-01-01T09:00:00+00:00",
            timezone="UTC",
        )

def test_activity_record_fractional_steps_rejected():
    with pytest.raises(ValueError, match="whole count"):
        ActivityRecord(
            provider="apple_health",
            record_id="rec-3",
            revision=1,
            metric="steps",
            value=5000.5,
            unit="count",
            start_time="2026-01-01T08:00:00+00:00",
            end_time="2026-01-01T09:00:00+00:00",
            timezone="UTC",
        )

def test_activity_record_inverted_interval_rejected():
    with pytest.raises(ValueError, match="ordered interval"):
        ActivityRecord(
            provider="apple_health",
            record_id="rec-4",
            revision=1,
            metric="steps",
            value=100.0,
            unit="count",
            start_time="2026-01-01T10:00:00+00:00",
            end_time="2026-01-01T09:00:00+00:00",
            timezone="UTC",
        )
