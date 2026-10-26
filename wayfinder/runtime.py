"""One-owner runtime factory and checksummed cold snapshots."""

import hashlib
import json
from pathlib import Path
import re
import shutil

from memory.engine import MemoryEngine
from memory.lifecycle.models import canonical_json
from memory.shared.service import RuntimeLock
from memory.storage import coordinated_write
from wayfinder.service import AppService


def engine_for(root):
    root = Path(root).resolve()
    graph = "wayfinder_" + hashlib.sha256(str(root).encode()).hexdigest()[:24]
    return MemoryEngine(
        qdrant_path=str(root / "vectors"),
        graph_name=graph,
        config={"extraction_policy": "none", "retrieval": {"reranker_enabled": False}},
    )


def open_service(root, factory=engine_for):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    try:
        lock = RuntimeLock(root / "owner.lock")
    except OSError as error:
        raise RuntimeError("Runtime is already owned or unavailable.") from error
    engine = None
    try:
        engine = factory(root)
        service = AppService(root, engine, acquire_lock=False)
        service.owner_lock = lock
        return service
    except Exception:
        try:
            if engine is not None:
                engine.close()
        finally:
            lock.close()
        raise


def backup(root, destination, factory=engine_for):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if not root.exists() or destination.exists() or destination.is_relative_to(root):
        raise ValueError(
            "Use an existing stopped runtime and a fresh destination outside it."
        )
    service = open_service(root, factory)
    try:
        with service.lock, service.engine.graph_store.write_lock, service.engine._operation_lock:
            store = service.engine.graph_store
            records = dict(
                nodes=store.execute("MATCH(n) RETURN labels(n),properties(n)").rows,
                edges=store.execute(
                    "MATCH(a)-[r]->(b) RETURN labels(a),a.id,type(r),labels(b),b.id,properties(r)"
                ).rows,
            )
            raw = canonical_json(records).encode()
            service.engine.close()  # Qdrant must be closed while its files are copied.
            destination.mkdir(parents=True)
            shutil.copytree(
                root,
                destination / "runtime",
                ignore=shutil.ignore_patterns("owner.lock", "*.log"),
            )
            (destination / "graph.json").write_bytes(raw)
            files = {
                str(p.relative_to(destination)): hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
                for p in destination.rglob("*")
                if p.is_file()
            }
            (destination / "snapshot.json").write_text(
                json.dumps(dict(format="wayfinder_snapshot_v1", files=files), indent=2),
                encoding="utf-8",
            )
            return dict(snapshot=str(destination), files=len(files), private=True)
    finally:
        service.close()


def restore(snapshot, target, current_runtime, factory=engine_for):
    source, target, current = map(
        lambda p: Path(p).resolve(), (snapshot, target, current_runtime)
    )
    if (
        target.exists()
        or target.is_relative_to(source)
        or target.is_relative_to(current)
    ):
        raise ValueError(
            "Restore requires a fresh directory outside the snapshot and current runtime."
        )
    manifest = json.loads((source / "snapshot.json").read_text(encoding="utf-8"))
    if manifest.get("format") != "wayfinder_snapshot_v1":
        raise ValueError("Unsupported snapshot.")
    for name, expected in manifest["files"].items():
        path = (source / name).resolve()
        if (
            not path.is_relative_to(source)
            or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise ValueError("Snapshot checksum or path validation failed.")
    if not (current / "app.sqlite3").exists():
        raise ValueError("Current runtime is required for deletion reconciliation.")
    # Serialize with the current owner: no deletion can race the restore merge.
    current_service = open_service(current, factory)
    restored = None
    try:
        with current_service.db() as db:
            tombstones = [dict(r) for r in db.execute("SELECT * FROM tombstones")]
        records = json.loads((source / "graph.json").read_text(encoding="utf-8"))
        for labels in (
            [n[0] for n in records["nodes"]]
            + [e[0] for e in records["edges"]]
            + [e[3] for e in records["edges"]]
        ):
            if not labels or any(
                not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", label) for label in labels
            ):
                raise ValueError("Invalid graph labels.")
        if any(
            not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", e[2]) for e in records["edges"]
        ):
            raise ValueError("Invalid graph relations.")
        shutil.copytree(source / "runtime", target)
        restored = open_service(target, factory)
        if restored.engine.graph_store.execute("MATCH(n) RETURN count(n)").rows[0][0]:
            raise ValueError(
                "Target graph already contains data; it will not be overwritten."
            )
        restored.engine.lifecycle.ensure_schema()
        with coordinated_write(
            restored.engine.vector_store, restored.engine.graph_store, []
        ):
            graph = restored.engine.graph_store
            for labels, props in records["nodes"]:
                graph.execute(
                    "MERGE(n:" + ":".join(labels) + " {id:$props.id}) SET n += $props",
                    {"props": props},
                )
            for sl, sid, rel, tl, tid, props in records["edges"]:
                graph.execute(
                    "MATCH(a:"
                    + ":".join(sl)
                    + " {id:$sid}),(b:"
                    + ":".join(tl)
                    + " {id:$tid}) CREATE(a)-[r:"
                    + rel
                    + "]->(b) SET r += $props",
                    {"sid": sid, "tid": tid, "props": props},
                )
        # Deletions after the snapshot must not reappear as active evidence.
        for item in tombstones:
            mid = item["memory"]
            restored.engine.delete(
                mid, user_confirmed=True, clean_orphaned_entities=True
            )
            with restored.db() as db:
                db.execute(
                    "INSERT OR REPLACE INTO tombstones VALUES (?,?,?,'completed')",
                    (mid, item["owner"], item["space"]),
                )
                db.execute(
                    "UPDATE proposals SET body='{}',result=NULL,status='forgotten' WHERE json_extract(result,'$.memory_id')=?",
                    (mid,),
                )
        return dict(
            runtime=str(target),
            stable_ids=True,
            reconciled_deletions=len(tombstones),
            live_overwritten=False,
        )
    finally:
        if restored:
            restored.close()
        current_service.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Cold Wayfinder backup / fresh restore. Quit the app first."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    save = sub.add_parser("backup")
    save.add_argument("--runtime", required=True)
    save.add_argument("--destination", required=True)
    load = sub.add_parser("restore")
    load.add_argument("--snapshot", required=True)
    load.add_argument("--target", required=True)
    load.add_argument("--current-runtime", required=True)
    args = parser.parse_args()
    result = (
        backup(args.runtime, args.destination)
        if args.command == "backup"
        else restore(args.snapshot, args.target, args.current_runtime)
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
