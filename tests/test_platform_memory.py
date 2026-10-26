"""Real disposable Iron Web integration. No live data, model inference or desktop."""

from concurrent.futures import ThreadPoolExecutor
import json

import pytest

from wayfinder.api import Client, serve
from wayfinder.runtime import open_service
from wayfinder.service import Identity
from tests.test_wayfinder_app import factory


@pytest.fixture
def memory(tmp_path):
    app = open_service(tmp_path / "runtime", factory)
    server = serve(app)
    client = Client(server.server_port, app.token)
    args = dict(
        space=client.call("create_space", name="Synthetic maintenance")["id"],
        task="fixture",
    )
    yield app, client, args
    server.shutdown()
    server.server_close()
    app.close()


def proposal(client, args, **changes):
    return client.call(
        "platform_memory_propose",
        **args,
        request_id=changes.pop("request_id", "once"),
        body=dict(
            dict(
                text="Synthetic retention is thirty days.",
                predicate="retention_days",
                value=30,
                task_id=args["task"],
            ),
            **changes,
        ),
    )


def decide(client, args, item, approve=True):
    return client.call(
        "platform_memory_decide",
        **args,
        id=item["id"],
        digest=item["digest"],
        approve=approve,
    )


def recall(client, args):
    return client.call(
        "platform_context", **args, query=dict(predicate="retention_days")
    )


def test_preview_has_no_storage_effect_and_exact_approval_stores_once(memory):
    app, client, args = memory
    revision = app.revision()
    preview = client.call(
        "platform_memory_preview",
        **args,
        body=dict(
            text="Synthetic fact",
            predicate="retention_days",
            value=30,
            task_id=args["task"],
        ),
    )
    assert preview["dry_run"] and preview["executed"] is False
    with app.db() as db:
        assert db.execute("SELECT count(*) FROM proposals").fetchone()[0] == 0
    assert app.revision() == revision
    item = proposal(client, args)
    assert recall(client, args)["evidence"] == []
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: decide(client, args, item), range(2)))
    assert all(r["status"] == "completed" and r["result"]["verified"] for r in results)
    assert len(client.call("inventory", space=args["space"])["records"]) == 1
    assert recall(client, args)["evidence"][0]["value"] == 30
    assert proposal(client, args)["id"] == item["id"]


def test_conflict_correction_and_retraction_preserve_history(memory):
    app, client, args = memory
    first = decide(client, args, proposal(client, args))
    first_mid = first["result"]["receipts"][0]["memory_id"]
    # Use the existing recall status for conflict analysis; do not invent a resolver.
    conflict = proposal(client, args, request_id="conflict", value=42)
    decide(client, args, conflict)
    packet = recall(client, args)
    assert packet["status"] != "supported"
    targets = [r["claim_id"] for r in packet["evidence"]]
    corrected = proposal(
        client,
        args,
        request_id="correction",
        action="correct",
        targets=targets,
        reason="Synthetic owner confirmation.",
        value=35,
    )
    assert decide(client, args, corrected)["status"] == "completed"
    packet = recall(client, args)
    assert packet["status"] == "supported" and packet["evidence"][0]["value"] == 35
    retract = proposal(
        client,
        args,
        request_id="retract",
        action="retract",
        targets=[packet["evidence"][0]["claim_id"]],
        reason="Synthetic maintenance review.",
        value=None,
    )
    assert decide(client, args, retract)["status"] == "completed"
    assert recall(client, args)["status"] != "supported"
    assert app.engine.get(first_mid) is not None  # Historical evidence was not purged.


@pytest.mark.parametrize(
    "mode", ["reject", "revoke", "expire", "stale", "digest", "payload"]
)
def test_denial_modes_never_publish(memory, mode):
    app, client, args = memory
    item = proposal(client, args)
    if mode == "reject":
        assert decide(client, args, item, False)["status"] == "rejected"
    elif mode == "revoke":
        assert (
            client.call("platform_memory_revoke", **args, id=item["id"])["status"]
            == "revoked"
        )
        assert decide(client, args, item)["status"] == "revoked"
    elif mode == "expire":
        app.platform.memory.actions.clock = lambda: item["expires"] + 1
        assert decide(client, args, item)["status"] == "expired"
    elif mode == "stale":
        other = proposal(client, args, request_id="other", value=42)
        decide(client, args, other)
        assert decide(client, args, item)["status"] == "failed"
        assert recall(client, args)["evidence"][0]["value"] == 42
        return
    else:
        if mode == "digest":
            item["digest"] = "0" * 64
        else:
            with app.db() as db:
                changed = dict(item["plan"])
                changed["body"]["value"] = 99
                db.execute(
                    "UPDATE memory_actions SET body=? WHERE id=?",
                    (json.dumps(changed), item["id"]),
                )
        with pytest.raises(ValueError, match="reviewed"):
            decide(client, args, item)
    assert recall(client, args)["evidence"] == []


def test_cross_task_worker_and_changed_requests_are_denied(memory):
    app, client, args = memory
    item = proposal(client, args)
    with pytest.raises(ValueError):
        proposal(client, args, value=99)
    with pytest.raises(ValueError):
        proposal(client, dict(args, task="other"), task_id=args["task"])
    with pytest.raises(ValueError):
        client.call(
            "platform_memory_decide",
            **dict(args, task="other"),
            id=item["id"],
            digest=item["digest"],
            approve=True,
        )
    with pytest.raises(ValueError):
        app.call(
            Identity(app.owner, "worker"),
            "platform_memory_propose",
            dict(args, body=item["plan"]["body"], request_id="worker"),
        )
    decide(client, args, item)
    targets = [recall(client, args)["evidence"][0]["claim_id"]]
    with pytest.raises(ValueError):
        proposal(
            client,
            dict(args, task="other"),
            action="retract",
            targets=targets,
            reason="wrong task",
        )


def test_lost_ack_reconciles_read_only_and_never_replays(memory, monkeypatch):
    app, client, args = memory
    item = proposal(client, args)
    driver = app.platform.memory.driver
    original = driver.perform
    calls = []

    def lost(*values):
        calls.append(1)
        original(*values)
        raise RuntimeError("Synthetic lost acknowledgement")

    monkeypatch.setattr(driver, "perform", lost)
    assert decide(client, args, item)["status"] == "outcome_unknown"
    assert decide(client, args, item)["status"] == "outcome_unknown" and len(calls) == 1
    revision = app.revision()
    result = client.call("platform_memory_reconcile", **args, id=item["id"])
    assert result["status"] == "completed" and result["reconciliation"]["verified"]
    assert app.revision() == revision
    assert (
        client.call("platform_memory_audit", **args, id=item["id"])[-1]["event"]
        == "reconciled"
    )


def test_restart_expires_pending_and_no_replay(memory):
    app, client, args = memory
    item = proposal(client, args)
    from wayfinder.platform.memory_control import MemoryControl

    app.platform.memory.close()
    app.platform.memory = MemoryControl(app)
    assert decide(client, args, item)["status"] == "expired"
    assert recall(client, args)["evidence"] == []


def test_managed_memory_cannot_bypass_gate_through_legacy_decide(memory):
    _, client, args = memory
    item = proposal(client, args)
    with pytest.raises(ValueError, match="platform approval"):
        client.call(
            "decide",
            space=args["space"],
            proposal=item["plan"]["proposal_ref"],
            approve=True,
        )
    assert recall(client, args)["evidence"] == []
    assert decide(client, args, item)["status"] == "completed"


def test_expiry_at_actual_memory_dispatch_prevents_effect(memory, monkeypatch):
    app, client, args = memory
    item = proposal(client, args)
    driver = app.platform.memory.driver
    original = app.decide

    def delay(*values, **kwargs):
        driver.clock = lambda: item["expires"] + 1
        return original(*values, **kwargs)

    monkeypatch.setattr(app, "decide", delay)
    outcome = decide(client, args, item)
    assert outcome["status"] == "outcome_unknown"
    assert recall(client, args)["evidence"] == []
    assert (
        client.call("platform_memory_reconcile", **args, id=item["id"])[
            "reconciliation"
        ]["verified"]
        is False
    )
