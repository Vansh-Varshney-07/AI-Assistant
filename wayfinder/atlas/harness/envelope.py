"""
wayfinder/atlas/harness/envelope.py
───────────────────────────────────
Standardized Result Envelope and Common Infrastructure for all Wayfinder tools.

Provides:
  - Canonical ToolResult envelope with uniform statuses:
    ok | empty | not_found | permission_denied | unavailable | partial | failed
  - SourceReference schema for explicit document/item citations
  - Timezone-aware ISO 8601 formatting utilities
  - Trace ID generation for auditable execution chains
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional


class ToolStatus(str, Enum):
    OK                 = "ok"
    EMPTY              = "empty"
    NOT_FOUND          = "not_found"
    PERMISSION_DENIED  = "permission_denied"
    UNAVAILABLE        = "unavailable"
    PARTIAL            = "partial"
    FAILED             = "failed"


@dataclass
class SourceRef:
    """Explicit citation tracking the originating system and item ID."""
    system: str                          # e.g. "google_calendar", "google_docs", "notion", "local_file"
    item_id: str                         # unique ID within originating system
    title: str = ""                      # human-readable title or file name
    uri: str = ""                        # web URL or file path if available
    section: str = ""                    # heading, page number, or block ID
    retrieved_at: str = ""               # ISO 8601 timestamp

    def to_dict(self) -> dict[str, str]:
        return {
            "system": self.system,
            "item_id": self.item_id,
            "title": self.title,
            "uri": self.uri,
            "section": self.section,
            "retrieved_at": self.retrieved_at or current_iso_timestamp(),
        }


@dataclass
class ToolResult:
    """Universal envelope returned by all Wayfinder tool executions."""
    success: bool
    status: ToolStatus
    data: Any = None
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    source_refs: list[SourceRef] = field(default_factory=list)
    partial: bool = False
    trace_id: str = field(default_factory=lambda: f"wf-tr-{uuid.uuid4().hex[:12]}")

    @classmethod
    def ok(cls, data: Any, source_refs: list[SourceRef] | None = None, warnings: list[str] | None = None) -> ToolResult:
        return cls(
            success=True,
            status=ToolStatus.OK,
            data=data,
            source_refs=source_refs or [],
            warnings=warnings or [],
        )

    @classmethod
    def empty(cls, message: str = "No records found", source_refs: list[SourceRef] | None = None) -> ToolResult:
        return cls(
            success=True,
            status=ToolStatus.EMPTY,
            data=[],
            warnings=[message],
            source_refs=source_refs or [],
        )

    @classmethod
    def partial_result(cls, data: Any, warnings: list[str], source_refs: list[SourceRef] | None = None) -> ToolResult:
        return cls(
            success=True,
            status=ToolStatus.PARTIAL,
            data=data,
            partial=True,
            warnings=warnings,
            source_refs=source_refs or [],
        )

    @classmethod
    def not_found(cls, message: str, item_id: str = "") -> ToolResult:
        return cls(
            success=False,
            status=ToolStatus.NOT_FOUND,
            error=message,
            warnings=[f"Item {item_id} not found" if item_id else message],
        )

    @classmethod
    def permission_denied(cls, message: str, required_scope: str = "") -> ToolResult:
        return cls(
            success=False,
            status=ToolStatus.PERMISSION_DENIED,
            error=message,
            warnings=[f"Required scope or approval missing: {required_scope}" if required_scope else message],
        )

    @classmethod
    def unavailable(cls, message: str) -> ToolResult:
        return cls(
            success=False,
            status=ToolStatus.UNAVAILABLE,
            error=message,
        )

    @classmethod
    def failed(cls, error: str, warnings: list[str] | None = None) -> ToolResult:
        return cls(
            success=False,
            status=ToolStatus.FAILED,
            error=error,
            warnings=warnings or [],
        )


# ── Timezone & ISO 8601 Utilities ─────────────────────────────────────────────

def current_iso_timestamp(tz: timezone = timezone.utc) -> str:
    """Generate RFC 3339 / ISO 8601 compliant string with explicit timezone offset."""
    return datetime.now(tz).isoformat()


def parse_iso_datetime(iso_str: str) -> datetime:
    """Parse an ISO 8601 datetime string, ensuring timezone awareness."""
    # Handle 'Z' suffix as UTC
    if iso_str.endswith("Z"):
        iso_str = iso_str[:-1] + "+00:00"
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
