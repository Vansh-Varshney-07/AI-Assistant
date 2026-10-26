"""Explicit, expiring file grants. No model is allowed to choose a host path."""

from dataclasses import dataclass
import ctypes
import fnmatch
import hashlib
import os
from pathlib import Path
import secrets
import stat
from threading import RLock
import time

MAX_BYTES = 2 * 1024 * 1024
TEXT_TYPES = {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".py", ".log"}
DOCUMENT_TYPES = TEXT_TYPES | {".docx", ".xlsx", ".pdf"}
PRIVATE_NAMES = {"credentials", "credentials.json", "auth.json", "app.sqlite3"}


def private(path):
    return (
        any(
            p.startswith(".") or p.casefold() in {"secrets", "runtime", "__pycache__"}
            for p in path.parts
        )
        or path.name.casefold() in PRIVATE_NAMES
    )


def reparse(info):
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400
    )


def version(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def checked_path(value):
    raw = os.fspath(value)
    # Reject alternate streams, device paths and network shares before resolving.
    if raw.startswith(("\\\\", "//", "\\??\\")) or ":" in raw[2:]:
        raise ValueError("Network, device and alternate-stream paths are unavailable.")
    path = Path(os.path.abspath(raw))
    for part in [*reversed(path.parents), path]:
        if reparse(part.lstat()):
            raise ValueError("Symbolic links and reparse points are unavailable.")
    return path


def open_checked(path, root):
    """Open without following links, then validate the opened object before reading."""
    checked_path(path)
    relative = path.relative_to(root)
    if os.name != "nt":
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for component in relative.parts[:-1]:
                child = os.open(
                    component,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=directory,
                )
                os.close(directory)
                directory = child
            fd = os.open(
                relative.name,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=directory,
            )
        finally:
            os.close(directory)
        return os.fdopen(fd, "rb")
    from ctypes import wintypes
    import msvcrt

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    final = kernel.GetFinalPathNameByHandleW
    final.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    final.restype = wintypes.DWORD
    handle = create(str(path), 0x80000000, 1, None, 3, 0x00200000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ValueError("File is unavailable or in use.")
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        count = final(handle, buffer, len(buffer), 0)
        if not 0 < count < len(buffer):
            raise ValueError("Opened file identity could not be checked.")
        actual = buffer.value
        if actual.startswith("\\\\?\\"):
            actual = actual[4:]
        if os.path.normcase(actual) != os.path.normcase(str(path)):
            raise ValueError("Opened file differs from the authorized path.")
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        handle = None
        return os.fdopen(fd, "rb")
    finally:
        if handle is not None:
            close(handle)


@dataclass
class Grant:
    scope: tuple
    root: Path
    identity: tuple
    expires: float
    file_only: str | None = None


class FileBroker:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.grants, self.references = {}, {}
        self.lock = RLock()

    def grant(self, scope, path, ttl=900):
        with self.lock:
            if len(self.grants) >= 128:
                self._expire()
                if len(self.grants) >= 128:
                    raise ValueError("Revoke an existing grant before adding another.")
            path = checked_path(path)
            if private(path):
                raise ValueError(
                    "Private application and credential paths are unavailable."
                )
            info = path.stat()
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise ValueError("Choose a regular file or directory.")
            root = path if path.is_dir() else path.parent
            gid = secrets.token_urlsafe(24)
            self.grants[gid] = Grant(
                tuple(scope),
                root,
                version(root.stat())[:2],
                self.clock() + ttl,
                None if path.is_dir() else path.name,
            )
            return dict(
                id=gid,
                name=path.name,
                expires_in=ttl,
                access="read",
                file_only=not path.is_dir(),
            )

    def _expire(self):
        for gid in list(self.grants):
            if self.grants[gid].expires <= self.clock():
                self.revoke(self.grants[gid].scope, gid)

    def _grant(self, scope, gid):
        grant = self.grants.get(gid)
        if not grant or grant.scope != tuple(scope) or grant.expires <= self.clock():
            raise ValueError("File grant expired, revoked or unavailable in this task.")
        root = checked_path(grant.root)
        if version(root.stat())[:2] != grant.identity:
            raise ValueError("Authorized directory was replaced.")
        return grant

    def revoke(self, scope, gid):
        with self.lock:
            grant = self.grants.get(gid)
            if grant and grant.scope != tuple(scope):
                raise ValueError("Grant unavailable in this task.")
            self.grants.pop(gid, None)
            self.references = {k: v for k, v in self.references.items() if v[0] != gid}
            return dict(revoked=True)

    def discover(self, scope, gid, pattern="*", limit=50):
        if not isinstance(pattern, str) or len(pattern) > 150 or not 1 <= limit <= 100:
            raise ValueError("Use a short filename pattern and a limit of 1–100.")
        with self.lock:
            grant = self._grant(scope, gid)
            if grant.file_only:
                path = checked_path(grant.root / grant.file_only)
                info = path.stat()
                if not stat.S_ISREG(info.st_mode):
                    raise ValueError("Selected file was replaced.")
                if not fnmatch.fnmatchcase(path.name.casefold(), pattern.casefold()):
                    return dict(
                        worker="W34",
                        files=[],
                        visited=1,
                        skipped=0,
                        bounded=True,
                        possibly_truncated=False,
                    )
                if len(self.references) >= 1000:
                    raise ValueError("Revoke file grants to clear old search results.")
                ref = secrets.token_urlsafe(24)
                self.references[ref] = (gid, path, version(info))
                return dict(
                    worker="W34",
                    files=[
                        dict(
                            id=ref,
                            name=path.name,
                            bytes=info.st_size,
                            supported=path.suffix.lower() in DOCUMENT_TYPES,
                        )
                    ],
                    visited=1,
                    skipped=0,
                    bounded=True,
                    possibly_truncated=False,
                )
            rows, visited, skipped = [], 0, 0
            pending = [grant.root]
            while pending and visited < 3000 and len(rows) < limit:
                directory = pending.pop()
                checked_path(directory)
                try:
                    with os.scandir(directory) as entries:
                        # Never materialize an unbounded directory listing.
                        for item in entries:
                            visited += 1
                            if visited > 3000 or len(rows) >= limit:
                                break
                            path = Path(item.path)
                            rel = path.relative_to(grant.root)
                            if private(rel) or (
                                grant.file_only and str(rel) != grant.file_only
                            ):
                                skipped += 1
                                continue
                            # Windows DirEntry.stat can omit the file identity; use lstat
                            # so the later handle check compares the same identity fields.
                            info = path.lstat()
                            if reparse(info):
                                skipped += 1
                                continue
                            if stat.S_ISDIR(info.st_mode):
                                if len(rel.parts) < 8:
                                    pending.append(path)
                                continue
                            if not stat.S_ISREG(
                                info.st_mode
                            ) or not fnmatch.fnmatchcase(
                                path.name.casefold(), pattern.casefold()
                            ):
                                continue
                            if len(self.references) >= 1000:
                                raise ValueError(
                                    "Revoke file grants to clear old search results."
                                )
                            ref = secrets.token_urlsafe(24)
                            self.references[ref] = (gid, path, version(info))
                            rows.append(
                                dict(
                                    id=ref,
                                    name=str(rel),
                                    bytes=info.st_size,
                                    supported=path.suffix.lower() in DOCUMENT_TYPES,
                                )
                            )
                except PermissionError:
                    skipped += 1
            self._grant(scope, gid)
            return dict(
                worker="W34",
                files=rows,
                visited=visited,
                skipped=skipped,
                bounded=True,
                possibly_truncated=bool(pending)
                or visited >= 3000
                or len(rows) >= limit,
            )

    def read(self, scope, reference, *, image=False):
        with self.lock:
            entry = self.references.get(reference)
            if not entry:
                raise ValueError("Discover/select a file before reading it.")
            gid, path, expected = entry
            grant = self._grant(scope, gid)
            allowed = {".png", ".jpg", ".jpeg"} if image else DOCUMENT_TYPES
            if (
                private(path.relative_to(grant.root))
                or path.suffix.lower() not in allowed
            ):
                raise ValueError("This file type or path is unavailable.")
            if expected[2] > MAX_BYTES:
                raise ValueError("Choose a file no larger than 2 MiB.")
            with open_checked(path, grant.root) as stream:
                before = os.fstat(stream.fileno())
                if (
                    not stat.S_ISREG(before.st_mode)
                    or reparse(before)
                    or version(before) != expected
                ):
                    raise ValueError("File changed after discovery. Search again.")
                raw = stream.read(MAX_BYTES + 1)
                if (
                    len(raw) > MAX_BYTES
                    or version(os.fstat(stream.fileno())) != expected
                ):
                    raise ValueError("File changed or exceeded its read limit.")
            self._grant(scope, gid)
            return dict(
                name=path.name,
                source=str(path.relative_to(grant.root)),
                sha256=hashlib.sha256(raw).hexdigest(),
                data=raw,
                extension=path.suffix.lower(),
                grant=gid,
            )

    def check_reference(self, scope, reference):
        with self.lock:
            entry = self.references.get(reference)
            if not entry:
                raise ValueError("File reference revoked.")
            self._grant(scope, entry[0])

    def clear(self):
        with self.lock:
            self.grants.clear()
            self.references.clear()
