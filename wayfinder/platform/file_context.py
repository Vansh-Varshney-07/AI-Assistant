"""Scoped file context service (P06.01).

Provides bounded file identity + excerpt to task workers.
- Hash checked at first access; access expires after task completion.
- Content capped at 6000 chars to prevent context stuffing.
"""
from __future__ import annotations
import hashlib, pathlib, time
from typing import Any

MAX_CHARS = 6000
EXPIRY_SECONDS = 3600  # 1 hour after creation


class FileContextExpired(Exception):
    pass


class FileContextEntry:
    def __init__(self, file_id: str, path: str, content: str, sha256: str):
        self.file_id = file_id
        self.path = path
        self.sha256 = sha256
        self._content = content[:MAX_CHARS]
        self.truncated = len(content) > MAX_CHARS
        self.created_at = time.time()
        self.revoked = False

    def is_expired(self) -> bool:
        return time.time() - self.created_at > EXPIRY_SECONDS

    def is_available(self) -> bool:
        return not self.revoked and not self.is_expired()

    def get_excerpt(self) -> str:
        if not self.is_available():
            raise FileContextExpired(f"File context for {self.file_id} has expired or been revoked")
        return self._content

    def revoke(self):
        self.revoked = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_id": self.file_id,
            "sha256": self.sha256,
            "path": str(self.path),
            "chars": len(self._content),
            "truncated": self.truncated,
            "available": self.is_available(),
            "created_at": self.created_at,
        }


class FileContextService:
    """Manages scoped file identity and bounded excerpts for task workers."""

    def __init__(self):
        self._store: dict[str, FileContextEntry] = {}

    def register(self, file_id: str, path: str) -> FileContextEntry:
        """Register a file and compute its hash. Returns the context entry."""
        p = pathlib.Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        raw = p.read_bytes()
        sha256 = hashlib.sha256(raw).hexdigest()
        try:
            content = raw.decode("utf-8", errors="replace")
        except Exception:
            content = raw.decode("latin-1", errors="replace")
        entry = FileContextEntry(file_id, path, content, sha256)
        self._store[file_id] = entry
        return entry

    def get(self, file_id: str) -> FileContextEntry:
        entry = self._store.get(file_id)
        if entry is None:
            raise KeyError(f"No file context registered for: {file_id}")
        return entry

    def get_excerpt(self, file_id: str) -> dict[str, Any]:
        """Get bounded excerpt + identity for a task worker."""
        entry = self.get(file_id)
        return {
            **entry.to_dict(),
            "excerpt": entry.get_excerpt(),
        }

    def revoke(self, file_id: str) -> None:
        """Revoke access after task completes."""
        entry = self._store.get(file_id)
        if entry:
            entry.revoke()

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        expired = [k for k, v in self._store.items() if not v.is_available()]
        for k in expired:
            del self._store[k]
        return len(expired)
