"""Exact-plan approval boundary. Driver availability never implies authorization."""

import hashlib
import json
from threading import Event, RLock
import time
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    action: Literal["type_text", "press_key", "click"]
    delivery_mode: Literal["background", "foreground"] | None = None
    text: str | None = Field(default=None, max_length=2000)
    key: Literal["ENTER", "TAB", "ESC", "CTRL+S", "CTRL+A"] | None = None
    x: int | None = Field(default=None, ge=0, le=16384)
    y: int | None = Field(default=None, ge=0, le=16384)

    @model_validator(mode="after")
    def exact_parameters(self):
        supplied = {k for k, v in self.model_dump().items() if v is not None} - {
            "action",
            "delivery_mode",
        }
        needed = {"type_text": {"text"}, "press_key": {"key"}, "click": {"x", "y"}}
        if supplied != needed[self.action]:
            raise ValueError("Action parameters do not match the selected action.")
        return self


class DesktopPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    summary: str = Field(min_length=1, max_length=1000)
    app: str = Field(min_length=1, max_length=200)
    window: int = Field(gt=0)
    process: int = Field(gt=0)
    state: str = Field(min_length=1, max_length=200)
    steps: list[Step] = Field(min_length=1, max_length=12)
    completion: str = Field(min_length=1, max_length=1000)
    observation: Literal["selected_window"]


class ActionGate:
    """Optional driver is a trusted integration, never supplied through the model/API."""

    def __init__(
        self,
        db,
        driver=None,
        clock=time.time,
        *,
        plan_model=DesktopPlan,
        table="desktop_actions",
        unavailable_message=None,
        bind_envelope=False,
        monotonic=time.monotonic,
    ):
        if table not in {"desktop_actions", "connector_actions", "memory_actions"}:
            raise ValueError("Unknown trusted action store.")
        self.table, self.plan_model = table, plan_model
        self.bind_envelope = bind_envelope
        self.unavailable_message = (
            unavailable_message
            or "Windows desktop execution is locked: a verified Hermes Windows driver is not connected."
        )
        self.db, self.driver, self.clock = db, driver, clock
        self.monotonic, self.deadlines = monotonic, {}
        self.lock, self.stops = RLock(), {}
        with db() as connection:
            connection.execute(f"""CREATE TABLE IF NOT EXISTS {self.table}(
                id TEXT PRIMARY KEY, scope TEXT, body TEXT, digest TEXT, expires REAL,
                status TEXT, result TEXT)""")
            connection.execute(
                f"UPDATE {self.table} SET status='outcome_unknown' WHERE status='executing'"
            )
            # Pending approvals are process-local grants; restarts require a new review.
            connection.execute(
                f"UPDATE {self.table} SET status='expired' WHERE status='pending'"
            )

    @property
    def available(self):
        return self.driver is not None and self.driver.available

    def propose(self, scope, body):
        plan = self.plan_model.model_validate(body)
        raw = json.dumps(plan.model_dump(), sort_keys=True, separators=(",", ":"))
        expires = self.clock() + 120
        fingerprint = self.fingerprint(scope, plan.model_dump(), expires)
        aid = uuid.uuid4().hex
        with self.lock, self.db() as connection:
            connection.execute('BEGIN IMMEDIATE')
            self._family_clear(connection, scope, plan.model_dump())
            connection.execute(f"INSERT INTO {self.table} VALUES (?,?,?,?,?,'pending',NULL)", (aid, json.dumps(scope), raw, fingerprint, expires))
            self.deadlines[aid] = self.monotonic() + 120
        return self.get(scope, aid)

    def expired(self, item):
        # A backwards wall-clock adjustment cannot prolong a one-shot grant.
        return item['expires'] <= self.clock() or self.monotonic() >= self.deadlines.get(item['id'], float('-inf'))

    def _family_clear(self, connection, scope, plan, exclude=None):
        rows = connection.execute(f"SELECT id,scope,body FROM {self.table} WHERE status IN ('executing','outcome_unknown')").fetchall()
        for row in rows:
            if row[0] == exclude:
                continue
            old_scope, old_plan = json.loads(row[1]), json.loads(row[2])
            same_family = old_scope[:2] == list(scope)[:2]
            if self.table == 'connector_actions':
                same_family = same_family or (old_plan.get('repository_identity') == plan.get('repository_identity') and old_plan.get('git_identity') == plan.get('git_identity'))
            if same_family:
                raise ValueError('This operation family has an unresolved outcome. Reconcile the original receipt before another effect.')

    def fingerprint(self, scope, plan, expires):
        body = (
            dict(scope=list(scope), plan=plan, expires=expires)
            if self.bind_envelope
            else plan
        )
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, scope, aid):
        with self.db() as connection:
            row = connection.execute(
                f"SELECT * FROM {self.table} WHERE id=? AND scope=?",
                (aid, json.dumps(scope)),
            ).fetchone()
        if not row:
            raise ValueError("Action unavailable in this task.")
        return dict(
            id=row[0],
            plan=json.loads(row[2]),
            digest=row[3],
            expires=row[4],
            status=row[5],
            result=json.loads(row[6]) if row[6] else None,
        )

    def stop(self, scope, aid, *, status="rejected"):
        if status not in {"rejected", "revoked"}:
            raise ValueError("Invalid revocation state.")
        # Revoke immediately even if a dispatched driver call is still returning.
        self.get(scope, aid)
        self.stops.setdefault(aid, Event()).set()
        with self.lock:
            item = self.get(scope, aid)
            if item["status"] == "pending":
                self._update(aid, status)
        return self.get(scope, aid)

    def _update(self, aid, status, result=None):
        with self.db() as connection:
            connection.execute(
                f"UPDATE {self.table} SET status=?,result=? WHERE id=?",
                (status, json.dumps(result) if result else None, aid),
            )
        if status not in {'pending', 'executing'}:
            self.deadlines.pop(aid, None)

    def decide(self, scope, aid, approve):
        if type(approve) is not bool:
            raise ValueError("Approval must be true or false.")
        if not approve:
            return self.stop(scope, aid)
        with self.lock:
            item = self.get(scope, aid)
            if item["status"] != "pending":
                return item
            if self.expired(item):
                self._update(aid, "expired")
                return self.get(scope, aid)
            if self.fingerprint(scope, item["plan"], item["expires"]) != item["digest"]:
                self._update(aid, "failed")
                raise ValueError("Action payload differs from its reviewed digest.")
            if not self.available:
                raise ValueError(self.unavailable_message)
            stopped = self.stops.setdefault(aid, Event())
            if stopped.is_set():
                raise ValueError("Action revoked.")
            with self.db() as connection:
                self._family_clear(connection, scope, item['plan'], exclude=aid)
            if hasattr(self.driver, 'authorization_current'):
                self.driver.authorization_current = lambda: not self.expired(item) and not stopped.is_set()
            self._update(aid, "executing")
        # No goal-level agent discretion. Validate each exact effect at its dispatch boundary.
        dispatched = False
        receipts = []
        try:
            plan = self.plan_model.model_validate(item["plan"])
            expected = plan.state
            for step in plan.steps:
                with self.lock:
                    if stopped.is_set() or self.expired(item):
                        self._update(aid, "stopped", dict(receipts=receipts))
                        return self.get(scope, aid)
                    if self.driver.observe(plan) != expected:
                        raise ValueError("Target changed since review.")
                    if stopped.is_set() or self.expired(item):
                        self._update(
                            aid,
                            "stopped" if stopped.is_set() or receipts else "expired",
                            dict(receipts=receipts),
                        )
                        return self.get(scope, aid)
                    dispatched = True
                    # Driver must compare-and-dispatch against this expected target state.
                    receipt = self.driver.perform(plan, step, expected)
                    expected = receipt["state"]
                    receipts.append(receipt)
            if not self.driver.verify(plan, receipts):
                raise RuntimeError("Completion could not be independently verified.")
            self._update(aid, "completed", dict(receipts=receipts, verified=True))
        except Exception as error:
            result = dict(receipts=receipts, verified=False)
            failure = getattr(error, "failure_details", None)
            if isinstance(failure, dict):
                result["failure"] = {
                    key: str(failure[key])[:1200]
                    for key in ("tool", "code", "message")
                    if key in failure
                }
            self._update(
                aid,
                "outcome_unknown" if dispatched else "failed",
                result,
            )
        finally:
            self.stops.pop(aid, None)
        return self.get(scope, aid)
