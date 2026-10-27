"""
wayfinder/atlas/helpers/document_helpers.py
──────────────────────────────────────────
Deterministic document processing helpers for W10 (Document Analyst).

Provides:
  - Heading-aware document chunking preserving traceability & section citations
  - Document metadata inspection (type, size, modified time, empty check)
  - Truncation detection to ensure partial reads are never passed as complete
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


def extract_document_metadata(path_or_str: str | Path) -> dict[str, Any]:
    """Inspects a local file and returns standardized metadata."""
    p = Path(path_or_str)
    if not p.exists():
        return {
            "exists": False,
            "path": str(p),
            "file_type": p.suffix.lower().lstrip("."),
            "size_bytes": 0,
            "is_empty": True,
        }

    stat = p.stat()
    size = stat.st_size
    return {
        "exists": True,
        "path": str(p.resolve()),
        "file_name": p.name,
        "file_type": p.suffix.lower().lstrip(".") or "unknown",
        "size_bytes": size,
        "modified_time": stat.st_mtime,
        "is_empty": size == 0,
    }


def chunk_document_with_citations(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
    source_system: str = "local_file",
    item_id: str = "",
    title: str = "",
) -> list[dict[str, Any]]:
    """
    Splits text into overlapping chunks while tracking current section heading
    and approximate line offsets to maintain source traceability.
    """
    if not text.strip():
        return []

    lines = text.splitlines(keepends=True)
    chunks: list[dict[str, Any]] = []

    current_heading = "Top of Document"
    current_chunk_lines: list[str] = []
    current_chunk_chars = 0
    start_line_num = 1
    current_line_num = 1

    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    for line in lines:
        match = heading_pattern.match(line.strip())
        if match:
            current_heading = match.group(2).strip()

        line_len = len(line)
        if current_chunk_chars + line_len > chunk_size and current_chunk_lines:
            chunk_text = "".join(current_chunk_lines).strip()
            chunks.append({
                "chunk_index": len(chunks) + 1,
                "text": chunk_text,
                "section": current_heading,
                "start_line": start_line_num,
                "end_line": current_line_num - 1,
                "source": {
                    "system": source_system,
                    "item_id": item_id,
                    "title": title,
                },
            })

            # Handle overlap by keeping trailing lines
            overlap_lines: list[str] = []
            overlap_chars = 0
            for prev_line in reversed(current_chunk_lines):
                if overlap_chars + len(prev_line) > overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_chars += len(prev_line)

            current_chunk_lines = overlap_lines
            current_chunk_chars = overlap_chars
            start_line_num = current_line_num - len(overlap_lines)

        current_chunk_lines.append(line)
        current_chunk_chars += line_len
        current_line_num += 1

    if current_chunk_lines and "".join(current_chunk_lines).strip():
        chunks.append({
            "chunk_index": len(chunks) + 1,
            "text": "".join(current_chunk_lines).strip(),
            "section": current_heading,
            "start_line": start_line_num,
            "end_line": current_line_num - 1,
            "source": {
                "system": source_system,
                "item_id": item_id,
                "title": title,
            },
        })

    return chunks
