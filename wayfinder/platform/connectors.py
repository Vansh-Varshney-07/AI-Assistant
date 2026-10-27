"""Scoped connector entry points reusing the existing exact-action gate."""

import hashlib
import json
from threading import RLock
import time
import uuid

from wayfinder.platform.git_connector import GitConnector, GitPlan, GitStep
from wayfinder.workers.actions import ActionGate

SCHEMAS = {
    "platform_git_grant": {"path"},
    "platform_git_revoke": {"grant"},
    "platform_git_observe": {"grant", "branch"},
    "platform_git_propose": {"grant", "branch", "expected_head", "request_id"},
    "platform_action_decide": {"id", "digest", "approve"},
    "platform_action_revoke": {"id"},
    "platform_action_result": {"id"},
    "platform_action_reconcile": {"id", "grant"},
    "platform_action_audit": {"id"},
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class ConnectorService:
    def __init__(self, app, *, clock=time.time):
        self.app, self.clock, self.lock = app, clock, RLock()
        self.closed = False
        self.git = GitConnector(clock=clock)
        self.actions = ActionGate(
            app.db,
            self.git,
            clock,
            plan_model=GitPlan,
            table="connector_actions",
            unavailable_message="The bounded Git connector is unavailable.",
            bind_envelope=True,
        )
        with app.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS connector_requests(
                    scope TEXT,request TEXT,digest TEXT,action TEXT,PRIMARY KEY(scope,request));
                CREATE TABLE IF NOT EXISTS connector_audit(
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,scope TEXT,action TEXT,
                    event TEXT,at REAL,details TEXT);
            """)
            rows = db.execute(
                "SELECT id,scope,status FROM connector_actions WHERE status IN ('expired','outcome_unknown')"
            ).fetchall()
            for row in rows:
                db.execute(
                    "INSERT INTO connector_audit(scope,action,event,at,details) VALUES (?,?,?,?,?)",
                    (
                        row["scope"],
                        row["id"],
                        "restart_observation",
                        clock(),
                        canonical(dict(status=row["status"], replayed=False)),
                    ),
                )

    def _audit(self, scope, aid, event, details=None):
        with self.app.db() as db:
            db.execute(
                "INSERT INTO connector_audit(scope,action,event,at,details) VALUES (?,?,?,?,?)",
                (json.dumps(scope), aid, event, self.clock(), canonical(details or {})),
            )

    def propose(self, scope, body):
        request = body.get("request_id")
        if not isinstance(request, str) or not request.strip() or len(request) > 100:
            raise ValueError("A bounded request ID is required.")
        inputs = {k: body.get(k) for k in ("grant", "branch", "expected_head")}
        digest = hashlib.sha256(canonical(inputs).encode()).hexdigest()
        with self.app.db() as db:
            old = db.execute(
                "SELECT digest,action FROM connector_requests WHERE scope=? AND request=?",
                (json.dumps(scope), request),
            ).fetchone()
        if old:
            if old["digest"] != digest:
                raise ValueError(
                    "Request ID belongs to different immutable action input."
                )
            return self.actions.get(scope, old["action"])
        observed = self.git.snapshot(scope, body.get("grant"), body.get("branch"))
        if observed["head"] != body.get("expected_head") or observed["target"]:
            raise ValueError(
                "HEAD changed or the destination ref already exists; review fresh input."
            )
        plan = GitPlan(
            repository=observed["repository"],
            grant_ref=body["grant"],
            branch=body["branch"],
            repository_identity=[str(v) for v in observed["identity"]],
            git_identity=[str(v) for v in observed["git_identity"]],
            expected_head=observed["head"],
            nonce=uuid.uuid4().hex,
            state=observed["state"],
            steps=[GitStep()],
        )
        item = self.actions.propose(scope, plan.model_dump())
        with self.app.db() as db:
            db.execute(
                "INSERT INTO connector_requests VALUES (?,?,?,?)",
                (json.dumps(scope), request, digest, item["id"]),
            )
        self._audit(
            scope,
            item["id"],
            "pending",
            dict(digest=item["digest"], operation="git.create_branch"),
        )
        return item

    def call(self, who, scope, operation, body):
        # Authorization at this final handler, even for future in-process callers.
        self.app.authorize(who)
        self.app.space(who, scope.space)
        if (
            who.owner != scope.owner
            or operation not in SCHEMAS
            or set(body) - ({"space", "task"} | SCHEMAS[operation])
        ):
            raise ValueError("Invalid connector operation or scope.")
        bound = scope.worker_scope()
        with self.lock:
            if self.closed or self.app.closed:
                raise ValueError("Connector service is stopped.")
            if operation == "platform_git_grant":
                path = body.get("path")
                if not isinstance(path, str) or not 1 <= len(path) <= 1000:
                    raise ValueError("Select a repository path.")
                return self.git.grant(bound, path)
            if operation == "platform_git_revoke":
                self.git.revoke(bound, body.get("grant"))
                with self.app.db() as db:
                    rows = db.execute(
                        "SELECT id,body FROM connector_actions WHERE scope=? AND status='pending'",
                        (json.dumps(bound),),
                    ).fetchall()
                for row in rows:
                    if json.loads(row["body"])["grant_ref"] == body["grant"]:
                        self.actions.stop(bound, row["id"], status="revoked")
                        self._audit(
                            bound,
                            row["id"],
                            "revoked",
                            dict(reason="Repository grant revoked"),
                        )
                return dict(revoked=True)
            if operation == "platform_git_observe":
                return self.git.snapshot(bound, body.get("grant"), body.get("branch"))
            if operation == "platform_git_propose":
                return self.propose(bound, body)
            item = self.actions.get(bound, body.get("id"))
            if operation == "platform_action_audit":
                with self.app.db() as db:
                    rows = db.execute(
                        "SELECT sequence,event,at,details FROM connector_audit WHERE scope=? AND action=? ORDER BY sequence DESC LIMIT 100",
                        (json.dumps(bound), item["id"]),
                    ).fetchall()
                return [
                    dict(
                        sequence=r["sequence"],
                        event=r["event"],
                        at=r["at"],
                        details=json.loads(r["details"]),
                    )
                    for r in reversed(rows)
                ]
            if operation == "platform_action_revoke":
                item = self.actions.stop(bound, item["id"], status="revoked")
                self._audit(
                    bound,
                    item["id"],
                    "revocation_requested",
                    dict(status=item["status"]),
                )
                return item
            if operation == "platform_action_result":
                return item
            if operation == "platform_action_decide":
                if body.get("digest") != item["digest"]:
                    self._audit(
                        bound,
                        item["id"],
                        "authorization_denied",
                        dict(reason="review_digest_mismatch"),
                    )
                    raise ValueError(
                        "Approval digest differs from the exact reviewed action."
                    )
                self.git.scope = bound
                self.git.approval_expires = item["expires"]
                try:
                    item = self.actions.decide(bound, item["id"], body.get("approve"))
                except (ValueError, TypeError):
                    current = self.actions.get(bound, item["id"])
                    self._audit(
                        bound,
                        item["id"],
                        "decision_failed",
                        dict(
                            status=current["status"],
                            reason="decision_validation_failed",
                        ),
                    )
                    raise
                finally:
                    self.git.scope = None
                    self.git.approval_expires = None
                self._audit(
                    bound,
                    item["id"],
                    item["status"],
                    dict(
                        digest=item["digest"],
                        verified=bool((item.get("result") or {}).get("verified")),
                    ),
                )
                return item
            if operation == "platform_action_reconcile":
                if item["status"] != "outcome_unknown":
                    raise ValueError(
                        "Only uncertain outcomes can be reconciled; reconciliation never dispatches a write."
                    )
                if (
                    self.actions.fingerprint(bound, item["plan"], item["expires"])
                    != item["digest"]
                ):
                    self._audit(
                        bound,
                        item["id"],
                        "reconciliation_denied",
                        dict(reason="review_digest_mismatch"),
                    )
                    raise ValueError(
                        "Reconciliation payload differs from its reviewed digest."
                    )
                plan = GitPlan.model_validate(item["plan"])
                observation = self.git.inspect_outcome(plan, bound, body.get("grant"))
                if observation["verified"]:
                    self.actions._update(
                        item["id"],
                        "completed",
                        dict(verified=True, reconciled=True, receipts=[observation]),
                    )
                self._audit(bound, item["id"], "reconciled", observation)
                return dict(
                    self.actions.get(bound, item["id"]), reconciliation=observation
                )
            raise ValueError("Unknown connector operation.")

    def close(self):
        with self.lock:
            self.closed = True
            self.git.close()
