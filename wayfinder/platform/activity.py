"""Bounded W26 data connection to an explicitly selected canonical activity CSV.

Use the existing file broker for handles/grants and Python's CSV reader for the
published data schema. No health inference, background collection or memory write.
"""

import csv
from datetime import datetime
import io
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, model_validator

from wayfinder.platform.contracts import Contract, VERSION


class ActivityRecord(Contract):
    provider: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    record_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    revision: int = Field(ge=1, le=2**31 - 1)
    metric: Literal["steps", "workout_duration"]
    value: float = Field(ge=0, le=1e9, allow_inf_nan=False)
    unit: Literal["count", "minute"]
    start_time: str = Field(min_length=1, max_length=40)
    end_time: str = Field(min_length=1, max_length=40)
    timezone: str = Field(min_length=1, max_length=80)

    @model_validator(mode="after")
    def valid_interval(self):
        if self.unit != {"steps": "count", "workout_duration": "minute"}[self.metric]:
            raise ValueError("Activity metric and unit do not match.")
        if self.metric == "steps" and not self.value.is_integer():
            raise ValueError("Steps require a whole count.")
        start, end = (
            datetime.fromisoformat(self.start_time),
            datetime.fromisoformat(self.end_time),
        )
        try:
            zone = ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as error:
            raise ValueError("An installed IANA timezone is required.") from error
        if start.utcoffset() is None or end.utcoffset() is None or start >= end:
            raise ValueError(
                "Activity requires an ordered interval with explicit offsets."
            )
        if any(v.utcoffset() != v.astimezone(zone).utcoffset() for v in (start, end)):
            raise ValueError("Timestamp offset does not match the declared timezone.")
        if (end - start).total_seconds() > 86400 * 31:
            raise ValueError("Activity intervals may cover at most 31 days.")
        if (
            self.metric == "workout_duration"
            and self.value * 60 > (end - start).total_seconds()
        ):
            raise ValueError("Workout duration exceeds its source interval.")
        return self


FIELDS = tuple(ActivityRecord.model_fields)


def read_activity(app, who, scope, reference):
    # This final resource handler authorizes even when called without the API router.
    app.authorize(who)
    app.space(who, scope.space)
    if who.owner != scope.owner or app.closed:
        raise ValueError("Activity scope unavailable.")
    selected = app.workers.files.read(scope.worker_scope(), reference)
    if selected["extension"] != ".csv":
        raise ValueError("Select a canonical activity CSV file.")
    try:
        reader = csv.DictReader(
            io.StringIO(selected["data"].decode("utf-8-sig")), strict=True
        )
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Activity CSV headers must match the published schema.")
        rows, keys = [], set()
        for raw in reader:
            if (
                len(rows) >= 366
                or set(raw) != set(FIELDS)
                or any(not isinstance(v, str) or len(v) > 200 for v in raw.values())
            ):
                raise ValueError("Activity row or 366-record budget exceeded.")
            row = ActivityRecord.model_validate(
                dict(raw, revision=int(raw["revision"]), value=float(raw["value"]))
            )
            key = (row.provider, row.record_id)
            if key in keys:
                raise ValueError(
                    "Repeated provider record identity; select one reviewed revision."
                )
            keys.add(key)
            rows.append(row.model_dump())
    except (UnicodeError, csv.Error, OverflowError) as error:
        raise ValueError("Activity CSV is malformed.") from error
    if not rows:
        raise ValueError("Activity CSV contains no records.")
    warnings = ["Missing periods are unknown; absence is not a zero value."]
    groups = {}
    for row in rows:
        groups.setdefault((row["provider"], row["metric"]), []).append(row)
    summaries = []
    for (provider, metric), items in groups.items():
        ordered = sorted(items, key=lambda r: datetime.fromisoformat(r["start_time"]))
        overlapping = any(
            datetime.fromisoformat(a["end_time"])
            > datetime.fromisoformat(b["start_time"])
            for a, b in zip(ordered, ordered[1:])
        )
        summaries.append(
            dict(
                provider=provider,
                metric=metric,
                unit=items[0]["unit"],
                records=len(items),
                total=None if overlapping else sum(r["value"] for r in items),
                overlapping=overlapping,
            )
        )
        if overlapping:
            warnings.append(
                "Overlapping intervals for "
                + provider
                + "/"
                + metric
                + "; total withheld."
            )
    if len({r["provider"] for r in rows}) > 1:
        warnings.append(
            "Provider totals are separate; cross-provider deduplication is not established."
        )
    # Recheck revocation and selected-file identity/hash immediately before returning.
    if (
        app.workers.files.read(scope.worker_scope(), reference)["sha256"]
        != selected["sha256"]
    ):
        raise ValueError("Activity source changed during reading.")
    return dict(
        contract=VERSION,
        source=dict(name=selected["source"], sha256=selected["sha256"]),
        format="wayfinder.activity.csv/1",
        records=rows,
        summaries=summaries,
        warnings=warnings,
        memory_written=False,
        provider_live=False,
    )
