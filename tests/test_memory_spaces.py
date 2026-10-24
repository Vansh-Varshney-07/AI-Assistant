"""Memory-space boundaries against real isolated FalkorDB/Qdrant stores."""

from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import threading
import uuid

import pytest

from memory.engine import MemoryEngine
from memory.spaces import SpaceDirectory
from memory.workbench import Workbench
from tests.test_workbench import claim, request
from tests.test_hosted_boundaries import Client
from workbench_server import handler_for


@pytest.fixture
def bench(tmp_path):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "vectors")
    ) as engine:
        yield Workbench(engine)


def send(bench, space, mode="retrieve", **kwargs):
    body = dict(request(mode), **kwargs)
    body.pop("namespace")
    return bench.run(dict(body, memory_space_id=space))


def create(bench, space):
    return bench.spaces.create(dict(memory_space_id=space, name=space))


def test_spaces_persist_empty_and_duplicate_names_have_distinct_ids(tmp_path):
    path = tmp_path / "spaces.sqlite3"
    first = SpaceDirectory(path).create({"name": "Experiment"})
    second = SpaceDirectory(path).create({"name": "Experiment"})
    assert first["memory_space_id"] != second["memory_space_id"]
    assert len(SpaceDirectory(path).list()) == 2
    assert SpaceDirectory(path).require(first["memory_space_id"]) == first
    with pytest.raises(ValueError, match="already exists"):
        SpaceDirectory(path).create(dict(memory_space_id=first["memory_space_id"]))


@pytest.mark.parametrize("bad", [None, "", "../a", "a b", "a" * 41, 123])
def test_invalid_ids_fail_closed(bench, bad):
    with pytest.raises(ValueError, match="space ID"):
        send(bench, bad)
    assert bench.inspection.inventory()["records"] == []


def test_unknown_and_conflicting_space_ids_are_rejected(bench):
    create(bench, "A")
    with pytest.raises(ValueError, match="Unknown memory space"):
        send(bench, "unknown")
    with pytest.raises(ValueError, match="same space"):
        bench.run(dict(request(namespace="B"), memory_space_id="A"))
    assert bench.inspection.inventory()["records"] == []


def test_same_request_id_cannot_mix_spaces_and_replays_remain_local(bench):
    for space in ("A", "B", "empty"):
        create(bench, space)
    event = uuid.uuid4().hex
    a = send(
        bench, "A", "claim", request_id=event, claims=[claim("Apple")], confirmed=True
    )
    b = send(
        bench, "B", "claim", request_id=event, claims=[claim("Berry")], confirmed=True
    )
    assert a["ok"] and b["ok"]
    assert a["stored"]["memory_id"] != b["stored"]["memory_id"]
    for space, value, result in (("A", "Apple", a), ("B", "Berry", b)):
        output = send(bench, space, "recall", predicate="probe_field")
        assert [e["value"] for e in output["recall"]["evidence"]] == [value]
        hits = send(bench, space)["diagnostics"]["retrieved_memory_ids"]
        assert hits == [result["stored"]["memory_id"]]
        assert len(bench.inventory(space)["records"]) == 1
        assert output["memory_space_id"] == space
    assert send(bench, "empty")["retrieved"] == []
    assert (
        send(bench, "empty", "recall", predicate="probe_field")["recall"][
            "answer_status"
        ]
        == "missing"
    )
    # A replay in one space cannot return the other space's source.
    replay = send(
        bench,
        "A",
        "claim",
        request_id=event,
        claims=[claim("Apple")],
        confirmed=True,
        session_id=a["stored"]["metadata"]["session_id"],
    )
    assert replay["ok"] and replay["stored"]["memory_id"] == a["stored"]["memory_id"]
    assert replay["diagnostics"]["created_memory_ids"] == []


def test_changes_and_reserved_scope_cannot_escape_space(bench):
    create(bench, "A")
    create(bench, "B")
    a = send(bench, "A", "claim", claims=[claim("Apple")], confirmed=True)
    old = a["stored"]["claims"][0]["claim_id"]
    result = send(
        bench,
        "B",
        "claim",
        claims=[claim("Bad", "correct", targets=[old], reason="Try cross-space")],
        confirmed=True,
    )
    assert not result["ok"] and bench.inventory("B")["records"] == []
    assert (
        send(bench, "A", "recall", predicate="probe_field")["recall"]["evidence"][0][
            "value"
        ]
        == "Apple"
    )
    for scope in ({"test_namespace": "B"}, {"memory_space_id": "B"}):
        with pytest.raises(ValueError, match="scope"):
            send(bench, "A", "claim", claims=[claim("Bad", scope=scope)])


def test_graph_only_memory_keeps_its_owner(bench):
    create(bench, "A")
    create(bench, "B")
    result = send(bench, "A", "store")
    bench.engine.vector_store.delete_memory(result["stored"]["memory_id"])
    records = bench.inventory("A")["records"]
    assert len(records) == 1 and not records[0]["vector_stored"]
    assert records[0]["memory_space_id"] == "A"
    assert bench.inventory("B")["records"] == []


def test_legacy_namespaces_remain_switchable_without_migration(bench):
    result = bench.run(request("store", namespace="old_test"))
    assert result["ok"]
    restored = Workbench(bench.engine)
    assert "old_test" in {s["memory_space_id"] for s in restored.list_spaces()}
    assert send(restored, "old_test")["diagnostics"]["retrieved_memory_ids"] == [
        result["stored"]["memory_id"]
    ]


def test_legacy_receipt_replays_and_alias_spelling_is_idempotent(bench):
    body = dict(
        request("claim", namespace="legacy"), claims=[claim("old")], confirmed=True
    )
    validated = bench.validate(body)[-1]
    mid = "wb_" + body["request_id"]
    bench.engine.add(
        body["prompt"],
        memory_id=mid,
        claims=validated,
        source_info=dict(
            origin="user",
            actor_id="workbench:legacy",
            user_confirmed=True,
            event_id=body["request_id"],
            quality=0.9,
        ),
        metadata=dict(
            source="manual_workbench",
            test_namespace="legacy",
            session_id=body["session_id"],
        ),
    )
    bench.list_spaces()
    replay = bench.run(body)
    assert replay["ok"] and replay["stored"]["memory_id"] == mid
    modern = dict(body, memory_space_id=body["namespace"])
    modern.pop("namespace")
    assert bench.run(modern)["ok"]
    assert len(bench.inventory("legacy")["records"]) == 1


def test_restart_preserves_spaces_records_and_scoped_recall(tmp_path):
    path = str(tmp_path / "vectors")
    with MemoryEngine(config={"extraction_policy": "none"}, qdrant_path=path) as engine:
        first = Workbench(engine)
        create(first, "A")
        create(first, "empty")
        result = send(first, "A", "claim", claims=[claim("durable")], confirmed=True)
        assert result["ok"]
    with MemoryEngine(config={"extraction_policy": "none"}, qdrant_path=path) as engine:
        second = Workbench(engine)
        assert {s["memory_space_id"] for s in second.list_spaces()} == {"A", "empty"}
        assert (
            send(second, "A", "recall", predicate="probe_field")["recall"]["evidence"][
                0
            ]["value"]
            == "durable"
        )
        assert second.inventory("empty")["records"] == []


def test_concurrent_requests_keep_distinct_spaces(bench):
    for space in ("A", "B"):
        create(bench, space)

    def write(index):
        space = "A" if index % 2 else "B"
        return send(bench, space, "store", prompt=f"{space} private marker {index}")

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(write, range(8)))
    assert all(r["ok"] for r in results)
    for space in ("A", "B"):
        records = bench.inventory(space)["records"]
        assert len(records) == 4
        assert all(r["content"].startswith(space + " private") for r in records)
        assert set(
            send(bench, space, top_k=10)["diagnostics"]["retrieved_memory_ids"]
        ) == {r["memory_id"] for r in records}


def test_hosted_context_never_includes_other_space(bench):
    for space, value in (("A", "apple_private_marker"), ("B", "berry_private_marker")):
        create(bench, space)
        stored = send(bench, space, "claim", claims=[claim(value)], confirmed=True)
        assert stored["ok"]
        if space == "A":
            mid = stored["stored"]["memory_id"]
    client = Client(
        '{"predicates":["probe_field"]}',
        json.dumps(
            dict(
                answer="apple_private_marker",
                citations=[mid],
                evidence_status="supported",
            )
        ),
    )
    bench.hosted_clients = {"test": client}
    result = send(bench, "A", model="test")
    assert result["ok"] and result["assistant"]["citations"] == [mid]
    assert "berry_private_marker" not in json.dumps(client.calls)
    assert "apple_private_marker" in json.dumps(client.calls)


def test_http_inventory_requires_exact_space_and_create_requires_token(bench):
    for space in ("A", "B"):
        create(bench, space)
        assert send(bench, space, "store", prompt=space + " private marker")["ok"]
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(bench, "test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        conn = HTTPConnection("127.0.0.1", server.server_port)
        for query in (
            "",
            "?memory_space_id=",
            "?memory_space_id=unknown",
            "?memory_space_id=A&memory_space_id=B",
            "?memory_space_id=A&all=true",
        ):
            conn.request("GET", "/api/memories" + query)
            response = conn.getresponse()
            assert response.status == 400
            assert "private marker" not in response.read().decode()
        conn.request("GET", "/api/memories?memory_space_id=A")
        response = conn.getresponse()
        body = json.loads(response.read())
        assert response.status == 200 and len(body["records"]) == 1
        assert "B private marker" not in json.dumps(body)
        conn.request(
            "POST",
            "/api/spaces",
            body='{"name":"test"}',
            headers={"Content-Type": "application/json"},
        )
        response = conn.getresponse()
        assert response.status == 403
        response.read()
        conn.request(
            "POST",
            "/api/spaces",
            body='{"name":"test"}',
            headers={
                "Content-Type": "application/json",
                "X-Workbench-Token": "test-token",
            },
        )
        response = conn.getresponse()
        assert response.status == 201
        assert (
            bench.inventory(json.loads(response.read())["memory_space_id"])["records"]
            == []
        )
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
