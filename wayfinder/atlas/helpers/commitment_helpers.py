"""
wayfinder/atlas/helpers/commitment_helpers.py
────────────────────────────────────────────
Deterministic extraction, normalization, and deduplication helpers for W16 (Commitment Tracker).

Enforces:
  - Detection of commitments vs tentative language ("I will" vs "I might try")
  - Structured extraction: owner, recipient, statement, deadline, confidence, evidence quote
  - Deduplication matching to avoid duplicate task creation
"""

from __future__ import annotations

import re
import uuid
from typing import Any


TENTATIVE_TRIGGERS = [
    r"\bi might\b",
    r"\bi'll try to\b",
    r"\bi will try to\b",
    r"\bmaybe\b",
    r"\bpossibly\b",
    r"\bif possible\b",
    r"\bhopefully\b",
]

CONFIRMED_PROMISE_PATTERNS = [
    (r"\b(?:i will|i'll)\s+([a-zA-Z0-9_\s]{5,60}?)(?:\s+by|\s+before|\s+tomorrow|\s+today|\s+on|\.|$)", "self"),
    (r"\b(?:we will|we'll)\s+([a-zA-Z0-9_\s]{5,60}?)(?:\s+by|\s+before|\s+tomorrow|\s+today|\s+on|\.|$)", "team"),
    (r"\b(?:please|could you)\s+([a-zA-Z0-9_\s]{5,60}?)(?:\s+by|\s+before|\s+tomorrow|\s+today|\.|$)", "requested"),
]

DEADLINE_PATTERNS = [
    r"\bby\s+([A-Za-z]+day|\d{1,2}:\d{2}|tomorrow|today|eod|end of day|\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b",
    r"\bbefore\s+([A-Za-z]+day|\d{1,2}:\d{2}|tomorrow|today|eod)\b",
    r"\bdue\s+(?:on\s+)?([A-Za-z]+day|\d{1,2}/\d{1,2}(?:/\d{2,4})?|tomorrow)\b",
]


def extract_commitments_from_text(
    text: str,
    source_ref: dict[str, str],
    default_owner: str = "",
) -> list[dict[str, Any]]:
    """Extracts candidate commitment records from raw text without mutating external stores."""
    commitments: list[dict[str, Any]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        lower_line = line.lower()

        # Check if line contains a tentative disclaimer
        is_tentative = any(re.search(pat, lower_line) for pat in TENTATIVE_TRIGGERS)

        for pat, role in CONFIRMED_PROMISE_PATTERNS:
            match = re.search(pat, line, re.IGNORECASE)
            if match:
                action = match.group(1).strip()
                if len(action) < 5:
                    continue

                # Find deadline
                deadline_str = ""
                for d_pat in DEADLINE_PATTERNS:
                    d_match = re.search(d_pat, line, re.IGNORECASE)
                    if d_match:
                        deadline_str = d_match.group(1).strip()
                        break

                confidence = 0.55 if is_tentative else 0.88
                status = "uncertain" if is_tentative else "proposed"

                commitments.append({
                    "commitment_id": f"comm-{uuid.uuid4().hex[:8]}",
                    "statement": f"{action}" if role != "requested" else f"Complete: {action}",
                    "owner": default_owner or ("me" if role == "self" else "unassigned"),
                    "recipient": "team" if role == "self" else "me",
                    "deadline": deadline_str or None,
                    "source_ref": source_ref,
                    "evidence_quote": line,
                    "confidence": confidence,
                    "status": status,
                    "is_tentative": is_tentative,
                })
                break

    return commitments


def deduplicate_commitments(
    existing_commitments: list[dict[str, Any]],
    new_commitments: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Separates new commitments into novel proposals vs existing matches.
    Prevents duplicate task creation while preserving source citations.
    """
    novel: list[dict[str, Any]] = []
    matched: list[dict[str, Any]] = []

    for item in new_commitments:
        stmt = item["statement"].lower().strip()
        found_match = False
        for ex in existing_commitments:
            ex_stmt = ex.get("statement", "").lower().strip()
            # If word sets heavily overlap (Jaccard > 0.6)
            s1 = set(stmt.split())
            s2 = set(ex_stmt.split())
            if s1 and s2:
                sim = len(s1 & s2) / len(s1 | s2)
                if sim >= 0.6:
                    found_match = True
                    matched.append({"existing_id": ex.get("commitment_id"), "duplicate_candidate": item})
                    break

        if not found_match:
            novel.append(item)

    return novel, matched
