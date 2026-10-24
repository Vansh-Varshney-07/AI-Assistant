"""Durable local memory-space directory. IDs are scopes, not authentication."""

from pathlib import Path
from contextlib import contextmanager
import re
import sqlite3
import time
import uuid


def validate_space_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", value):
        raise ValueError(
            "Memory space ID must contain 1–40 letters, digits, underscores or hyphens."
        )
    return value


class SpaceDirectory:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS spaces (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at REAL NOT NULL)"
            )

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            with db:
                yield db
        finally:
            db.close()

    def ensure(self, space_id, name=None, *, create_only=False):
        validate_space_id(space_id)
        if name is None:
            name = space_id
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
            raise ValueError("Space name must contain 1–100 characters.")
        with self.connect() as db:
            try:
                db.execute(
                    "INSERT INTO spaces VALUES (?,?,?)"
                    if create_only
                    else "INSERT OR IGNORE INTO spaces VALUES (?,?,?)",
                    (space_id, name.strip(), time.time()),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(
                    "That memory space ID already exists. Switch to it or choose another ID."
                ) from error
        return self.require(space_id)

    def create(self, body):
        if not isinstance(body, dict) or set(body) - {"memory_space_id", "name"}:
            raise ValueError("Use only name and optional memory_space_id.")
        return self.ensure(
            body.get("memory_space_id", "space_" + uuid.uuid4().hex),
            body.get("name"),
            create_only=True,
        )

    def require(self, space_id):
        validate_space_id(space_id)
        with self.connect() as db:
            row = db.execute(
                "SELECT id,name,created_at FROM spaces WHERE id=?", (space_id,)
            ).fetchone()
        if row is None:
            raise ValueError("Unknown memory space ID. Create the space first.")
        return dict(zip(("memory_space_id", "name", "created_at"), row))

    def list(self):
        with self.connect() as db:
            return [
                dict(zip(("memory_space_id", "name", "created_at"), row))
                for row in db.execute(
                    "SELECT id,name,created_at FROM spaces ORDER BY created_at DESC,id"
                )
            ]
