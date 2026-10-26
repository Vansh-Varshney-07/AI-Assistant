"""Real disposable Iron Web/API, deterministic embeddings; no GUI or account."""

import importlib.util
import json
from pathlib import Path

import pytest

from tests.conftest import isolated_graphs, offline_models  # noqa: F401 -- explicit existing pytest fixtures
from tests.test_wayfinder_app import factory

spec = importlib.util.spec_from_file_location("electron_backend_host", Path(__file__).with_name("host.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def host(tmp_path):
    session = module.Session(tmp_path / "runtime", factory)
    session.start()
    yield session
    session.close()


def seed(host):
    sid = host.call("create_space", {"name": "Synthetic desktop verification"})["id"]
    return sid, {"space": sid, "task": "general"}


def test_live_api_boot_scope_and_snapshot(host):
    sid, scope = seed(host)
    result = host.describe()
    assert result["state"] == "ready"
    assert result["capabilities"]["memory"] is True
    assert result["capabilities"]["general_chat"] is False
    assert result["capabilities"]["native_desktop"] is False
    snapshot = host.snapshot({"space": sid})
    assert snapshot["actions"] == snapshot["workflows"] == snapshot["jobs"] == []
    assert snapshot["metrics"]["model_tokens"] is None
    with pytest.raises(ValueError):
        host.snapshot({"space": "foreign"})


def test_memory_proposal_exact_receipt_and_recall_via_existing_api(host):
    sid, scope = seed(host)
    item = host.call("platform_memory_propose", dict(scope, request_id="once", body=dict(
        text="Synthetic retention is 30 days.", subject="me", predicate="retention_days",
        value=30, task_id="general", action="assert")))
    assert item["status"] == "pending"
    assert host.call("recall", {"space": sid, "predicate": "retention_days"})["packet"]["evidence"] == []
    with pytest.raises(ValueError):
        host.call("platform_memory_decide", dict(scope, id=item["id"], digest="changed", approve=True))
    result = host.call("platform_memory_decide", dict(scope, id=item["id"], digest=item["digest"], approve=True))
    assert result["status"] == "completed"
    assert result["result"]["verified"] is True
    assert host.snapshot({"space": sid})["actions"][0]["id"] == item["id"]
    packet = host.call("recall", {"space": sid, "predicate": "retention_days"})["packet"]
    assert packet["evidence"][0]["value"] == 30
    replay = host.call("platform_memory_decide", dict(scope, id=item["id"], digest=item["digest"], approve=True))
    assert replay["id"] == item["id"]
    assert len(host.call("inventory", {"space": sid})["records"]) == 1


def test_selected_file_grant_revoke_and_foreign_scope(host, tmp_path):
    sid, scope = seed(host)
    selected = tmp_path / "selected.md"
    selected.write_text("Synthetic selected evidence", encoding="utf-8")
    grant = host.call("worker_grant", dict(scope, path=str(selected)))
    files = host.call("worker_search", dict(scope, grant=grant["id"]))
    assert files["files"][0]["name"] == "selected.md"
    host.call("worker_revoke", dict(scope, grant=grant["id"]))
    with pytest.raises(ValueError):
        host.call("worker_search", dict(scope, grant=grant["id"]))


@pytest.mark.parametrize("operation", ["worker_action_decide", "platform_google_read", "propose", "decide", "chat_start", "schedule_create"])
def test_unqualified_or_legacy_approval_routes_excluded(host, operation):
    with pytest.raises(ValueError, match="not included"):
        host.call(operation, {})


def test_unqualified_model_and_native_workers_cannot_start(host):
    sid, scope = seed(host)
    with pytest.raises(ValueError, match="Only the qualified"):
        host.call("worker_start", dict(scope, role="W37", question="click"))
    with pytest.raises(ValueError, match="Runtime"):
        host.call("worker_start", dict(scope, role="W35", question="read", reference="r"))
    assert host.snapshot({"space": sid})["jobs"] == []


def test_background_settings_and_secret_exposure(host):
    with pytest.raises(ValueError, match="Background"):
        host.call("settings", {"value": {"font_size": 14, "background": True}})
    serialized = json.dumps(host.describe())
    assert host.service.token not in serialized


def test_unresolved_action_guard_does_not_depend_on_recent_display_limit(host):
    sid, scope = seed(host)
    encoded = json.dumps((host.service.owner, sid, "general"))
    with host.service.db() as db:
        db.execute("INSERT INTO memory_actions VALUES (?,?,?,?,?,?,?)", ("older-unknown", encoded, "{}", "digest", 1.0, "outcome_unknown", None))
        for i in range(65):
            db.execute("INSERT INTO memory_actions VALUES (?,?,?,?,?,?,?)", (f"newer-{i}", encoded, "{}", "digest", 1.0, "rejected", None))
    assert all(row["id"] != "older-unknown" for row in host.snapshot({"space": sid})["actions"])
    with pytest.raises(ValueError, match="unresolved"):
        host.call("platform_memory_propose", dict(scope, request_id="must-not-dispatch", body={}))


def test_retry_inspection_refuses_foreign_scope_before_reading_inputs(host):
    seed(host)
    with pytest.raises(ValueError):
        host.call("retry_details", {"space": "foreign", "id": "guessed"})
    with pytest.raises(ValueError):
        host.call("retry_details", {"space": "foreign", "id": "guessed", "question": "replacement"})


def test_failed_contract_boot_closes_transport_and_releases_owned_runtime(tmp_path, monkeypatch):
    import wayfinder.api as api

    servers, serve, call = [], api.serve, api.Client.call

    def track(service):
        server = serve(service)
        servers.append(server)
        return server

    def unsupported(client, operation, **body):
        result = call(client, operation, **body)
        return dict(result, contract="unsupported") if operation == "status" else result

    session = module.Session(tmp_path / "failed-contract-runtime", factory)
    with monkeypatch.context() as patch:
        patch.setattr(api, "serve", track)
        patch.setattr(api.Client, "call", unsupported)
        with pytest.raises(ValueError, match="Unsupported backend"):
            session.start()
    assert servers[0].socket.fileno() == -1
    assert session.service is None
    try:
        assert session.start()["state"] == "ready"
    finally:
        session.close()
