"""Trusted read-only source sent to the existing managed Hermes interpreter."""

import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path

from run_agent import AIAgent
from tools.registry import registry

root = Path("/opt/hermes")
modules = {
    "delegation": "tools/delegate_tool.py",
    "scheduler": "tools/cronjob_tools.py",
    "mcp": "tools/mcp_tool.py",
    "reader": "tools/file_operations.py",
    "agent": "run_agent.py",
}
entries = []
for entry in registry.get_all_entries():
    raw = json.dumps(entry.schema, sort_keys=True, separators=(",", ":")).encode()
    entries.append(
        dict(
            tool_id=entry.name,
            toolset=entry.toolset,
            schema_sha256=hashlib.sha256(raw).hexdigest(),
            state="registered_not_probed",
        )
    )
result = dict(
    version=importlib.metadata.version("hermes-agent"),
    agent_parameters=sorted(inspect.signature(AIAgent).parameters),
    modules={
        name: dict(
            present=(root / rel).is_file(),
            sha256=hashlib.sha256((root / rel).read_bytes()).hexdigest(),
        )
        for name, rel in modules.items()
        if (root / rel).is_file()
    },
    tools=sorted(entries, key=lambda row: row["tool_id"]),
    dependency_checks="not run: checks may install or contact optional services",
)
print("WAYFINDER_RUNTIME=" + json.dumps(result, allow_nan=False))
