"""Real storage/API checks; fixture embeddings remain confined to isolated tests."""

import json
import threading
import uuid
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest

from memory.engine import MemoryEngine
from memory.workbench import Workbench
from tests.fixtures.graph import graph_name_for
from workbench_server import handler_for


def request(mode="retrieve", namespace="validation", **kwargs):
    return dict(
        prompt="A local workbench validation probe.",
        mode=mode,
        namespace=namespace,
        session_id=uuid.uuid4().hex,
        request_id=uuid.uuid4().hex,
        **kwargs,
    )


@pytest.fixture
def bench(tmp_path):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "vectors")
    ) as engine:
        yield Workbench(engine)


def claim(value, action="assert", **kwargs):
    return dict(
        subject="manual-user",
        predicate="probe_field",
        value=value,
        kind="fact",
        action=action,
        **kwargs,
    )


def test_empty_retrieval_is_truthful_and_read_only(bench):
    result = bench.run(request())
    assert result["ok"] and result["diagnostics"]["pipeline_invoked"]
    assert result["diagnostics"]["methods"] == ["MemoryEngine.search"]
    assert result["diagnostics"]["retrieval_ran"] is False
    assert result["diagnostics"]["retrieval_completed"] is True
    assert bench.inspection.inventory()["records"] == []


def test_namespace_evidence_and_no_current_prompt_leak(bench):
    a = bench.run(request("store", namespace="north"))
    b = bench.run(request("store", namespace="south"))
    assert a["ok"] and b["ok"]
    assert a["diagnostics"]["storage_confirmed"] is True
    assert a["retrieved"] == []  # Retrieval occurred before the new source existed.
    output = bench.run(request(namespace="north"))
    assert output["diagnostics"]["retrieved_memory_ids"] == [a["stored"]["memory_id"]]
    assert output["retrieved"][0]["retrieval_trace"]["selection_rank"] == 1
    assert output["retrieved"][0]["retrieval_trace"]["total_retrieval_ms"] >= 0
    all_records = bench.inspection.inventory()["records"]
    assert len(all_records) == 2
    assert {r["namespace"] for r in all_records} == {"north", "south"}
    assert all(r["updated_timestamp"] is None for r in all_records)
    assert all(r["payload"] and r["observations"] and r["sources"] for r in all_records)


def test_explicit_correction_and_conflict_states_are_engine_evidence(bench):
    a = bench.run(request("claim", claims=[claim("old")], confirmed=True))
    old = a["stored"]["claims"][0]["claim_id"]
    b = bench.run(
        request(
            "claim",
            claims=[claim("new", "correct", targets=[old], reason="Manual correction")],
            confirmed=True,
        )
    )
    assert b["ok"]
    assert b["diagnostics"]["changed_claims"][0]["after"] == "corrected"
    packet = bench.run(request("recall", predicate="probe_field"))["recall"]
    assert packet["answer_status"] == "supported"
    assert [c["value"] for c in packet["evidence"]] == ["new"]
    assert bench.inspection.detail(a["stored"]["memory_id"])["statuses"] == [
        "corrected"
    ]
    assert len(bench.inspection.inventory()["records"]) == 2
    c = bench.run(request("claim", claims=[claim("another")], confirmed=True))
    assert c["ok"]
    packet = bench.run(request("recall", predicate="probe_field"))["recall"]
    assert packet["answer_status"] == "disputed"
    assert {c["value"] for c in packet["evidence"]} == {"new", "another"}


def test_change_cannot_target_other_namespace_and_needs_confirmation(bench):
    a = bench.run(
        request("claim", namespace="north", claims=[claim("old")], confirmed=True)
    )
    old = a["stored"]["claims"][0]["claim_id"]
    target = claim("new", "supersede", targets=[old], reason="Change")
    with pytest.raises(ValueError, match="confirmation"):
        bench.run(request("claim", claims=[target]))
    result = bench.run(
        request("claim", namespace="south", claims=[target], confirmed=True)
    )
    assert result["ok"] is False and not result["diagnostics"]["pipeline_invoked"]
    assert bench.inspection.detail(a["stored"]["memory_id"])["statuses"] == ["accepted"]


def test_retry_same_event_preserves_source_and_does_not_duplicate(bench):
    body = request("store")
    first = bench.run(body)
    second = bench.run(body)
    assert first["ok"] and second["ok"]
    assert second["diagnostics"]["created_memory_ids"] == []
    assert len(bench.inspection.inventory()["records"]) == 1
    changed = bench.run(dict(body, prompt="Changed event content"))
    assert changed["ok"] is False
    assert (
        bench.inspection.detail(first["stored"]["memory_id"])["content"]
        == body["prompt"]
    )


def test_graph_only_record_visible_and_missing_vector_not_claimed(bench):
    result = bench.run(request("store"))
    mid = result["stored"]["memory_id"]
    # Deliberate isolated-test damage, never an application repair operation.
    bench.engine.vector_store.delete_memory(mid)
    inventory = bench.inspection.inventory()["records"]
    assert len(inventory) == 1
    assert inventory[0]["graph_stored"] and not inventory[0]["vector_stored"]
    assert inventory[0]["payload"] is None and inventory[0]["namespace"] == "validation"


def test_retrieval_failure_does_not_create_memory_or_leak_driver_secret(
    bench, monkeypatch
):
    bench.run(request("store"))

    def broken(*args, **kwargs):
        raise RuntimeError("connection password=DO_NOT_EXPOSE")

    monkeypatch.setattr(bench.engine, "search", broken)
    result = bench.run(request("store"))
    assert not result["ok"]
    assert not result["diagnostics"]["retrieval_completed"]
    assert result["diagnostics"]["created_memory_ids"] == []
    assert "DO_NOT_EXPOSE" not in json.dumps(result)
    assert len(bench.inspection.inventory()["records"]) == 1


def test_inventory_scrolls_all_pages_without_neural_loading(bench, monkeypatch):
    # Exercise the adapter's pagination without inserting 100+ records in real stores.
    calls = []

    def scroll(**kwargs):
        calls.append(kwargs)
        return [], "next-page" if kwargs.get("offset") is None else None

    monkeypatch.setattr(bench.engine.vector_store, "scroll", scroll)
    assert bench.inspection.inventory()["records"] == []
    assert calls[1]["offset"] == "next-page"
    assert all(not c.get("with_vectors", False) for c in calls)
    assert bench.engine._embedder is None


def test_http_loopback_origin_token_and_no_shell_or_file_routes(bench):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(bench, "test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = HTTPConnection("127.0.0.1", server.server_port)
        conn.request("GET", "/")
        response = conn.getresponse()
        assert response.status == 200 and b"Memory Testing Workbench" in response.read()
        assert "frame-ancestors" in response.getheader("Content-Security-Policy")
        conn.request(
            "GET", "/api/memories", headers={"Origin": "https://foreign.example"}
        )
        response = conn.getresponse()
        assert response.status == 403
        response.read()
        conn.request("GET", "/api/session", headers={"Host": "foreign.example"})
        response = conn.getresponse()
        assert response.status == 403
        response.read()
        conn.request(
            "POST",
            "/api/prompt",
            body=json.dumps(request()),
            headers={"Content-Type": "application/json"},
        )
        response = conn.getresponse()
        assert response.status == 403
        response.read()
        conn.request(
            "POST",
            "/api/prompt",
            body=json.dumps(request()),
            headers={
                "Content-Type": "application/json",
                "X-Workbench-Token": "test-token",
            },
        )
        response = conn.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["ok"]
        conn.request("GET", "/../../config.yaml")
        response = conn.getresponse()
        assert response.status == 404
        response.read()
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_authenticated_stop_returns_and_shuts_down_server(bench):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(bench, "test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = HTTPConnection("127.0.0.1", server.server_port)
        conn.request(
            "POST",
            "/api/stop",
            body="{}",
            headers={
                "Content-Type": "application/json",
                "X-Workbench-Token": "test-token",
            },
        )
        response = conn.getresponse()
        assert (
            response.status == 200
            and json.loads(response.read())["status"] == "stopping"
        )
        thread.join(timeout=5)
        assert not thread.is_alive()
        conn.close()
        assert bench.engine.storage_status()["memories"] == 0
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.neural
def test_real_cached_model_storage_retrieval_and_restart(tmp_path, monkeypatch):
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    graph = graph_name_for(tmp_path)
    path = str(tmp_path / "real-vectors")
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=path, graph_name=graph
    ) as engine:
        bench = Workbench(engine)
        result = bench.run(
            request("claim", claims=[claim("local-validation-marker")], confirmed=True)
        )
        assert result["ok"] and result["diagnostics"]["storage_confirmed"]
        mid = result["stored"]["memory_id"]
        assert engine.embedder._providers == ["CPUExecutionProvider"]
    # New engine, embedded-store handle, adapter and session; same durable storage.
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=path, graph_name=graph
    ) as engine:
        bench = Workbench(engine)
        result = bench.run(request())
        assert result["ok"] and mid in result["diagnostics"]["retrieved_memory_ids"]
        assert result["retrieved"][0]["retrieval_trace"]["total_retrieval_ms"] >= 0
        result = bench.run(request("recall", predicate="probe_field"))
        assert result["recall"]["answer_status"] == "supported"
        assert result["recall"]["evidence"][0]["value"] == "local-validation-marker"
