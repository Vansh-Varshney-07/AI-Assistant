"""
wayfinder/atlas/discovery/inspect_plugins.py
─────────────────────────────────────────────
Collects metadata about every installed Hermes plugin and cross-references
them with the tool registry to detect new or missing tool registrations.

For each plugin it records:
  - Plugin ID and name
  - Installation status (installed / not_installed / unknown)
  - Discovery method (cli_list | manifest_file | manual_declared)
  - Tools contributed by this plugin (cross-referenced with tools.jsonl)
  - Whether those tools are registered in the Atlas registry

Output: wayfinder/atlas/registry/snapshot_plugins.json
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

# ── Known plugins (manually declared baseline) ────────────────────────────────
# Add new plugins here when they are not auto-discoverable via CLI.
KNOWN_PLUGINS: list[dict[str, Any]] = [
    {
        "id": "whatsapp-agent-platform",
        "display_name": "WhatsApp Agent Platform (Personal Assistant Adapter)",
        "adapter_type": "messaging_platform_adapter",
        "channel_scope": "personal_assistant",
        "restriction": "Meta restricts replies to agent creator; not for customer-facing business bot",
        "install_cmd": "hermes plugins install whatsapp-agent-platform",
        "tools_contributed": [
            "whatsapp.receive_event",
            "whatsapp.reply_text",
            "whatsapp.send_media",
            "whatsapp.process_voice",
            "whatsapp.proactive_notify",
            "whatsapp.process_reaction",
        ],
        "source": "manual_declared",
    },
    {
        "id": "whatsapp-cloud-api",
        "display_name": "WhatsApp Business Cloud API (Planned)",
        "adapter_type": "business_cloud_api",
        "channel_scope": "business_messaging",
        "restriction": "Requires Meta Business credentials and verified business phone number",
        "install_cmd": "configure via Meta Cloud API webhook + credentials",
        "tools_contributed": [
            "whatsapp.biz_receive_message",
            "whatsapp.biz_send_reply",
            "whatsapp.biz_send_template",
        ],
        "source": "manual_declared",
    },
    {
        "id": "tavily",
        "display_name": "Tavily Search & Research",
        "install_cmd": "npx skills add tavily-ai/skills --skill '*' --global --yes",
        "tools_contributed": [
            "tavily_search",
            "tavily_extract",
            "tavily_research",
            "tavily_map",
            "tavily_crawl",
            "tavily_dynamic_search",
        ],
        "source": "manual_declared",
    },
]


# ── Hermes CLI helpers ────────────────────────────────────────────────────────

def _hermes_bin() -> str | None:
    return shutil.which("hermes")


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


# ── Strategy 1: hermes plugins list ──────────────────────────────────────────

def _discover_via_cli() -> list[dict[str, Any]]:
    """Try `hermes plugins list --json` then plain text fallback."""
    code, stdout, _ = _run_hermes("plugins", "list", "--json")
    if code == 0 and stdout.strip():
        try:
            data = json.loads(stdout)
            plugins = data if isinstance(data, list) else data.get("plugins", [])
            return [
                {
                    "id": p.get("id") or p.get("name", "unknown"),
                    "display_name": p.get("name", ""),
                    "version": p.get("version", ""),
                    "status": p.get("status", "installed"),
                    "source": "cli_list",
                    "raw": p,
                }
                for p in plugins
            ]
        except json.JSONDecodeError:
            pass

    # Plain-text fallback
    code, stdout, _ = _run_hermes("plugins", "list")
    if code != 0 or not stdout.strip():
        return []

    plugins = []
    for line in stdout.splitlines():
        m = re.match(r"^\s*([\w\-]+)\s+(.+)?$", line)
        if m:
            plugins.append({
                "id": m.group(1).strip(),
                "display_name": m.group(2).strip() if m.group(2) else "",
                "status": "installed",
                "source": "cli_list",
            })
    return plugins


# ── Registry cross-reference ──────────────────────────────────────────────────

def _load_registered_tool_ids() -> set[str]:
    if not TOOLS_JSONL.exists():
        return set()
    ids: set[str] = set()
    with TOOLS_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    t = json.loads(line)
                    if "id" in t:
                        ids.add(t["id"])
                    for alias in t.get("aliases", []):
                        ids.add(alias)
                except json.JSONDecodeError:
                    pass
    return ids


def _check_plugin_status(plugin_id: str, cli_installed_ids: set[str]) -> str:
    if plugin_id in cli_installed_ids:
        return "installed"
    hermes = _hermes_bin()
    if not hermes:
        return "unknown"
    return "not_installed"


# ── Main ──────────────────────────────────────────────────────────────────────

def inspect_plugins() -> dict[str, Any]:
    print("[inspect_plugins] Discovering installed plugins via CLI…")
    cli_plugins = _discover_via_cli()
    cli_installed_ids = {p["id"] for p in cli_plugins}

    registered_tool_ids = _load_registered_tool_ids()
    print(f"  Registry contains {len(registered_tool_ids)} tool IDs")

    # Merge CLI-discovered plugins with the known-plugin baseline
    merged: dict[str, dict[str, Any]] = {}

    for p in cli_plugins:
        merged[p["id"]] = {**p, "status": "installed"}

    for kp in KNOWN_PLUGINS:
        pid = kp["id"]
        if pid not in merged:
            status = _check_plugin_status(pid, cli_installed_ids)
            merged[pid] = {**kp, "status": status}
        else:
            # Enrich CLI record with manually declared metadata
            merged[pid].update({k: v for k, v in kp.items() if k not in merged[pid]})

    # Cross-reference tools
    unregistered_tools: list[str] = []
    for plugin in merged.values():
        contributed = plugin.get("tools_contributed", [])
        plugin["tools_in_registry"] = [t for t in contributed if t in registered_tool_ids]
        plugin["tools_missing_from_registry"] = [t for t in contributed if t not in registered_tool_ids]
        unregistered_tools.extend(plugin["tools_missing_from_registry"])

    result = {
        "plugin_count": len(merged),
        "installed": [p["id"] for p in merged.values() if p.get("status") == "installed"],
        "not_installed": [p["id"] for p in merged.values() if p.get("status") == "not_installed"],
        "unknown": [p["id"] for p in merged.values() if p.get("status") == "unknown"],
        "unregistered_tools": list(set(unregistered_tools)),
        "plugins": list(merged.values()),
    }

    print(f"\n[inspect_plugins] Summary:")
    print(f"  Plugins total:     {result['plugin_count']}")
    print(f"  Installed:         {result['installed']}")
    print(f"  Not installed:     {result['not_installed']}")
    if unregistered_tools:
        print(f"  [!] Tools not in registry: {list(set(unregistered_tools))}")

    return result


if __name__ == "__main__":
    data = inspect_plugins()
    out = json.dumps(data, indent=2)
    print("\n" + out)

    snapshot_path = REGISTRY_DIR / "snapshot_plugins.json"
    snapshot_path.write_text(out, encoding="utf-8")
    print(f"\nSnapshot saved -> {snapshot_path}")
    sys.exit(0)
