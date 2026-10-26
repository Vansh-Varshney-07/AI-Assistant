"""Historical artifact checks and telemetry, using the existing workflow lifecycle."""

import hashlib
import json
import statistics
from typing import Literal
import uuid

from pydantic import Field

from wayfinder.platform.contracts import Contract, ReadRequest, VERSION


class EvaluationRequest(Contract):
    contract: Literal["wayfinder.platform/1"] = VERSION
    request_id: str = Field(min_length=1, max_length=100)
    required_phrases: list[str] = Field(default_factory=list, max_length=8)
    expected_file_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


SCHEMAS = {
    "platform_workflow_evaluate": {"id", "request"},
    "platform_workflow_metrics": {"limit"},
    "platform_read_retry": {"id", "request_id", "reference"},
    "platform_read_clear": {"id"},
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class WorkflowReview:
    def __init__(self, platform):
        self.platform, self.app = platform, platform.app
        with self.app.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS platform_evaluations(
                    scope TEXT,workflow TEXT,request TEXT,digest TEXT,result TEXT,
                    PRIMARY KEY(scope,workflow,request));
                CREATE TABLE IF NOT EXISTS platform_retries(
                    scope TEXT,source TEXT,request TEXT,digest TEXT,child TEXT,
                    PRIMARY KEY(scope,source));
            """)

    def call(self, who, scope, operation, body):
        self.app.authorize(who)
        self.app.space(who, scope.space)
        if (
            who.owner != scope.owner
            or operation not in SCHEMAS
            or set(body) - (SCHEMAS[operation] | {"space", "task"})
        ):
            raise ValueError("Invalid workflow review or scope.")
        p = self.platform
        with p.lock:
            if p.closed or self.app.closed:
                raise ValueError("Workflow review is stopped.")
            if operation == "platform_workflow_metrics":
                return self.metrics(scope, body.get("limit", 100))
            row = p._row(scope, body.get("id"))
            if operation == "platform_workflow_evaluate":
                return self.evaluate(
                    scope, row, EvaluationRequest.model_validate(body.get("request"))
                )
            if operation == "platform_read_clear":
                if row["status"] not in {
                    "completed",
                    "failed",
                    "blocked",
                    "cancelled",
                    "timed_out",
                    "stale",
                    "interrupted",
                    "cleared",
                }:
                    raise ValueError("Stop active work before clearing its artifact.")
                with self.app.db() as db:
                    # Keep immutable request/digest and retry identities for deduplication.
                    db.execute(
                        "UPDATE platform_workflows SET body='{}',context=NULL,result=NULL WHERE id=? AND scope=?",
                        (row["id"], canonical(scope.model_dump())),
                    )
                    db.execute(
                        "DELETE FROM platform_evaluations WHERE workflow=? AND scope=?",
                        (row["id"], canonical(scope.model_dump())),
                    )
                p._transition(
                    scope,
                    row["id"],
                    "cleared",
                    dict(artifact_removed=True, worker_artifact_retained=True),
                )
                return p._public(p._row(scope, row["id"]))
            if operation == "platform_read_retry":
                return self.retry(who, scope, row, body)
            raise ValueError("Unknown workflow review operation.")

    def metrics(self, scope, limit):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Metrics limit must be 1–100.")
        with self.app.db() as db:
            rows = db.execute(
                "SELECT w.status,w.created,w.job,(SELECT min(a.at) FROM platform_audit a WHERE a.workflow=w.id AND a.scope=w.scope AND a.status IN ('completed','failed','blocked','cancelled','timed_out','stale','interrupted')) AS observed FROM platform_workflows w WHERE w.scope=? ORDER BY w.created DESC LIMIT ?",
                (canonical(scope.model_dump()), limit),
            ).fetchall()
        counts, elapsed = {}, []
        for row in rows:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
            if row["status"] in {
                "completed",
                "failed",
                "blocked",
                "cancelled",
                "timed_out",
                "stale",
                "interrupted",
                "cleared",
            }:
                elapsed.append(
                    max(0, (row["observed"] or row["created"]) - row["created"])
                )
        return dict(
            contract=VERSION,
            sampled=len(rows),
            sample_limit=limit,
            status_counts=counts,
            worker_dispatches=sum(bool(r["job"]) for r in rows),
            median_elapsed_seconds=round(statistics.median(elapsed), 3)
            if elapsed
            else None,
            max_elapsed_seconds=round(max(elapsed), 3) if elapsed else None,
            model_tokens=None,
            cost=None,
            quality="Explicit artifact checks only; no semantic accuracy claim.",
        )

    def evaluate(self, scope, row, request):
        if row["status"] != "completed":
            raise ValueError("Only a completed historical artifact can be evaluated.")
        if any(not s.strip() or len(s) > 200 for s in request.required_phrases):
            raise ValueError("Evaluation phrases require 1–200 characters.")
        key, payload = canonical(scope.model_dump()), json.loads(row["result"])
        artifact = hashlib.sha256(canonical(payload).encode()).hexdigest()
        fingerprint = hashlib.sha256(
            canonical(dict(request=request.model_dump(), artifact=artifact)).encode()
        ).hexdigest()
        with self.app.db() as db:
            old = db.execute(
                "SELECT digest,result FROM platform_evaluations WHERE scope=? AND workflow=? AND request=?",
                (key, row["id"], request.request_id),
            ).fetchone()
        if old:
            if old["digest"] != fingerprint:
                raise ValueError(
                    "Evaluation ID belongs to a different rubric or artifact."
                )
            return json.loads(old["result"])
        text, evidence = payload.get("synthesis", ""), payload.get("evidence") or {}
        checks = dict(
            bounded_answer=isinstance(text, str) and 0 < len(text) <= 12000,
            file_provenance=bool((evidence.get("file") or {}).get("sha256")),
            memory_provenance=bool((evidence.get("memory") or {}).get("revision")),
            verification_timestamp=isinstance(payload.get("verified_at"), (float, int)),
        )
        if request.expected_file_sha256:
            checks["expected_file"] = (
                evidence.get("file", {}).get("sha256") == request.expected_file_sha256
            )
        matches = [phrase in text for phrase in request.required_phrases]
        if matches:
            checks["required_phrases"] = all(matches)
        result = dict(
            contract=VERSION,
            evaluation_ref=uuid.uuid4().hex,
            workflow_ref=row["id"],
            artifact_sha256=artifact,
            evaluated_at=self.platform.clock(),
            checks=checks,
            phrase_matches=matches,
            passed=all(checks.values()),
            semantic_accuracy=None,
            fresh_for_action=False,
            limitation="Literal rubric and historical provenance checks do not establish factual accuracy or current authorization.",
        )
        with self.app.db() as db:
            db.execute(
                "INSERT INTO platform_evaluations VALUES (?,?,?,?,?)",
                (key, row["id"], request.request_id, fingerprint, canonical(result)),
            )
        return result

    def retry(self, who, scope, row, body):
        if row["status"] not in {
            "failed",
            "blocked",
            "timed_out",
            "interrupted",
            "stale",
        }:
            raise ValueError(
                "Only an unsuccessful read-only workflow is retry eligible."
            )
        request_id = body.get("request_id")
        if (
            not isinstance(request_id, str)
            or not request_id.strip()
            or len(request_id) > 100
        ):
            raise ValueError("Retry requires a bounded request ID.")
        original = ReadRequest.model_validate_json(row["body"])
        key = canonical(scope.model_dump())
        request = original.model_copy(
            update=dict(
                request_id="retry-"
                + hashlib.sha256(
                    canonical([row["id"], request_id]).encode()
                ).hexdigest(),
                reference=body.get("reference"),
            )
        )
        request = ReadRequest.model_validate(request.model_dump())
        fingerprint = hashlib.sha256(
            canonical(request.model_dump()).encode()
        ).hexdigest()
        with self.app.db() as db:
            if db.execute(
                "SELECT 1 FROM platform_retries WHERE scope=? AND child=?",
                (key, row["id"]),
            ).fetchone():
                raise ValueError("The one-retry budget is exhausted.")
            old = db.execute(
                "SELECT * FROM platform_retries WHERE scope=? AND source=?",
                (key, row["id"]),
            ).fetchone()
            if old and (old["digest"] != fingerprint or old["request"] != request_id):
                raise ValueError(
                    "A different retry already owns this workflow's retry budget."
                )
            if old and old["child"]:
                return self.platform._public(self.platform._row(scope, old["child"]))
            db.execute(
                "INSERT OR IGNORE INTO platform_retries VALUES (?,?,?,?,NULL)",
                (key, row["id"], request_id, fingerprint),
            )
        # Explicit read-only retry. start rechecks runtime, file grant and memory freshness.
        child = self.platform.start(who, scope, request)
        with self.app.db() as db:
            db.execute(
                "UPDATE platform_retries SET child=? WHERE scope=? AND source=?",
                (child["id"], key, row["id"]),
            )
        return child
