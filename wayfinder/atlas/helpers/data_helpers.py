"""
wayfinder/atlas/helpers/data_helpers.py
──────────────────────────────────────
Deterministic tabular data inspection and calculation helpers for W11 (Data Analyst).

Guarantees:
  - Exact arithmetic via Python math/statistics, preventing LLM arithmetic hallucination
  - Detection of spreadsheet formula errors (#REF!, #DIV/0!, #N/A)
  - Type inference and missing value accounting
"""

from __future__ import annotations

import statistics
from typing import Any


FORMULA_ERRORS = {"#REF!", "#VALUE!", "#N/A", "#DIV/0!", "#NAME?", "#NUM!", "#NULL!"}


def inspect_tabular_schema(headers: list[str], rows: list[list[Any]]) -> dict[str, Any]:
    """Inspects columns, identifies inferred types, and counts missing values."""
    col_count = len(headers)
    total_rows = len(rows)
    columns_info: list[dict[str, Any]] = []

    for idx, name in enumerate(headers):
        vals = []
        missing_count = 0
        error_count = 0
        types_seen = set()

        for r in rows:
            if idx >= len(r) or r[idx] is None or r[idx] == "":
                missing_count += 1
                continue
            val = r[idx]
            str_val = str(val).strip()

            if str_val.upper() in FORMULA_ERRORS:
                error_count += 1
                types_seen.add("formula_error")
                continue

            # Type checking
            if isinstance(val, (int, float)):
                types_seen.add("numeric")
                vals.append(float(val))
            elif str_val.replace(".", "", 1).isdigit() or (str_val.startswith("-") and str_val[1:].replace(".", "", 1).isdigit()):
                types_seen.add("numeric")
                try:
                    vals.append(float(str_val))
                except ValueError:
                    types_seen.add("string")
            elif str_val.lower() in {"true", "false"}:
                types_seen.add("boolean")
            else:
                types_seen.add("string")

        inferred = "mixed" if len(types_seen) > 1 else (list(types_seen)[0] if types_seen else "empty")

        columns_info.append({
            "column_index": idx,
            "name": name,
            "inferred_type": inferred,
            "total_records": total_rows,
            "missing_count": missing_count,
            "formula_error_count": error_count,
            "types_detected": list(types_seen),
        })

    return {
        "column_count": col_count,
        "row_count": total_rows,
        "columns": columns_info,
        "duplicate_headers": len(headers) != len(set(headers)),
    }


def validate_data_quality(headers: list[str], rows: list[list[Any]]) -> list[dict[str, Any]]:
    """Identifies quality issues: ragged rows, duplicate rows, and formula errors."""
    issues: list[dict[str, Any]] = []
    expected_cols = len(headers)

    seen_rows = set()
    for row_idx, r in enumerate(rows):
        if len(r) != expected_cols:
            issues.append({
                "type": "ragged_row",
                "row_number": row_idx + 1,
                "message": f"Row has {len(r)} cells, expected {expected_cols}",
            })

        for col_idx, cell in enumerate(r):
            if str(cell).strip().upper() in FORMULA_ERRORS:
                issues.append({
                    "type": "formula_error",
                    "row_number": row_idx + 1,
                    "column": headers[col_idx] if col_idx < len(headers) else str(col_idx),
                    "value": str(cell),
                })

        row_tuple = tuple(r)
        if row_tuple in seen_rows:
            issues.append({
                "type": "duplicate_row",
                "row_number": row_idx + 1,
                "message": "Row content is an exact duplicate of a previous row",
            })
        else:
            seen_rows.add(row_tuple)

    return issues


def calculate_column_stats(rows: list[list[Any]], col_index: int) -> dict[str, Any]:
    """Calculates statistical summary for numeric column values safely."""
    nums: list[float] = []
    null_count = 0

    for r in rows:
        if col_index >= len(r) or r[col_index] is None or r[col_index] == "":
            null_count += 1
            continue
        try:
            val = float(str(r[col_index]).replace(",", "").strip())
            nums.append(val)
        except (ValueError, TypeError):
            null_count += 1

    if not nums:
        return {
            "valid_count": 0,
            "null_count": null_count,
            "sum": 0.0,
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
        }

    return {
        "valid_count": len(nums),
        "null_count": null_count,
        "sum": sum(nums),
        "mean": round(statistics.mean(nums), 4),
        "median": round(statistics.median(nums), 4),
        "min": min(nums),
        "max": max(nums),
    }
