"""Phases 0–2: real disposable FalkorDB + embedded Qdrant, offline test embeddings."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
from http.client import HTTPConnection
import json

import pytest

from memory.engine import MemoryEngine
from wayfinder.api import Client, serve, wire
from wayfinder.runtime import backup, open_service, restore
from wayfinder.service import AccessDenied, Identity, StaleContext, uid


def factory(root):
    return MemoryEngine(
        qdrant_path=str(root / "vectors"),
        graph_name="test_wayfinder_"
        + hashlib.sha256(str(root).encode()).hexdigest()[:18],
        config={"extraction_policy": "none"},
    )


@pytest.fixture
def app(tmp_path):
    app = open_service(tmp_path / "runtime", factory)
    yield app
    app.close()


def space(app, name="Cedar", who=None):
    return app.call(who or Identity(app.owner), "create_space", {"name": name})["id"]


def call(app, operation, **body):
    return app.call(Identity(app.owner), operation, body)


def propose(app, sid, value=30, **kwargs):
    request = kwargs.pop("request", uid())
    body = dict(
        text=f"Cedar retention is {value} days.",
        predicate="retention_days",
        value=value,
        **kwargs,
    )
    return call(app, "propose", space=sid, request=request, body=body)


def approve(app, sid, proposal):
    return call(app, "decide", space=sid, proposal=proposal["id"], approve=True)


def recall(app, sid, **kwargs):
    return call(app, "recall", space=sid, predicate="retention_days", **kwargs)


def values(result):
    return [e["value"] for e in result["packet"]["evidence"]]


def test_consent_isolation_fresh_conversation_and_transcript_separation(app):
    cedar, maple = space(app), space(app, "Maple")
    pending = propose(app, cedar)
    assert values(recall(app, cedar)) == []
    approved = approve(app, cedar, pending)
    assert approved["result"]["stored"] is True
    for _ in range(2):
        conv = call(app, "conversation", space=cedar)
        assert values(recall(app, cedar)) == [30]
        call(
            app,
            "transcript",
            space=cedar,
            conversation=conv["conversation"],
            id=uid(),
            text="Retention is 99 days (transcript only)",
        )
    assert values(recall(app, maple)) == []
    assert values(recall(app, cedar)) == [30]
    assert len(call(app, "inventory", space=cedar)["records"]) == 1
    assert approved["result"]["memory_id"] in {
        e["memory_id"] for e in recall(app, cedar)["packet"]["evidence"]
    }


def test_correction_rejection_history_conflict_and_missing(app):
    sid = space(app)
    first = approve(app, sid, propose(app, sid))
    target = first["result"]["claim_ids"]
    rejected = propose(
        app, sid, 7, action="correct", targets=target, reason="User correction"
    )
    call(app, "decide", space=sid, proposal=rejected["id"], approve=False)
    assert values(recall(app, sid)) == [30]
    correction = approve(
        app,
        sid,
        propose(
            app, sid, 7, action="correct", targets=target, reason="User correction"
        ),
    )
    assert values(recall(app, sid)) == [7]
    history = recall(app, sid, temporal_mode="historical")
    assert 30 in values(history)
    source = call(app, "source", space=sid, memory_id=first["result"]["memory_id"])
    assert source["claims"][0]["changed_by"]
    assert correction["result"]["claim_ids"]
    approve(app, sid, propose(app, sid, 14))
    assert recall(app, sid)["packet"]["answer_status"] == "disputed"
    missing = call(app, "recall", space=sid, predicate="unknown_field")
    assert missing["packet"]["answer_status"] == "missing"
    assert missing["packet"]["evidence"] == []


def test_immutable_replay_concurrent_approval_and_independent_space_ids(app):
    a, b = space(app), space(app)
    request = uid()
    p = propose(app, a, request=request)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: approve(app, a, p), range(2)))
    assert results[0]["result"] == results[1]["result"]
    assert propose(app, a, request=request)["id"] == p["id"]
    with pytest.raises(ValueError, match="immutable"):
        propose(app, a, 8, request=request)
    other = approve(app, b, propose(app, b, request=request))
    assert other["result"]["memory_id"] != results[0]["result"]["memory_id"]
    assert len(call(app, "inventory", space=a)["records"]) == 1


def test_authenticated_http_role_and_foreign_space_deny_before_inspection(
    app, monkeypatch
):
    sid = space(app)
    approve(app, sid, propose(app, sid))
    app.credentials["worker-test"] = Identity(app.owner, "worker")
    app.credentials["other-owner-test"] = Identity("different-owner")
    server = serve(app)
    original = app.inspection.inventory

    def must_not_read(*args, **kwargs):
        pytest.fail("Unauthorized request reached records")

    monkeypatch.setattr(app.inspection, "inventory", must_not_read)
    try:
        for token in ("bad", "worker-test", "other-owner-test"):
            with pytest.raises(ValueError):
                Client(server.server_port, token).call("inventory", space=sid)
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request(
            "POST",
            "/v2/inventory",
            json.dumps({"space": sid}),
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + app.token,
                "Origin": "https://attacker.invalid",
            },
        )
        assert connection.getresponse().status == 403
        connection.close()
        monkeypatch.setattr(app.inspection, "inventory", original)
        assert (
            len(
                Client(server.server_port, app.token).call("inventory", space=sid)[
                    "records"
                ]
            )
            == 1
        )
    finally:
        server.shutdown()
        server.server_close()


def test_target_task_and_conversation_boundaries(app):
    a, b = space(app), space(app, "Maple")
    first = approve(app, a, propose(app, a))
    for sid, task in ((b, "general"), (a, "other-task")):
        with pytest.raises(AccessDenied):
            propose(
                app,
                sid,
                7,
                task_id=task,
                action="correct",
                targets=first["result"]["claim_ids"],
                reason="escape",
            )
    conv = call(app, "conversation", space=a)
    with pytest.raises(AccessDenied):
        call(app, "conversation", space=b, conversation=conv["conversation"])
    assert values(recall(app, a, task_id="different")) == []
    record = call(app, "source", space=a, memory_id=first["result"]["memory_id"])
    assert record["claims"][0]["scope"]["contract"] == "wayfinder_memory_v2"
    with pytest.raises(ValueError):
        call(app, "recall", space=a, predicate="retention_days", owner="spoof")


def test_context_proof_scope_stale_approval_and_mid_request_change(app, monkeypatch):
    a, b = space(app), space(app)
    approve(app, a, propose(app, a))
    context = recall(app, a)
    assert call(app, "validate_context", space=a, proof=context["proof"])["valid"]
    with pytest.raises(StaleContext):
        call(app, "validate_context", space=b, proof=context["proof"])
    stale = propose(app, a, 7)
    approve(app, a, propose(app, a, 14))
    with pytest.raises(StaleContext):
        approve(app, a, stale)
    with pytest.raises(StaleContext):
        call(app, "validate_context", space=a, proof=context["proof"])
    original = app.engine.recall

    def racing(*args, **kwargs):
        result = original(*args, **kwargs)
        approve(app, a, propose(app, a, 21))
        return result

    monkeypatch.setattr(app.engine, "recall", racing)
    with pytest.raises(StaleContext, match="during recall"):
        recall(app, a)


def test_storage_failure_no_false_receipt_and_safe_retry(app, monkeypatch):
    sid = space(app)
    pending = propose(app, sid)
    original = app.engine.add

    def fail(*args, **kwargs):
        raise OSError("fixture storage failure")

    monkeypatch.setattr(app.engine, "add", fail)
    with pytest.raises(OSError):
        approve(app, sid, pending)
    row = call(app, "proposals", space=sid)[0]
    assert row["status"] == "applying" and row["result"] is None
    assert values(recall(app, sid)) == []
    monkeypatch.setattr(app.engine, "add", original)
    assert approve(app, sid, pending)["result"]["stored"]


def test_forget_failure_blocks_reads_and_retry_scrubs_copies(app, monkeypatch):
    sid = space(app)
    saved = approve(app, sid, propose(app, sid))
    mid = saved["result"]["memory_id"]
    pending = call(
        app,
        "propose",
        space=sid,
        request=uid(),
        body=dict(operation="forget", memory_id=mid),
    )
    original = app.engine.delete

    def fail(*args, **kwargs):
        raise OSError("fixture delete failure")

    monkeypatch.setattr(app.engine, "delete", fail)
    with pytest.raises(OSError):
        approve(app, sid, pending)
    with pytest.raises(ValueError, match="Deletion recovery"):
        recall(app, sid)
    monkeypatch.setattr(app.engine, "delete", original)
    assert approve(app, sid, pending)["result"]["deleted"]
    assert values(recall(app, sid)) == []
    assert call(app, "inventory", space=sid)["records"] == []
    forgotten = next(
        r for r in call(app, "proposals", space=sid) if r["id"] == saved["id"]
    )
    assert forgotten["body"] == {} and forgotten["result"] is None
    assert approve(app, sid, saved)["status"] == "forgotten"


def test_restart_backup_restore_checksums_and_deletion_reconciliation(tmp_path):
    runtime = tmp_path / "cold"
    app = open_service(runtime, factory)
    sid = space(app)
    first = approve(app, sid, propose(app, sid))
    mid, owner = first["result"]["memory_id"], app.owner
    call(app, "settings", value=dict(font_size=14, background=False))
    app.close()
    snapshot = tmp_path / "snapshot"
    assert backup(runtime, snapshot, factory)["files"] > 2
    restored = tmp_path / "restore"
    assert restore(snapshot, restored, runtime, factory)["live_overwritten"] is False
    other = open_service(restored, factory)
    assert other.owner == owner
    assert values(recall(other, sid)) == [30]
    assert call(other, "inventory", space=sid)["records"][0]["memory_id"] == mid
    other.close()
    app = open_service(runtime, factory)
    assert call(app, "settings")["font_size"] == 14
    forget = call(
        app,
        "propose",
        space=sid,
        request=uid(),
        body=dict(operation="forget", memory_id=mid),
    )
    approve(app, sid, forget)
    app.close()
    restored2 = tmp_path / "restore-after-forget"
    assert restore(snapshot, restored2, runtime, factory)["reconciled_deletions"] == 1
    other = open_service(restored2, factory)
    assert values(recall(other, sid)) == []
    other.close()
    app = open_service(runtime, factory)
    assert values(recall(app, sid)) == []
    app.close()
    with pytest.raises(ValueError, match="fresh"):
        restore(snapshot, runtime, runtime, factory)
    (snapshot / "graph.json").write_text("corruption", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        restore(snapshot, tmp_path / "badrestore", runtime, factory)


def test_single_owner_settings_validation_message_replay_and_wire_precision(app):
    with pytest.raises(RuntimeError):
        open_service(app.root, factory)
    with pytest.raises(ValueError):
        call(app, "settings", value=dict(font_size=999, background=True))
    with pytest.raises(ValueError):
        call(
            app, "settings", value=dict(font_size=14, background=True, api_key="never")
        )
    sid = space(app)
    conv = call(app, "conversation", space=sid)["conversation"]
    payload = dict(space=sid, conversation=conv, id=uid(), text="a transcript")
    call(app, "transcript", **payload)
    assert len(call(app, "transcript", **payload)["messages"]) == 1
    with pytest.raises(ValueError, match="different"):
        call(app, "transcript", **dict(payload, text="changed"))
    assert wire({"valid_until": 2**63 - 1})["valid_until"] == str(2**63 - 1)


def test_commit_before_receipt_failure_reconciles_without_duplicate(app, monkeypatch):
    sid = space(app)
    pending = propose(app, sid)
    original = app.engine.add

    def committed_then_failed(*args, **kwargs):
        original(*args, **kwargs)
        raise OSError("fixture receipt interruption after commit")

    monkeypatch.setattr(app.engine, "add", committed_then_failed)
    with pytest.raises(OSError):
        approve(app, sid, pending)
    assert call(app, "proposals", space=sid)[0]["result"] is None
    monkeypatch.setattr(app.engine, "add", original)
    assert approve(app, sid, pending)["result"]["stored"]
    assert len(call(app, "inventory", space=sid)["records"]) == 1


def test_failed_uncommitted_write_cannot_use_stale_approval(app, monkeypatch):
    sid = space(app)
    pending = propose(app, sid)
    original = app.engine.add

    def fail(*args, **kwargs):
        raise OSError("fixture write failed before commit")

    monkeypatch.setattr(app.engine, "add", fail)
    with pytest.raises(OSError):
        approve(app, sid, pending)
    monkeypatch.setattr(app.engine, "add", original)
    approve(app, sid, propose(app, sid, 7))
    with pytest.raises(StaleContext):
        approve(app, sid, pending)
    assert values(recall(app, sid)) == [7]


def test_startup_failure_releases_engine_and_owner_for_retry(tmp_path, monkeypatch):
    import wayfinder.runtime as runtime_module

    original = runtime_module.AppService

    def fail(*args, **kwargs):
        raise OSError("fixture application-state initialization failure")

    monkeypatch.setattr(runtime_module, "AppService", fail)
    with pytest.raises(OSError):
        open_service(tmp_path / "startup", factory)
    monkeypatch.setattr(runtime_module, "AppService", original)
    recovered = open_service(tmp_path / "startup", factory)
    assert recovered.call(Identity(recovered.owner), "status", {})["memory"] == "online"
    recovered.close()
