"""
wayfinder/atlas/indexing/retrieval.py
──────────────────────────────────────
Finds relevant capabilities (tools and skills) for a natural-language request.

This module is the interface between a user request / orchestrator query and
the Atlas vector index. It returns ranked candidates that the orchestrator
then validates against the registry and policy layer before planning a workflow.

Key design principle:
  Vector similarity → DISCOVERY only.
  The orchestrator must still check availability.status and permissions
  before treating any result as executable.

Usage:
    python -m wayfinder.atlas.indexing.retrieval "research AI memory developments"
    python -m wayfinder.atlas.indexing.retrieval "send a summary on WhatsApp"
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

INDEX_DIR    = Path(__file__).parent.parent / "_index"
REGISTRY_DIR = Path(__file__).parent.parent / "registry"
POLICY_FILE  = Path(__file__).parent.parent / "policies" / "tool_permissions.yaml"


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class CapabilityCandidate:
    id: str
    name: str = ""
    type: str = "tool"          # "tool" | "skill"
    provider: str = ""
    description: str = ""
    score: float = 0.0          # cosine similarity
    status: str = "unverified"  # from registry
    risk: str = "unknown"
    approval_required: bool = False
    source_plugin: str = ""
    capabilities: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def is_executable(self) -> bool:
        """True only when the registry marks this capability as verified."""
        return self.status == "verified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "provider": self.provider,
            "score": round(self.score, 4),
            "status": self.status,
            "risk": self.risk,
            "approval_required": self.approval_required,
            "executable": self.is_executable,
            "source_plugin": self.source_plugin,
        }


# ── ChromaDB retrieval ────────────────────────────────────────────────────────

def _get_collection(index_dir: Path):
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    except ImportError:
        print(
            "chromadb not installed. Run:\n"
            "  pip install chromadb sentence-transformers"
        )
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(index_dir))
    ef = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
    return client.get_or_create_collection(name="atlas_tools", embedding_function=ef)


# ── Manual JSONL fallback (no vector DB needed) ───────────────────────────────

def _keyword_search_jsonl(query: str, top_k: int = 5) -> list[CapabilityCandidate]:
    """
    Simple keyword overlap fallback when the vector index is not built.
    Scores by fraction of query tokens found in the record's search_text.
    """
    results: list[CapabilityCandidate] = []
    tokens = set(query.lower().split())

    for jsonl_path in [
        REGISTRY_DIR / "tools.jsonl",
        REGISTRY_DIR / "skills.jsonl",
    ]:
        if not jsonl_path.exists():
            continue
        with jsonl_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    t = json.loads(line)
                except json.JSONDecodeError:
                    continue

                haystack = " ".join(filter(None, [
                    t.get("indexing", {}).get("search_text", ""),
                    t.get("description", ""),
                    t.get("name", ""),
                    " ".join(t.get("capabilities", [])),
                    " ".join(t.get("use_cases", [])),
                ])).lower()

                matched = sum(1 for tok in tokens if tok in haystack)
                score = matched / max(len(tokens), 1)

                if score > 0:
                    perms = t.get("permissions", {})
                    results.append(CapabilityCandidate(
                        id=t.get("id", ""),
                        name=t.get("name", ""),
                        type=t.get("type", "tool"),
                        provider=t.get("provider", ""),
                        description=t.get("description", ""),
                        score=score,
                        status=t.get("availability", {}).get("status", "unverified"),
                        risk=perms.get("risk", "unknown"),
                        approval_required=perms.get("approval_required", False),
                        source_plugin=t.get("source_plugin", ""),
                        capabilities=t.get("capabilities", []),
                    ))

    results.sort(key=lambda c: c.score, reverse=True)
    return results[:top_k]


# ── Main retrieval function ───────────────────────────────────────────────────

def retrieve(
    query: str,
    top_k: int = 5,
    filter_by_type: str | None = None,       # "tool" | "skill" | None
    filter_by_status: str | None = None,     # "verified" | "unverified" | None
    index_dir: Path = INDEX_DIR,
) -> list[CapabilityCandidate]:
    """
    Find the top-k capabilities most relevant to `query`.

    Falls back to keyword search if the vector index is not built yet.
    Results are always sorted by descending similarity score.

    Important: results are CANDIDATES only. The orchestrator must validate
    availability.status and permissions before execution.
    """
    candidates: list[CapabilityCandidate] = []

    # Try vector search first
    if index_dir.exists():
        try:
            col = _get_collection(index_dir)
            where: dict[str, Any] = {}
            if filter_by_type:
                where["type"] = {"$eq": filter_by_type}

            query_kwargs: dict[str, Any] = {
                "query_texts": [query],
                "n_results": top_k * 2,  # over-fetch for post-filter
            }
            if where:
                query_kwargs["where"] = where

            res = col.query(**query_kwargs)
            ids      = res["ids"][0]
            metas    = res["metadatas"][0]
            distances = res["distances"][0]

            for rid, meta, dist in zip(ids, metas, distances):
                score = 1.0 - dist  # cosine distance → similarity
                c = CapabilityCandidate(
                    id=rid,
                    name=meta.get("name", rid),
                    type=meta.get("type", "tool"),
                    provider=meta.get("provider", ""),
                    score=score,
                    status=meta.get("status", "unverified"),
                    risk=meta.get("risk", "unknown"),
                    approval_required=bool(meta.get("approval_required", False)),
                    source_plugin=meta.get("source_plugin", ""),
                    capabilities=json.loads(meta["capabilities"])
                        if isinstance(meta.get("capabilities"), str)
                        else meta.get("capabilities", []),
                )
                candidates.append(c)
        except Exception as exc:
            print(f"[retrieval] Vector search error ({exc}); falling back to keyword search")
            candidates = _keyword_search_jsonl(query, top_k=top_k * 2)
    else:
        print("[retrieval] Index not found — using keyword fallback (run build_index.py to enable vector search)")
        candidates = _keyword_search_jsonl(query, top_k=top_k * 2)

    # Post-filter by status
    if filter_by_status:
        candidates = [c for c in candidates if c.status == filter_by_status]

    # Sort and trim
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_k]


# ── Orchestrator-friendly helper ──────────────────────────────────────────────

def retrieve_for_workflow(query: str, top_k: int = 8) -> dict[str, Any]:
    """
    Returns a structured payload the orchestrator can consume directly.

    Separates results into:
      - executable_candidates: verified tools ready to use
      - unverified_candidates: tools that need availability/permission check
    """
    candidates = retrieve(query, top_k=top_k)
    executable = [c for c in candidates if c.is_executable]
    unverified = [c for c in candidates if not c.is_executable]

    return {
        "query": query,
        "total_candidates": len(candidates),
        "executable_candidates": [c.to_dict() for c in executable],
        "unverified_candidates": [c.to_dict() for c in unverified],
        "note": (
            "Vector similarity is for discovery only. "
            "Orchestrator must validate availability and permissions before execution."
        ),
    }


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "research a topic and summarise it"
    print(f"[retrieval] Query: {query!r}\n")

    payload = retrieve_for_workflow(query)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
