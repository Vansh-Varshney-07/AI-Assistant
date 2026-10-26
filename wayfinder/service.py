"""Authenticated application boundary over the existing Iron Web engine.

The SQLite file owns UI state, consent and receipts. Facts continue to be owned
by the engine's coordinated graph/vector publication, not a second fact store.
"""

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
from threading import RLock
import time
import uuid

from pydantic import BaseModel, ConfigDict, Field

from memory.lifecycle.models import ClaimInput, canonical_json
from memory.shared.service import RuntimeLock
from memory.workbench import Inspection


class AccessDenied(ValueError):
    pass


class StaleContext(ValueError):
    pass


@dataclass(frozen=True)
class Identity:
    owner: str
    role: str = "orchestrator"


class MemoryProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    text: str = Field(min_length=1, max_length=20000)
    subject: str = Field(default="me", min_length=1, max_length=200)
    predicate: str = Field(min_length=1, max_length=128)
    value: object
    task_id: str = Field(default="general", min_length=1, max_length=100)
    kind: str = "fact"
    action: str = "assert"
    targets: list[str] | None = None
    reason: str = Field(default="", max_length=2000)


def uid():
    return uuid.uuid4().hex


def digest(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def text(value, limit=200):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"Expected nonempty text of at most {limit} characters.")
    return value.strip()


class AppService:
    def __init__(self, runtime, engine, *, acquire_lock=True):
        self.root = Path(runtime).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.owner_lock = (
            RuntimeLock(self.root / "owner.lock") if acquire_lock else None
        )
        self.engine = engine
        self.inspection = Inspection(engine)
        self.closed = False
        self.proofs = {}
        with self.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS spaces(id TEXT PRIMARY KEY,owner TEXT,name TEXT);
                CREATE TABLE IF NOT EXISTS conversations(id TEXT PRIMARY KEY,owner TEXT,space TEXT);
                CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,conversation TEXT,text TEXT,created REAL);
                CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY,owner TEXT,space TEXT,request TEXT,
                    digest TEXT,body TEXT,status TEXT,revision TEXT,result TEXT,UNIQUE(owner,space,request));
                CREATE TABLE IF NOT EXISTS tombstones(memory TEXT PRIMARY KEY,owner TEXT,space TEXT,status TEXT);
                CREATE TABLE IF NOT EXISTS settings(owner TEXT PRIMARY KEY,value TEXT NOT NULL);
            """)
            db.execute("INSERT OR IGNORE INTO meta VALUES ('owner',?)", (uid(),))
            self.owner = db.execute(
                "SELECT value FROM meta WHERE key='owner'"
            ).fetchone()[0]
        self.credentials = {secrets.token_urlsafe(32): Identity(self.owner)}
        self.token = next(iter(self.credentials))
        from wayfinder.workers.hub import WorkerHub

        self.workers = WorkerHub(self.db)
        from wayfinder.platform.service import PlatformService

        self.platform = PlatformService(self)

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.root / "app.sqlite3", timeout=20)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def authenticate(self, token):
        for key, identity in self.credentials.items():
            if isinstance(token, str) and secrets.compare_digest(token, key):
                return identity
        raise AccessDenied("Authentication required.")

    def authorize(self, who):
        if not isinstance(who, Identity) or who.role != "orchestrator":
            raise AccessDenied("Main-memory access is restricted to the orchestrator.")

    def space(self, who, sid):
        self.authorize(who)
        with self.db() as db:
            row = db.execute(
                "SELECT * FROM spaces WHERE id=? AND owner=?", (sid, who.owner)
            ).fetchone()
        if row is None:
            raise AccessDenied("Space unavailable to this identity.")
        return dict(row)

    def revision(self):
        return str(
            int(
                self.engine.graph_store.redis.get(self.engine.graph_store.revision_key)
                or 0
            )
        )

    def scope(self, who, sid, task):
        self.space(who, sid)
        return dict(
            contract="wayfinder_memory_v2",
            owner_id=who.owner,
            memory_space_id=sid,
            task_id=text(task, 100),
        )

    def records(self, who, sid):
        self.space(who, sid)  # Must precede any engine/inspection access.
        with self.db() as db:
            pending = db.execute(
                "SELECT 1 FROM tombstones WHERE space=? AND status='pending'", (sid,)
            ).fetchone()
        if pending:
            raise ValueError(
                "Deletion recovery is pending. Retry its approval before reading this space."
            )
        return self.inspection.inventory(namespace=sid)["records"]

    def owned_record(self, who, sid, mid):
        self.space(who, sid)
        record = self.inspection.detail(text(mid))
        if (
            not record
            or record["memory_space_id"] != sid
            or record["metadata"].get("owner_id") != who.owner
        ):
            raise AccessDenied("Source unavailable to this identity and space.")
        return record

    def proposal(self, who, sid, request, body, *, dry_run=False):
        self.space(who, sid)
        request = text(request)
        if not isinstance(body, dict):
            raise ValueError("Proposal must be an object.")
        if body.get("operation") == "forget":
            if set(body) != {"operation", "memory_id"}:
                raise ValueError("Forget requires only a source identity.")
            self.owned_record(who, sid, body["memory_id"])
        else:
            parsed = MemoryProposal.model_validate(body)
            scope = self.scope(who, sid, parsed.task_id)
            claim = ClaimInput(
                **parsed.model_dump(exclude={"text", "task_id"}), scope=scope
            )
            if (
                claim.action not in {"assert", "correct", "supersede", "retract"}
                or claim.aliases
                or claim.references
            ):
                raise ValueError(
                    "Only scoped assertions and explicit changes are supported."
                )
            if claim.action != "assert" and (
                not claim.targets or not claim.reason.strip()
            ):
                raise ValueError(
                    "A change requires explicit target claim IDs and a reason."
                )
            owned = {
                c["claim_id"]
                for r in self.records(who, sid)
                for c in r["claims"]
                if c["scope"] == scope
                and c["subject"] == claim.subject
                and c["predicate"] == claim.predicate
            }
            if set(claim.targets or []) - owned:
                raise AccessDenied(
                    "Change targets must match this owner, space, task, subject and field."
                )
            body = parsed.model_dump()
        if dry_run:
            return dict(body=body, revision=self.revision(), dry_run=True)
        fingerprint = digest(body)
        with self.db() as db:
            old = db.execute(
                "SELECT * FROM proposals WHERE owner=? AND space=? AND request=?",
                (who.owner, sid, request),
            ).fetchone()
            if old:
                if old["digest"] != fingerprint:
                    raise ValueError(
                        "Request identity belongs to different immutable input."
                    )
                return self.render_proposal(old)
            pid = uid()
            db.execute(
                "INSERT INTO proposals VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    pid,
                    who.owner,
                    sid,
                    request,
                    fingerprint,
                    canonical_json(body),
                    "pending",
                    self.revision(),
                    None,
                ),
            )
            return self.render_proposal(
                db.execute("SELECT * FROM proposals WHERE id=?", (pid,)).fetchone()
            )

    @staticmethod
    def render_proposal(row):
        item = dict(row)
        item["body"] = json.loads(item["body"])
        item["result"] = json.loads(item["result"]) if item["result"] else None
        return item

    def decide(self, who, sid, pid, approve, *, before_effect=None):
        self.space(who, sid)
        if type(approve) is not bool:
            raise ValueError("Approval must be a boolean.")
        with self.db() as db:
            row = db.execute(
                "SELECT * FROM proposals WHERE id=? AND owner=? AND space=?",
                (pid, who.owner, sid),
            ).fetchone()
        if not row:
            raise AccessDenied("Proposal unavailable.")
        proposal = self.render_proposal(row)
        if (
            approve
            and proposal["request"].startswith("platform-memory-")
            and before_effect is None
        ):
            raise ValueError(
                "Platform memory events require the exact platform approval route."
            )
        if proposal["status"] in {"completed", "rejected", "forgotten"}:
            return proposal
        if not approve:
            if proposal["status"] == "applying":
                raise ValueError(
                    "An interrupted operation must be reconciled, not rejected as unapplied."
                )
            with self.db() as db:
                db.execute("UPDATE proposals SET status='rejected' WHERE id=?", (pid,))
            return dict(proposal, status="rejected")
        body = proposal["body"]
        mid = "wf_" + digest([who.owner, sid, proposal["request"]])
        forgetting = body.get("operation") == "forget"
        existing = None if forgetting else self.engine.get(mid)
        if (
            not existing
            and not (forgetting and proposal["status"] == "applying")
            and proposal["revision"] != self.revision()
        ):
            raise StaleContext(
                "Memory changed after preview. Create and inspect a fresh proposal."
            )
        if existing and existing.metadata.get("proposal_digest") != proposal["digest"]:
            raise ValueError("Stored receipt differs from approved input.")
        with self.db() as db:
            db.execute("UPDATE proposals SET status='applying' WHERE id=?", (pid,))
        if forgetting:
            mid = body["memory_id"]
            with self.db() as db:
                db.execute(
                    "INSERT OR IGNORE INTO tombstones VALUES (?,?,?,'pending')",
                    (mid, who.owner, sid),
                )
            self.proofs.clear()  # Deletion intent invalidates context even if storage fails.
            if before_effect is not None:
                before_effect()
            self.engine.delete(mid, user_confirmed=True, clean_orphaned_entities=True)
            if (
                self.engine.get(mid) is not None
                or self.engine.graph_store.execute(
                    "MATCH(c:MemoryClaim {memory_id:$mid}) RETURN c.id", {"mid": mid}
                ).rows
            ):
                raise RuntimeError("Deletion incomplete; no completion receipt issued.")
            result = dict(
                memory_id=mid,
                deleted=True,
                receipt_id=pid,
                backup_notice="Older backups and separately retained transcripts require separate retention control.",
            )
            with self.db() as db:
                db.execute(
                    "UPDATE tombstones SET status='completed' WHERE memory=?", (mid,)
                )
                # Retain identity/digest, remove the application's extra evidence copies.
                db.execute(
                    "UPDATE proposals SET body='{}',result=NULL,status='forgotten' WHERE owner=? AND space=? AND json_extract(result,'$.memory_id')=?",
                    (who.owner, sid, mid),
                )
        else:
            parsed = MemoryProposal.model_validate(body)
            claim = ClaimInput(
                **parsed.model_dump(exclude={"text", "task_id"}),
                scope=self.scope(who, sid, parsed.task_id),
            )
            if before_effect is not None:
                before_effect()
            self.engine.add(
                parsed.text,
                memory_id=mid,
                claims=[claim.model_dump()],
                source_info=dict(
                    origin="user",
                    actor_id=who.owner,
                    user_confirmed=True,
                    event_id=pid,
                    quality=0.9,
                ),
                metadata=dict(
                    source="wayfinder_v2",
                    owner_id=who.owner,
                    memory_space_id=sid,
                    test_namespace=sid,
                    proposal_digest=proposal["digest"],
                ),
            )
            record = self.owned_record(who, sid, mid)
            if not (record["vector_stored"] and record["graph_stored"]):
                raise RuntimeError("Storage unconfirmed; no completion receipt issued.")
            result = dict(
                memory_id=mid,
                receipt_id=pid,
                stored=True,
                claim_ids=[c["claim_id"] for c in record["claims"]],
            )
        with self.db() as db:
            db.execute(
                "UPDATE proposals SET status='completed',result=? WHERE id=?",
                (canonical_json(result), pid),
            )
        self.proofs.clear()
        return dict(proposal, status="completed", result=result)

    def call(self, who, operation, body):
        self.authorize(who)
        if not isinstance(body, dict):
            raise ValueError("Request body must be an object.")
        if operation.startswith("worker_"):
            return self.worker_call(who, operation, body)
        if operation.startswith("platform_"):
            return self.platform.call(who, operation, body)
        schemas = {
            "status": set(),
            "spaces": set(),
            "create_space": {"name"},
            "conversation": {"space", "conversation"},
            "transcript": {"space", "conversation", "id", "text"},
            "settings": {"value"},
            "inventory": {"space"},
            "source": {"space", "memory_id"},
            "propose": {"space", "request", "body"},
            "decide": {"space", "proposal", "approve"},
            "proposals": {"space"},
            "recall": {"space", "subject", "predicate", "task_id", "temporal_mode"},
            "validate_context": {"space", "proof"},
            "clear_transcript": {"space", "conversation"},
        }
        if operation not in schemas or set(body) - schemas[operation]:
            raise ValueError("Unknown operation or fields.")
        with self.lock:
            if self.closed:
                raise ValueError("Memory service is stopped.")
            sid = body.get("space")
            if "space" in schemas[operation]:
                self.space(who, sid)
            if operation == "status":
                self.engine.graph_store.execute("RETURN 1")
                return dict(
                    version="0.2.0",
                    memory="online",
                    contract="wayfinder_memory_v2",
                    graph=self.engine.graph_name,
                    revision=self.revision(),
                    models="Hermes desktop analysis on request; general chat is local transcript only",
                    plugins="Scoped desktop workers available; other plugins not connected",
                )
            if operation == "spaces":
                with self.db() as db:
                    return [
                        dict(r)
                        for r in db.execute(
                            "SELECT * FROM spaces WHERE owner=? ORDER BY rowid",
                            (who.owner,),
                        )
                    ]
            if operation == "create_space":
                name, sid = text(body.get("name"), 100), "space_" + uid()
                with self.db() as db:
                    db.execute(
                        "INSERT INTO spaces VALUES (?,?,?)", (sid, who.owner, name)
                    )
                return self.space(who, sid)
            if operation in {"conversation", "transcript", "clear_transcript"}:
                cid = body.get("conversation")
                with self.db() as db:
                    if operation == "conversation" and not cid:
                        cid = uid()
                        db.execute(
                            "INSERT INTO conversations VALUES (?,?,?)",
                            (cid, who.owner, sid),
                        )
                    row = db.execute(
                        "SELECT * FROM conversations WHERE id=? AND owner=? AND space=?",
                        (cid, who.owner, sid),
                    ).fetchone()
                    if not row:
                        raise AccessDenied("Conversation unavailable in this space.")
                    if operation == "transcript":
                        message, msgid = (
                            text(body.get("text"), 20000),
                            text(body.get("id")),
                        )
                        old = db.execute(
                            "SELECT * FROM messages WHERE id=?", (msgid,)
                        ).fetchone()
                        if old and (
                            old["conversation"] != cid or old["text"] != message
                        ):
                            raise ValueError(
                                "Message identity already has different input."
                            )
                        db.execute(
                            "INSERT OR IGNORE INTO messages VALUES (?,?,?,?)",
                            (msgid, cid, message, time.time()),
                        )
                    if operation == "clear_transcript":
                        db.execute("DELETE FROM messages WHERE conversation=?", (cid,))
                    return dict(
                        conversation=cid,
                        space=sid,
                        messages=[
                            dict(r)
                            for r in db.execute(
                                "SELECT * FROM messages WHERE conversation=? ORDER BY created,id",
                                (cid,),
                            )
                        ],
                    )
            if operation == "settings":
                with self.db() as db:
                    if "value" in body:
                        value = body["value"]
                        if (
                            not isinstance(value, dict)
                            or set(value) != {"font_size", "background"}
                            or type(value["font_size"]) is not int
                            or not 10 <= value["font_size"] <= 24
                            or type(value["background"]) is not bool
                        ):
                            raise ValueError(
                                "Settings require font_size 10–24 and boolean background."
                            )
                        db.execute(
                            "INSERT INTO settings VALUES (?,?) ON CONFLICT(owner) DO UPDATE SET value=excluded.value",
                            (who.owner, canonical_json(value)),
                        )
                    row = db.execute(
                        "SELECT value FROM settings WHERE owner=?", (who.owner,)
                    ).fetchone()
                    return (
                        json.loads(row[0])
                        if row
                        else dict(font_size=12, background=False)
                    )
            if operation == "inventory":
                return dict(records=self.records(who, sid), revision=self.revision())
            if operation == "source":
                self.records(who, sid)
                return self.owned_record(who, sid, body.get("memory_id"))
            if operation == "propose":
                return self.proposal(who, sid, body.get("request"), body.get("body"))
            if operation == "decide":
                return self.decide(who, sid, body.get("proposal"), body.get("approve"))
            if operation == "proposals":
                with self.db() as db:
                    return [
                        self.render_proposal(r)
                        for r in db.execute(
                            "SELECT * FROM proposals WHERE owner=? AND space=? ORDER BY rowid DESC",
                            (who.owner, sid),
                        )
                    ]
            if operation == "recall":
                self.records(who, sid)
                mode = body.get("temporal_mode", "now")
                if mode not in {"now", "historical"}:
                    raise ValueError("Choose now or historical recall.")
                subject, predicate = (
                    text(body.get("subject", "me")),
                    text(body.get("predicate"), 128),
                )
                scope = self.scope(who, sid, body.get("task_id", "general"))
                before = self.revision()
                packet = self.engine.recall(
                    predicate,
                    subject=subject,
                    predicate=predicate,
                    scope=scope,
                    temporal_mode=mode,
                )
                if before != self.revision():
                    raise StaleContext(
                        "Memory changed during recall. Retry with fresh evidence."
                    )
                proof = secrets.token_urlsafe(24)
                self.proofs[proof] = (who.owner, sid, before, time.monotonic() + 300)
                if len(self.proofs) > 256:
                    self.proofs.pop(next(iter(self.proofs)))
                return dict(
                    packet=packet,
                    proof=proof,
                    revision=before,
                    contract="wayfinder_memory_v2",
                )
            if operation == "validate_context":
                proof = self.proofs.get(body.get("proof"))
                if (
                    not proof
                    or proof[:2] != (who.owner, sid)
                    or proof[2] != self.revision()
                    or proof[3] < time.monotonic()
                ):
                    raise StaleContext(
                        "Context expired or memory changed. Retrieve again."
                    )
                return dict(valid=True, revision=proof[2])

    def close(self):
        # Platform jobs acquire their own lock before entering existing memory
        # APIs. Close that boundary before holding the application memory lock.
        self.platform.close()
        with self.lock:
            if not self.closed:
                self.closed = True
                self.workers.close()
                self.proofs.clear()
                try:
                    self.engine.close()
                finally:
                    if self.owner_lock:
                        self.owner_lock.close()

    def worker_call(self, who, operation, body):
        schemas = {
            "worker_status": {"space", "task"},
            "worker_grant": {"space", "task", "path"},
            "worker_search": {"space", "task", "grant", "pattern"},
            "worker_revoke": {"space", "task", "grant"},
            "worker_image": {"space", "task", "path", "sha256"},
            "worker_clear_images": {"space", "task"},
            "worker_start": {
                "space",
                "task",
                "role",
                "question",
                "reference",
                "image",
                "context",
            },
            "worker_jobs": {"space", "task"},
            "worker_result": {"space", "task", "id"},
            "worker_cancel": {"space", "task", "id"},
            "worker_forget": {"space", "task", "id"},
            "worker_action_propose": {"space", "task", "plan"},
            "worker_action_decide": {"space", "task", "id", "approve"},
            "worker_action_stop": {"space", "task", "id"},
            "worker_action_result": {"space", "task", "id"},
        }
        if operation not in schemas or set(body) - schemas[operation]:
            raise ValueError("Unknown worker operation or fields.")
        with self.lock:
            if self.closed:
                raise ValueError("Service is stopped.")
            self.space(who, body.get("space"))
            scope = (who.owner, body["space"], text(body.get("task"), 100))
        # Model calls are background jobs; revocation and the main UI remain responsive.
        hub = self.workers
        if operation == "worker_status":
            return hub.status()
        if operation == "worker_grant":
            return hub.files.grant(scope, text(body.get("path"), 1000))
        if operation == "worker_search":
            return hub.files.discover(
                scope, text(body.get("grant")), body.get("pattern", "*")
            )
        if operation == "worker_revoke":
            return hub.revoke_files(scope, text(body.get("grant")))
        if operation == "worker_image":
            return hub.share_image(
                scope, text(body.get("path"), 1000), text(body.get("sha256"), 64)
            )
        if operation == "worker_clear_images":
            return hub.clear_images(scope)
        if operation == "worker_start":
            return hub.start(
                scope,
                role=body.get("role"),
                question=body.get("question"),
                reference=body.get("reference"),
                image=body.get("image"),
                context=body.get("context", ""),
            )
        if operation == "worker_jobs":
            return hub.list(scope)
        if operation == "worker_result":
            return hub.get(scope, text(body.get("id")))
        if operation == "worker_cancel":
            return hub.cancel(scope, text(body.get("id")))
        if operation == "worker_forget":
            return hub.forget(scope, text(body.get("id")))
        if operation == "worker_action_propose":
            return hub.actions.propose(scope, body.get("plan"))
        if operation == "worker_action_decide":
            return hub.actions.decide(scope, text(body.get("id")), body.get("approve"))
        if operation == "worker_action_stop":
            return hub.actions.stop(scope, text(body.get("id")))
        if operation == "worker_action_result":
            return hub.actions.get(scope, text(body.get("id")))
