"""
wayfinder/atlas/indexing/build_index.py
───────────────────────────────────────
Converts the verified tool and skill metadata from the Atlas registry into
vector-search documents, one document per tool or skill.

Vector backend: ChromaDB (local, persistent) — zero-infra for local dev.
Embedding model: sentence-transformers/all-MiniLM-L6-v2 (CPU-friendly).

To swap backends, implement the VectorStore protocol and pass it to
build_index().

Usage:
    python -m wayfinder.atlas.indexing.build_index
    python -m wayfinder.atlas.indexing.build_index --reset
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Protocol

REGISTRY_DIR = Path(__file__).parent.parent / "registry"
TOOLS_JSONL   = REGISTRY_DIR / "tools.jsonl"
SKILLS_JSONL  = REGISTRY_DIR / "skills.jsonl"
INDEX_DIR     = Path(__file__).parent.parent / "_index"


# ── VectorStore protocol (swap-friendly) ──────────────────────────────────────

class VectorStore(Protocol):
    def upsert(self, doc_id: str, text: str, metadata: dict[str, Any]) -> None: ...
    def delete(self, doc_id: str) -> None: ...
    def reset(self) -> None: ...
    def count(self) -> int: ...


# ── ChromaDB backend ─────────────────────────────────────────────────────────

class ChromaVectorStore:
    """Local persistent ChromaDB store."""

    def __init__(self, persist_dir: Path, collection_name: str = "atlas_tools"):
        try:
            import chromadb
            from chromadb.utils.embedding_functions import (
                SentenceTransformerEmbeddingFunction,
            )
        except ImportError:
            print(
                "chromadb not installed. Run:\n"
                "  pip install chromadb sentence-transformers\n"
                "or add them to requirements.txt"
            )
            sys.exit(1)

        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        ef = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        self._col = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, doc_id: str, text: str, metadata: dict[str, Any]) -> None:
        # ChromaDB requires all metadata values to be str/int/float/bool
        safe_meta = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                     for k, v in metadata.items()}
        self._col.upsert(ids=[doc_id], documents=[text], metadatas=[safe_meta])

    def delete(self, doc_id: str) -> None:
        self._col.delete(ids=[doc_id])

    def reset(self) -> None:
        self._col.delete(where={"id": {"$ne": "__never__"}})

    def count(self) -> int:
        return self._col.count()


# ── Document builder ──────────────────────────────────────────────────────────

def _tool_to_doc(tool: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """Convert a tool record to (doc_id, search_text, metadata)."""
    doc_id = tool["id"]

    # Use explicit search_text if provided; otherwise synthesise from fields
    search_text = tool.get("indexing", {}).get("search_text", "")
    if not search_text:
        parts = [tool.get("name", ""), tool.get("description", "")]
        parts += tool.get("use_cases", [])
        parts += tool.get("capabilities", [])
        search_text = " ".join(filter(None, parts))

    metadata = {
        "id":           doc_id,
        "type":         tool.get("type", "tool"),
        "provider":     tool.get("provider", ""),
        "risk":         tool.get("permissions", {}).get("risk", "unknown"),
        "status":       tool.get("availability", {}).get("status", "unverified"),
        "source_plugin":tool.get("source_plugin", ""),
        "capabilities": tool.get("capabilities", []),
        "approval_required": tool.get("permissions", {}).get("approval_required", False),
    }
    return doc_id, search_text, metadata


def _skill_to_doc(skill: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """Convert a skill record to (doc_id, search_text, metadata)."""
    doc_id = skill["id"]

    parts = [skill.get("name", ""), skill.get("description", "")]
    parts += skill.get("required_tools", [])
    parts += [str(v) for v in skill.get("inputs", {}).values() if isinstance(v, str)]
    search_text = " ".join(filter(None, parts))

    metadata = {
        "id":                    doc_id,
        "type":                  "skill",
        "provider":              skill.get("provider", ""),
        "required_tools":        skill.get("required_tools", []),
        "optional_tools":        skill.get("optional_tools", []),
        "performs_external_writes": skill.get("performs_external_writes", False),
        "approval_required":     skill.get("approval_required", False),
    }
    return doc_id, search_text, metadata


# ── JSONL loaders ─────────────────────────────────────────────────────────────

def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    if not path.exists():
        print(f"  [warn] {path} not found — skipping")
        return records
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  [warn] Parse error on line {i} of {path.name}: {e}")
    return records


# ── Main build ────────────────────────────────────────────────────────────────

def build_index(store: VectorStore, reset: bool = False) -> None:
    if reset:
        print("[build_index] Resetting existing index…")
        store.reset()

    tools  = _load_jsonl(TOOLS_JSONL)
    skills = _load_jsonl(SKILLS_JSONL)

    indexed = 0
    skipped = 0

    print(f"\n[build_index] Indexing {len(tools)} tools…")
    for tool in tools:
        if not tool.get("indexing", {}).get("enabled", True):
            skipped += 1
            continue
        doc_id, text, meta = _tool_to_doc(tool)
        store.upsert(doc_id, text, meta)
        print(f"  ✓ {doc_id}")
        indexed += 1

    print(f"\n[build_index] Indexing {len(skills)} skills…")
    for skill in skills:
        doc_id, text, meta = _skill_to_doc(skill)
        store.upsert(doc_id, text, meta)
        print(f"  ✓ {doc_id}")
        indexed += 1

    print(f"\n[build_index] Done. Indexed={indexed}, Skipped={skipped}")
    print(f"  Total documents in store: {store.count()}")


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build Wayfinder Atlas vector index")
    parser.add_argument("--reset", action="store_true", help="Wipe and rebuild the index")
    parser.add_argument("--index-dir", default=str(INDEX_DIR), help="Directory for ChromaDB persistence")
    args = parser.parse_args()

    store = ChromaVectorStore(persist_dir=Path(args.index_dir))
    build_index(store, reset=args.reset)


if __name__ == "__main__":
    main()
