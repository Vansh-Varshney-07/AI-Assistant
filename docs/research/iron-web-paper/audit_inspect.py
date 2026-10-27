"""Read-only summaries of existing artifacts; never imports the application."""
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path.cwd()

if sys.argv[1] == "artifacts":
    for path in sorted((ROOT / "docs").rglob("*.csv")):
        if "research" in path.parts:
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            outcomes = {k: dict(Counter(str(r.get(k, "")) for r in rows))
                        for k in (reader.fieldnames or [])
                        if k.lower() in {"outcome", "result", "status", "passed", "test_result"}}
        print(json.dumps({"file": path.relative_to(ROOT).as_posix(), "rows": len(rows),
                          "fields": reader.fieldnames, "outcomes": outcomes,
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, ensure_ascii=False))
    for path in sorted((ROOT / "docs").rglob("*.json")):
        if "research" in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            shape = ({k: (len(v) if isinstance(v, (list, dict)) else type(v).__name__)
                      for k, v in data.items()} if isinstance(data, dict) else {"list_length": len(data)})
            print(json.dumps({"file": path.relative_to(ROOT).as_posix(), "shape": shape}, ensure_ascii=False))
        except (ValueError, OSError) as error:
            print(json.dumps({"file": str(path), "error": type(error).__name__}))
elif sys.argv[1] == "ast":
    for name in sys.argv[2:]:
        path = ROOT / name
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        entries = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                calls = sorted({ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)})
                entries.append({"function": node.name, "line": node.lineno, "end": node.end_lineno,
                                "calls": calls})
        print(json.dumps({"file": name, "functions": entries}, ensure_ascii=False))
elif sys.argv[1] == "json-shape":
    for name in sys.argv[2:]:
        path = ROOT / name
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        def shape(value, depth=0):
            if depth > 2:
                return type(value).__name__
            if isinstance(value, dict):
                return {k: shape(v, depth+1) for k, v in value.items()}
            if isinstance(value, list):
                return {"length": len(value), "first_shape": shape(value[0], depth+1) if value else None}
            return type(value).__name__
        print(json.dumps({"file": name, "shape": shape(data)}, ensure_ascii=False))
