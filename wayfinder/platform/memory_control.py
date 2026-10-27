"""Scope and exact approvals around existing Iron Web change events; no new memory engine."""

import hashlib
import json
from threading import RLock
import time
from typing import Literal
import uuid

from pydantic import Field

from wayfinder.platform.contracts import Contract, VERSION
from wayfinder.service import MemoryProposal, digest
from wayfinder.workers.actions import ActionGate


SCHEMAS = {
    "platform_memory_preview": {"body"},
    "platform_memory_propose": {"body", "request_id"},
    "platform_memory_decide": {"id", "digest", "approve"},
    "platform_memory_revoke": {"id"},
    "platform_memory_result": {"id"},
    "platform_memory_reconcile": {"id"},
    "platform_memory_audit": {"id"},
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class MemoryStep(Contract):
    action: Literal["memory.apply_event"] = "memory.apply_event"


class MemoryPlan(Contract):
    contract: Literal["wayfinder.platform/1"] = VERSION
    proposal_ref: str = Field(min_length=1, max_length=100)
    body: MemoryProposal
    state: str = Field(pattern=r"^[a-f0-9]{64}$")
    steps: list[MemoryStep] = Field(min_length=1, max_length=1)


class MemoryDriver:
    available = True

    def __init__(self, app, clock):
        self.app, self.clock = app, clock
        self.who = self.scope = self.expires = None
        self.authorization_current = None

    def proposal(self, plan, scope):
        with self.app.db() as db:
            row = db.execute(
                "SELECT * FROM proposals WHERE id=? AND owner=? AND space=?",
                (plan.proposal_ref, scope.owner, scope.space),
            ).fetchone()
        if not row:
            raise ValueError("Memory proposal unavailable in this scope.")
        item = self.app.render_proposal(row)
        body = plan.body.model_dump()
        if (
            body["task_id"] != scope.task
            or item["body"] != body
            or item["digest"] != digest(body)
        ):
            raise ValueError(
                "Memory proposal differs from the reviewed task and payload."
            )
        return item

    def state(self, plan, scope):
        item = self.proposal(plan, scope)
        if item["status"] != "pending" or item["revision"] != self.app.revision():
            raise ValueError("Memory changed after review; inspect a fresh proposal.")
        # Reuse existing validation, including exact target claim ownership and field.
        self.app.proposal(
            self.who, scope.space, "preview", plan.body.model_dump(), dry_run=True
        )
        return hashlib.sha256(
            canonical(
                dict(
                    scope=scope.model_dump(),
                    revision=item["revision"],
                    body=item["body"],
                )
            ).encode()
        ).hexdigest()

    def observe(self, plan):
        with self.app.lock:
            return self.state(plan, self.scope)

    def perform(self, plan, step, expected):
        with self.app.lock:
            if self.state(plan, self.scope) != expected:
                raise ValueError("Memory preconditions changed.")
            self.check_dispatch()
            self.app.decide(
                self.who,
                self.scope.space,
                plan.proposal_ref,
                True,
                before_effect=self.check_dispatch,
            )
            observed = self.inspect_outcome(plan, self.scope)
            return dict(state=expected, **observed)

    def check_dispatch(self):
        if self.expires is None or self.clock() >= self.expires or not self.authorization_current or not self.authorization_current():
            raise ValueError(
                "Memory approval expired at the storage dispatch boundary."
            )

    def inspect_outcome(self, plan, scope):
        item = self.proposal(plan, scope)
        mid = "wf_" + digest([scope.owner, scope.space, item["request"]])
        record = (
            self.app.owned_record(self.who, scope.space, mid)
            if self.app.engine.get(mid)
            else None
        )
        expected_value = (
            dict(
                retracted_field=plan.body.predicate.strip(),
                targets=plan.body.targets,
                reason=plan.body.reason,
            )
            if plan.body.action == "retract"
            else plan.body.value
        )
        verified = bool(
            record
            and record["vector_stored"]
            and record["graph_stored"]
            and record["metadata"].get("proposal_digest") == item["digest"]
            and any(
                c["scope"] == self.app.scope(self.who, scope.space, scope.task)
                and c["subject"] == plan.body.subject.strip()
                and c["predicate"]
                == (
                    ("__retracted__." if plan.body.action == "retract" else "")
                    + plan.body.predicate.strip()
                )
                and (
                    c["value"] == expected_value
                    if plan.body.action != "retract"
                    else c["value"].get("retracted_field")
                    == expected_value["retracted_field"]
                    and set(c["value"].get("targets", []))
                    == set(expected_value["targets"])
                    and c["value"].get("reason") == expected_value["reason"]
                )
                for c in record["claims"]
            )
        )
        return dict(
            verified=verified,
            memory_id=mid if verified else None,
            receipt_id=plan.proposal_ref,
        )

    def verify(self, plan, receipts):
        return bool(receipts) and self.inspect_outcome(plan, self.scope)["verified"]


class MemoryControl:
    def __init__(self, app, *, clock=time.time):
        self.app, self.clock, self.lock = app, clock, RLock()
        self.closed = False
        self.driver = MemoryDriver(app, clock)
        self.actions = ActionGate(
            app.db,
            self.driver,
            clock,
            plan_model=MemoryPlan,
            table="memory_actions",
            bind_envelope=True,
        )
        with app.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS platform_memory_requests(
                    scope TEXT,request TEXT,digest TEXT,action TEXT,PRIMARY KEY(scope,request));
                CREATE TABLE IF NOT EXISTS platform_memory_audit(
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,scope TEXT,action TEXT,
                    event TEXT,at REAL,details TEXT);
            """)
            rows = db.execute(
                "SELECT id,scope,status FROM memory_actions WHERE status IN ('expired','outcome_unknown')"
            ).fetchall()
            for row in rows:
                owner, space, task = json.loads(row["scope"])
                db.execute(
                    "INSERT INTO platform_memory_audit(scope,action,event,at,details) VALUES (?,?,?,?,?)",
                    (
                        canonical(dict(owner=owner, space=space, task=task)),
                        row["id"],
                        "restart_observation",
                        clock(),
                        canonical(dict(status=row["status"], replayed=False)),
                    ),
                )

    def audit(self, scope, aid, event, details=None):
        with self.app.db() as db:
            db.execute(
                "INSERT INTO platform_memory_audit(scope,action,event,at,details) VALUES (?,?,?,?,?)",
                (
                    canonical(scope.model_dump()),
                    aid,
                    event,
                    self.clock(),
                    canonical(details or {}),
                ),
            )

    def call(self, who, scope, operation, body):
        self.app.authorize(who)
        self.app.space(who, scope.space)
        if (
            who.owner != scope.owner
            or operation not in SCHEMAS
            or set(body) - (SCHEMAS[operation] | {"space", "task"})
        ):
            raise ValueError("Invalid memory operation or scope.")
        with self.lock, self.app.lock:
            if self.closed or self.app.closed:
                raise ValueError("Memory integration is stopped.")
            self.driver.who, self.driver.scope = who, scope
            try:
                return self._call(who, scope, operation, body)
            finally:
                self.driver.who = self.driver.scope = self.driver.expires = None

    def _call(self, who, scope, operation, body):
        bound = scope.worker_scope()
        if operation in {"platform_memory_preview", "platform_memory_propose"}:
            parsed = MemoryProposal.model_validate(body.get("body"))
            if parsed.task_id != scope.task or len(parsed.targets or []) > 8:
                raise ValueError(
                    "Memory task must match; at most eight explicit targets."
                )
            inputs = parsed.model_dump()
            preview = self.app.proposal(
                who, scope.space, "preview", inputs, dry_run=True
            )
            if operation == "platform_memory_preview":
                return dict(
                    contract=VERSION,
                    **preview,
                    executed=False,
                    expires=self.clock() + 120,
                )
            request = body.get("request_id")
            if (
                not isinstance(request, str)
                or not request.strip()
                or len(request) > 100
            ):
                raise ValueError("A bounded request ID is required.")
            key, fingerprint = canonical(scope.model_dump()), digest(inputs)
            with self.app.db() as db:
                old = db.execute(
                    "SELECT digest,action FROM platform_memory_requests WHERE scope=? AND request=?",
                    (key, request),
                ).fetchone()
            if old:
                if old["digest"] != fingerprint:
                    raise ValueError(
                        "Request ID belongs to different immutable memory input."
                    )
                return self.actions.get(bound, old["action"])
            existing = self.app.proposal(
                who, scope.space, "platform-memory-" + uuid.uuid4().hex, inputs
            )
            plan = MemoryPlan(
                proposal_ref=existing["id"],
                body=parsed,
                state="0" * 64,
                steps=[MemoryStep()],
            )
            plan = plan.model_copy(update={"state": self.driver.state(plan, scope)})
            item = self.actions.propose(bound, plan.model_dump())
            with self.app.db() as db:
                db.execute(
                    "INSERT INTO platform_memory_requests VALUES (?,?,?,?)",
                    (key, request, fingerprint, item["id"]),
                )
            self.audit(
                scope,
                item["id"],
                "pending",
                dict(digest=item["digest"], action=parsed.action),
            )
            return item
        item = self.actions.get(bound, body.get("id"))
        if operation == "platform_memory_audit":
            with self.app.db() as db:
                rows = db.execute(
                    "SELECT sequence,event,at,details FROM platform_memory_audit WHERE scope=? AND action=? ORDER BY sequence DESC LIMIT 100",
                    (canonical(scope.model_dump()), item["id"]),
                ).fetchall()
            return [dict(r, details=json.loads(r["details"])) for r in reversed(rows)]
        if operation == "platform_memory_result":
            return item
        if operation == "platform_memory_revoke":
            item = self.actions.stop(bound, item["id"], status="revoked")
            self.audit(
                scope, item["id"], "revocation_requested", dict(status=item["status"])
            )
            return item
        intact = (
            self.actions.fingerprint(bound, item["plan"], item["expires"])
            == item["digest"]
        )
        if not intact or (
            operation == "platform_memory_decide"
            and body.get("digest") != item["digest"]
        ):
            self.audit(scope, item["id"], "authorization_denied")
            raise ValueError("Memory approval differs from the reviewed envelope.")
        if operation == "platform_memory_reconcile":
            if item["status"] != "outcome_unknown":
                raise ValueError(
                    "Only uncertain memory outcomes require reconciliation."
                )
            observation = self.driver.inspect_outcome(
                MemoryPlan.model_validate(item["plan"]), scope
            )
            if observation["verified"]:
                self.actions._update(
                    item["id"],
                    "completed",
                    dict(verified=True, reconciled=True, receipts=[observation]),
                )
            self.audit(scope, item["id"], "reconciled", observation)
            return dict(self.actions.get(bound, item["id"]), reconciliation=observation)
        if operation == "platform_memory_decide":
            self.driver.expires = item["expires"]
            try:
                item = self.actions.decide(bound, item["id"], body.get("approve"))
            except (ValueError, TypeError):
                self.audit(scope, item["id"], "decision_failed")
                raise
            self.audit(
                scope,
                item["id"],
                item["status"],
                dict(verified=bool((item.get("result") or {}).get("verified"))),
            )
            return item
        raise ValueError("Unknown memory operation.")

    def close(self):
        with self.lock:
            self.closed = True
