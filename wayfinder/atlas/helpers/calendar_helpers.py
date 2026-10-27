"""
wayfinder/atlas/helpers/calendar_helpers.py
──────────────────────────────────────────
Deterministic calendar helpers for W13 (Calendar Analyst) & W15 (Schedule Optimizer).

Calculates:
  - Timezone-safe start/end parsing (including all-day events)
  - Interval merging and conflict detection
  - Free/busy availability intervals within an arbitrary query window
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any


def parse_event_boundary(dt_val: str | dict[str, str], fallback_tz: timezone = timezone.utc, is_end: bool = False) -> datetime:
    """Parse Google Calendar 'dateTime' or 'date' (all-day event) into timezone-aware datetime."""
    if isinstance(dt_val, dict):
        if "dateTime" in dt_val:
            s = dt_val["dateTime"]
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
            return dt if dt.tzinfo else dt.replace(tzinfo=fallback_tz)
        elif "date" in dt_val:
            d = date.fromisoformat(dt_val["date"])
            t = time.max if is_end else time.min
            return datetime.combine(d, t).replace(tzinfo=fallback_tz)
        raise ValueError(f"Invalid date boundary structure: {dt_val}")
    elif isinstance(dt_val, str):
        s = dt_val[:-1] + "+00:00" if dt_val.endswith("Z") else dt_val
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=fallback_tz)
    raise TypeError(f"Unexpected date format type: {type(dt_val)}")


def detect_conflicts(events: list[dict[str, Any]], fallback_tz: timezone = timezone.utc) -> list[dict[str, Any]]:
    """Identifies overlapping events and returns pairs of conflicting event summaries/IDs."""
    normalized = []
    for ev in events:
        start_raw = ev.get("start", {})
        end_raw = ev.get("end", {})
        if not start_raw or not end_raw:
            continue
        try:
            st = parse_event_boundary(start_raw, fallback_tz=fallback_tz, is_end=False)
            et = parse_event_boundary(end_raw, fallback_tz=fallback_tz, is_end=True)
            normalized.append({"id": ev.get("id", ""), "title": ev.get("summary", "(No Title)"), "start": st, "end": et})
        except Exception:
            continue

    normalized.sort(key=lambda x: x["start"])
    conflicts: list[dict[str, Any]] = []

    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            ev1 = normalized[i]
            ev2 = normalized[j]
            # If ev2 starts before ev1 ends, there is an overlap
            if ev2["start"] < ev1["end"]:
                conflicts.append({
                    "event_a": {"id": ev1["id"], "title": ev1["title"], "start": ev1["start"].isoformat(), "end": ev1["end"].isoformat()},
                    "event_b": {"id": ev2["id"], "title": ev2["title"], "start": ev2["start"].isoformat(), "end": ev2["end"].isoformat()},
                    "overlap_minutes": max(0, int((min(ev1["end"], ev2["end"]) - max(ev1["start"], ev2["start"])).total_seconds() / 60)),
                })
            else:
                break
    return conflicts


def calculate_availability(
    events: list[dict[str, Any]],
    window_start: datetime,
    window_end: datetime,
    min_gap_minutes: int = 15,
    fallback_tz: timezone = timezone.utc,
) -> list[dict[str, Any]]:
    """
    Computes free intervals between busy events within [window_start, window_end].
    Merges overlapping or contiguous busy intervals first.
    """
    if window_start.tzinfo is None:
        window_start = window_start.replace(tzinfo=fallback_tz)
    if window_end.tzinfo is None:
        window_end = window_end.replace(tzinfo=fallback_tz)

    busy_intervals: list[tuple[datetime, datetime]] = []

    for ev in events:
        # Ignore free/transparent events if marked
        if ev.get("transparency") == "transparent":
            continue
        start_raw = ev.get("start", {})
        end_raw = ev.get("end", {})
        if not start_raw or not end_raw:
            continue
        try:
            st = parse_event_boundary(start_raw, fallback_tz=fallback_tz, is_end=False)
            et = parse_event_boundary(end_raw, fallback_tz=fallback_tz, is_end=True)
            # Clip to window
            effective_start = max(window_start, st)
            effective_end = min(window_end, et)
            if effective_start < effective_end:
                busy_intervals.append((effective_start, effective_end))
        except Exception:
            continue

    busy_intervals.sort(key=lambda x: x[0])

    # Merge overlapping busy periods
    merged_busy: list[tuple[datetime, datetime]] = []
    for cur_st, cur_et in busy_intervals:
        if not merged_busy:
            merged_busy.append((cur_st, cur_et))
        else:
            prev_st, prev_et = merged_busy[-1]
            if cur_st <= prev_et:
                merged_busy[-1] = (prev_st, max(prev_et, cur_et))
            else:
                merged_busy.append((cur_st, cur_et))

    # Calculate free gaps
    free_slots: list[dict[str, Any]] = []
    cursor = window_start

    for b_st, b_et in merged_busy:
        if b_st > cursor:
            gap_duration = (b_st - cursor).total_seconds() / 60
            if gap_duration >= min_gap_minutes:
                free_slots.append({
                    "start": cursor.isoformat(),
                    "end": b_st.isoformat(),
                    "duration_minutes": int(gap_duration),
                })
        cursor = max(cursor, b_et)

    if cursor < window_end:
        gap_duration = (window_end - cursor).total_seconds() / 60
        if gap_duration >= min_gap_minutes:
            free_slots.append({
                "start": cursor.isoformat(),
                "end": window_end.isoformat(),
                "duration_minutes": int(gap_duration),
            })

    return free_slots
