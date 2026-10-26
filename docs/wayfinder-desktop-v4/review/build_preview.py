"""Render trusted offline design inputs; no backend, browser or package install."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
serialized = json.dumps(manifest, ensure_ascii=True).replace("<", "\\u003c")
script = (root / "preview.js").read_text(encoding="utf-8")
assert "</script" not in script.lower()
template = (root / "preview.template.html").read_text(encoding="utf-8")
assert template.count("{{MANIFEST_JSON}}") == template.count("{{PREVIEW_SCRIPT}}") == 1
output = template.replace("{{MANIFEST_JSON}}", serialized).replace("{{PREVIEW_SCRIPT}}", script)
(root / "preview.html").write_text(output, encoding="utf-8")
print("Built offline preview from the authoritative design manifest")
