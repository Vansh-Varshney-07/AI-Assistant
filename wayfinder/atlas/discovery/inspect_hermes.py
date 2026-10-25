"""
wayfinder/atlas/discovery/inspect_hermes.py
───────────────────────────────────────────
Discovers the actual runtime capabilities registered in the Hermes agent
by introspecting its CLI and any available metadata endpoints.

Outputs: a list of raw capability dicts that build_index.py can consume.

Discovery strategy (in priority order):
  1. `hermes tools list --json`   — machine-readable tool list (if supported)
  2. `hermes tools list`          — text output; parsed with regex fallback
  3. Hermes config directory scan — reads any tools.json / manifest.json
  4. Manually verified manifest   — falls back to registry/tools.jsonl

All discovered entries are tagged with:
  - source: "hermes_runtime" | "hermes_config" | "manual_manifest"
  - availability.status: "verified" | "unverified" | "discovery_failed"
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path(__file__).parent.parent / "registry"
TOOLS_JSONL   = REGISTRY_DIR / "tools.jsonl"

# ── Hermes binary ────────────────────────────────────────────────────────────

def _hermes_bin() -> str | None:
    """Return the hermes binary path, or None if not on PATH."""
    return shutil.which("hermes")


# ── Strategy 1 & 2: CLI introspection ────────────────────────────────────────

def _run_hermes(*args: str, timeout: int = 10) -> tuple[int, str, str]:
    hermes = _hermes_bin()
    if not hermes:
        return -1, "", "hermes not found on PATH"
    try:
        result = subprocess.run(
            [hermes, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as exc:
        return -1, "", str(exc)


def _discover_via_cli_json() -> list[dict[str, Any]]:
    """Try `hermes tools list --json` for a structured response."""
    code, stdout, _ = _run_hermes("tools", "list", "--json")
    if code != 0 or not stdout.strip():
        return []
    try:
        data = json.loads(stdout)
        tools = data if isinstance(data, list) else data.get("tools", [])
        return [
            {
                "id": t.get("id") or t.get("name", "unknown"),
                "name": t.get("name", ""),
                "description": t.get("description", ""),
                "source": "hermes_runtime",
                "availability": {"status": "verified"},
                "raw": t,
            }
            for t in tools
        ]
    except json.JSONDecodeError:
        return []


def _discover_via_cli_text() -> list[dict[str, Any]]:
    """Fallback: parse `hermes tools list` plain-text output."""
    code, stdout, _ = _run_hermes("tools", "list")
    if code != 0 or not stdout.strip():
        return []

    tools = []
    # Expect lines like:  tool_name   - Description text
    for line in stdout.splitlines():
        m = re.match(r"^\s*([\w.]+)\s+-\s+(.+)$", line)
        if m:
            name, desc = m.group(1).strip(), m.group(2).strip()
            tools.append({
                "id": name,
                "name": name,
                "description": desc,
                "source": "hermes_runtime",
                "availability": {"status": "verified"},
            })
    return tools


# ── Strategy 3: Config directory scan ────────────────────────────────────────

def _discover_via_config_dir() -> list[dict[str, Any]]:
    """
    Look for a tools.json or manifest.json in common Hermes config locations.
    """
    search_paths = [
        Path.home() / ".hermes" / "tools.json",
        Path.home() / ".hermes" / "manifest.json",
        Path.home() / ".config" / "hermes" / "tools.json",
    ]
    for p in search_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                items = data if isinstance(data, list) else data.get("tools", [])
                return [
                    {
                        "id": t.get("id") or t.get("name", "unknown"),
                        "name": t.get("name", ""),
                        "description": t.get("description", ""),
                        "source": "hermes_config",
                        "availability": {"status": "unverified", "notes": f"from {p}"},
                        "raw": t,
                    }
                    for t in items
                ]
            except Exception:
                continue
    return []


# ── Strategy 4: Manual manifest fallback ─────────────────────────────────────

def _load_manual_manifest() -> list[dict[str, Any]]:
    """Load from the curated tools.jsonl registry as a last resort."""
    if not TOOLS_JSONL.exists():
        return []
    tools = []
    with TOOLS_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    t = json.loads(line)
                    t.setdefault("source", "manual_manifest")
                    t.setdefault("availability", {}).setdefault("status", "unverified")
                    tools.append(t)
                except json.JSONDecodeError:
                    continue
    return tools


# ── Deduplication ─────────────────────────────────────────────────────────────

def _deduplicate(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for t in tools:
        tid = t.get("id", t.get("name", "unknown"))
        if tid not in seen:
            seen[tid] = t
        else:
            # Prefer higher-confidence source
            priority = {"hermes_runtime": 0, "hermes_config": 1, "manual_manifest": 2}
            existing_p = priority.get(seen[tid].get("source", "manual_manifest"), 99)
            new_p      = priority.get(t.get("source", "manual_manifest"), 99)
            if new_p < existing_p:
                seen[tid] = t
    return list(seen.values())


# ── Main entry point ─────────────────────────────────────────────────────────

def discover_hermes_capabilities() -> list[dict[str, Any]]:
    """
    Run all discovery strategies in order, deduplicate results, and return
    a merged list of capability dicts ready for registry update / indexing.
    """
    tools: list[dict[str, Any]] = []

    print("[inspect_hermes] Strategy 1: hermes tools list --json")
    discovered = _discover_via_cli_json()
    if discovered:
        print(f"  ✓ Found {len(discovered)} tool(s) via JSON CLI")
        tools.extend(discovered)
    else:
        print("  ✗ No JSON output — trying text parse")
        discovered = _discover_via_cli_text()
        if discovered:
            print(f"  ✓ Found {len(discovered)} tool(s) via text CLI")
            tools.extend(discovered)
        else:
            print("  ✗ No CLI output")

    if not tools:
        print("[inspect_hermes] Strategy 3: config directory scan")
        discovered = _discover_via_config_dir()
        if discovered:
            print(f"  ✓ Found {len(discovered)} tool(s) in config dir")
            tools.extend(discovered)

    if not tools:
        print("[inspect_hermes] Strategy 4: manual manifest fallback")
        discovered = _load_manual_manifest()
        print(f"  ✓ Loaded {len(discovered)} tool(s) from manual manifest")
        tools.extend(discovered)

    tools = _deduplicate(tools)
    print(f"\n[inspect_hermes] Total unique capabilities discovered: {len(tools)}")
    return tools


if __name__ == "__main__":
    capabilities = discover_hermes_capabilities()
    out = json.dumps(capabilities, indent=2)
    print(out)

    # Optionally write to a discovery snapshot
    snapshot_path = REGISTRY_DIR / "snapshot_hermes.json"
    snapshot_path.write_text(out, encoding="utf-8")
    print(f"\nSnapshot saved → {snapshot_path}")
    sys.exit(0)
