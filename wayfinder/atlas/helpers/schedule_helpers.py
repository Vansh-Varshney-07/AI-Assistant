"""
wayfinder/atlas/helpers/schedule_helpers.py
──────────────────────────────────────────
Deterministic constraint evaluation & slot allocation helpers for W15 (Schedule Optimizer).

Enforces:
  - Hard constraint checking (no overlap with existing calendar events, no deadline violations)
  - Objective scoring hierarchy:
      1. Zero deadline violations
      2. Priority adherence (high priority placed earlier)
      3. Minimal schedule fragmentation (compact blocks)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def validate_schedule_plan(
    proposed_slots: list[dict[str, Any]],
    existing_calendar_events: list[dict[str, Any]],
    fallback_tz: timezone = timezone.utc,
) -> list[str]:
    """
    Checks proposed task time slots against existing calendar commitments
    and internally for any mutual overlaps or negative durations.
    """
    violations: list[str] = []

    parsed_proposed = []
    for slot in proposed_slots:
        st_raw = slot.get("start")
        et_raw = slot.get("end")
        title = slot.get("task_title", "Untitled Task")
        deadline_raw = slot.get("deadline")

        if not st_raw or not et_raw:
            violations.append(f"Slot for '{title}' missing start or end timestamp")
            continue

        st = datetime.fromisoformat(st_raw)
        et = datetime.fromisoformat(et_raw)
        if st.tzinfo is None:
            st = st.replace(tzinfo=fallback_tz)
        if et.tzinfo is None:
            et = et.replace(tzinfo=fallback_tz)

        if st >= et:
            violations.append(f"Invalid duration for '{title}': start {st} >= end {et}")

        if deadline_raw:
            dl = datetime.fromisoformat(deadline_raw)
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=fallback_tz)
            if et > dl:
                violations.append(f"Deadline violation: '{title}' ends at {et}, after deadline {dl}")

        parsed_proposed.append({"title": title, "start": st, "end": et})

    # Check mutual overlap between proposed tasks
    for i in range(len(parsed_proposed)):
        for j in range(i + 1, len(parsed_proposed)):
            p1 = parsed_proposed[i]
            p2 = parsed_proposed[j]
            if max(p1["start"], p2["start"]) < min(p1["end"], p2["end"]):
                violations.append(f"Mutual overlap between proposed tasks '{p1['title']}' and '{p2['title']}'")

    # Check collision with existing calendar events
    for p in parsed_proposed:
        for ev in existing_calendar_events:
            ev_st_raw = ev.get("start", {}).get("dateTime")
            ev_et_raw = ev.get("end", {}).get("dateTime")
            if not ev_st_raw or not ev_et_raw:
                continue
            ev_st = datetime.fromisoformat(ev_st_raw.replace("Z", "+00:00"))
            ev_et = datetime.fromisoformat(ev_et_raw.replace("Z", "+00:00"))
            if max(p["start"], ev_st) < min(p["end"], ev_et):
                violations.append(f"Conflict: task '{p['title']}' overlaps with existing calendar event '{ev.get('summary')}'")

    return violations


def score_schedule_candidate(
    candidate: dict[str, Any],
    weights: dict[str, float] | None = None,
) -> float:
    """
    Ranks candidate schedules using explicit priority:
    Higher score is better. Penalizes deadline violations severely.
    """
    w = weights or {
        "deadline_violation_penalty": 100.0,
        "priority_match": 10.0,
        "fragmentation_penalty": 2.0,
    }

    deadline_violations = candidate.get("deadline_violations_count", 0)
    priority_matches = candidate.get("high_priority_scheduled_count", 0)
    fragmentation_count = candidate.get("fragmented_blocks_count", 0)

    score = 100.0
    score -= (deadline_violations * w["deadline_violation_penalty"])
    score += (priority_matches * w["priority_match"])
    score -= (fragmentation_count * w["fragmentation_penalty"])

    return round(score, 2)
