"""Synthetic contract/API checks with real disposable Iron Web storage; no UI."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
from threading import Event
import time

import pytest

from wayfinder.api import Client, serve
from wayfinder.atlas.indexing.retrieval import CapabilityCandidate
from wayfinder.platform.contracts import Scope
from wayfinder.platform.runtime import RuntimeInspector
from wayfinder.platform.service import PlatformService
from wayfinder.runtime import open_service
from wayfinder.service import Identity
from tests.test_wayfinder_app import factory


class FixtureWorker:
    """Explicit mock tier: never presented as installed-Hermes proof."""

    def __init__(self):
        self.payloads = []
        self.entered, self.release = Event(), Event()
        self.release.set()
        self.result = dict(
            ok=True,
            runtime="Hermes",
            effective_tools=[],
            text="The document says 42 days and supplied memory says 30 days; confirmation is needed.",
        )

    def run(self, payload, cancelled):
        self.payloads.append(payload)
        self.entered.set()
        while not self.release.wait(0.01):
            if cancelled.is_set():
                raise RuntimeError("cancelled")
        return dict(self.result)


@pytest.fixture
def platform(tmp_path):
    app = open_service(tmp_path / "runtime", factory)
    server = serve(app)
    client = Client(server.server_port, app.token)
    sid = client.call("create_space", name="Platform synthetic fixture")["id"]
    args = dict(space=sid, task="integration-test")
    worker = FixtureWorker()
    app.workers.bridge = worker
    app.platform.inspector.snapshot = dict(
        compatible=True,
        fingerprint="fixture-runtime",
        observed=time.time(),
        expires=time.time() + 300,
        runtime=dict(version="mock-tier"),
    )
    path = tmp_path / "selected.md"
    path.write_text(
        "Fictional release note. Retention: 42 days. No external actions.",
        encoding="utf-8",
    )
    grant = client.call("worker_grant", **args, path=str(path))
    ref = client.call("worker_search", **args, grant=grant["id"])["files"][0]["id"]
    request = dict(
        request_id="read-once",
        question="Compare the selected release note with the supplied retention memory.",
        reference=ref,
        context=dict(subject="me", predicate="retention_days"),
    )
    fixture = dict(
        app=app,
        client=client,
        args=args,
        worker=worker,
        request=request,
        path=path,
        grant=grant,
    )
    seed(fixture, 30)
    yield fixture
    worker.release.set()
    server.shutdown()
    server.server_close()
    app.close()


def seed(fixture, value):
    client, args = fixture["client"], fixture["args"]
    proposal = client.call(
        "propose",
        space=args["space"],
        request="fixture-" + str(value),
        body=dict(
            text=f"Synthetic retention is {value} days.",
            subject="me",
            predicate="retention_days",
            value=value,
            task_id=args["task"],
        ),
    )
    return client.call(
        "decide", space=args["space"], proposal=proposal["id"], approve=True
    )


def start(fixture, **changes):
    return fixture["client"].call(
        "platform_read_start",
        **fixture["args"],
        request=dict(fixture["request"], **changes),
    )


def finished(fixture, item):
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        item = fixture["client"].call(
            "platform_read_result", **fixture["args"], id=item["id"]
        )
        if item["status"] != "worker_running":
            return item
        time.sleep(0.02)
    raise AssertionError("Workflow did not settle")


def test_persisted_artifact_evaluation_and_scoped_metrics(platform):
    client, args = platform["client"], platform["args"]
    item = finished(platform, start(platform))
    request = dict(
        request_id="rubric",
        required_phrases=["42 days", "30 days"],
        expected_file_sha256=hashlib.sha256(platform["path"].read_bytes()).hexdigest(),
    )
    result = client.call(
        "platform_workflow_evaluate", **args, id=item["id"], request=request
    )
    assert result["passed"] and result["semantic_accuracy"] is None
    assert result["fresh_for_action"] is False
    assert (
        client.call(
            "platform_workflow_evaluate", **args, id=item["id"], request=request
        )
        == result
    )
    with pytest.raises(ValueError):
        client.call(
            "platform_workflow_evaluate",
            **args,
            id=item["id"],
            request=dict(request, required_phrases=["99 days"]),
        )
    failed = client.call(
        "platform_workflow_evaluate",
        **args,
        id=item["id"],
        request=dict(request_id="mismatch", required_phrases=["99 days"]),
    )
    assert failed["passed"] is False
    metrics = client.call("platform_workflow_metrics", **args)
    assert (
        metrics["status_counts"] == {"completed": 1}
        and metrics["worker_dispatches"] == 1
    )
    assert metrics["cost"] is None and metrics["median_elapsed_seconds"] >= 0
    assert (
        client.call("platform_workflow_metrics", **dict(args, task="other"))["sampled"]
        == 0
    )
    with pytest.raises(ValueError):
        client.call(
            "platform_workflow_evaluate",
            **dict(args, task="other"),
            id=item["id"],
            request=request,
        )
    with pytest.raises(ValueError):
        client.call("platform_workflow_metrics", **args, limit=True)


def test_explicit_read_retry_refreshes_context_and_has_one_retry_budget(platform):
    client, args, worker = platform["client"], platform["args"], platform["worker"]
    worker.result["ok"] = False
    original = finished(platform, start(platform))
    assert original["status"] in {"failed", "stale"}
    worker.result["ok"] = True
    retry = dict(
        id=original["id"],
        request_id="retry-once",
        reference=platform["request"]["reference"],
    )
    child = client.call("platform_read_retry", **args, **retry)
    completed = finished(platform, child)
    assert completed["status"] == "completed" and len(worker.payloads) == 2
    assert client.call("platform_read_retry", **args, **retry)["id"] == child["id"]
    with pytest.raises(ValueError):
        client.call("platform_read_retry", **args, **dict(retry, request_id="another"))
    # Simulate an eligible terminal result on the child; its retry budget remains zero.
    with platform["app"].db() as db:
        db.execute(
            "UPDATE platform_workflows SET status='failed' WHERE id=?", (child["id"],)
        )
    with pytest.raises(ValueError, match="budget"):
        client.call("platform_read_retry", **args, **dict(retry, id=child["id"]))


def test_retry_requires_current_grant_and_rejects_successful_or_cancelled_work(
    platform,
):
    client, args = platform["client"], platform["args"]
    item = finished(platform, start(platform))
    with pytest.raises(ValueError):
        client.call(
            "platform_read_retry",
            **args,
            id=item["id"],
            request_id="invalid",
            reference=platform["request"]["reference"],
        )
    platform["worker"].result["ok"] = False
    failed = finished(platform, start(platform, request_id="failed"))
    platform["app"].workers.files.revoke(
        (platform["app"].owner, args["space"], args["task"]), platform["grant"]["id"]
    )
    child = client.call(
        "platform_read_retry",
        **args,
        id=failed["id"],
        request_id="fresh-check",
        reference=platform["request"]["reference"],
    )
    assert child["status"] == "blocked"
    assert len(platform["worker"].payloads) == 2


def test_clear_removes_platform_artifacts_but_retains_deduplication(platform):
    client, args, app = platform["client"], platform["args"], platform["app"]
    item = finished(platform, start(platform))
    client.call(
        "platform_workflow_evaluate",
        **args,
        id=item["id"],
        request=dict(request_id="clear-me"),
    )
    cleared = client.call("platform_read_clear", **args, id=item["id"])
    assert cleared["status"] == "cleared" and cleared["result"] is None
    assert (
        start(platform)["status"] == "cleared" and len(platform["worker"].payloads) == 1
    )
    with app.db() as db:
        row = db.execute(
            "SELECT body,context,result FROM platform_workflows WHERE id=?",
            (item["id"],),
        ).fetchone()
        assert row["body"] == "{}" and row["context"] is None and row["result"] is None
        assert (
            db.execute(
                "SELECT count(*) FROM platform_evaluations WHERE workflow=?",
                (item["id"],),
            ).fetchone()[0]
            == 0
        )
    from wayfinder.platform.service import PlatformService

    app.platform.close()
    app.platform = PlatformService(app)
    assert (
        client.call("platform_read_result", **args, id=item["id"])["status"]
        == "cleared"
    )


def test_authenticated_read_workflow_uses_existing_memory_and_worker(platform):
    result = finished(platform, start(platform))
    assert result["status"] == "completed", result
    body = result["result"]
    assert body["evidence"]["memory"]["evidence"][0]["value"] == 30
    assert (
        body["evidence"]["file"]["sha256"]
        == hashlib.sha256(platform["path"].read_bytes()).hexdigest()
    )
    assert body["executed"] is False
    assert body["metrics"]["worker_invocations"] == 1
    assert body["metrics"]["cost"] is None
    assert "30" in platform["worker"].payloads[0]["question"]
    assert "proof" not in platform["worker"].payloads[0]["question"]
    assert platform["app"].owner not in platform["worker"].payloads[0]["question"]
    assert platform["args"]["space"] not in platform["worker"].payloads[0]["question"]
    audit = platform["client"].call(
        "platform_audit", **platform["args"], id=result["id"]
    )
    assert [row["status"] for row in audit] == [
        "planned",
        "context",
        "worker_running",
        "validated",
        "completed",
    ]


def test_duplicate_requests_are_immutable_and_concurrent_submission_runs_once(platform):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: start(platform), range(2)))
    assert results[0]["id"] == results[1]["id"]
    assert finished(platform, results[0])["status"] == "completed"
    assert len(platform["worker"].payloads) == 1
    with pytest.raises(ValueError, match="immutable"):
        start(platform, question="Changed payload")


def test_worker_identity_and_cross_task_context_access_are_denied(platform):
    app, client, args = platform["app"], platform["client"], platform["args"]
    app.credentials["worker-test-token"] = Identity(app.owner, "worker")
    restricted = Client(client.base.split(":")[2].split("/")[0], "worker-test-token")
    with pytest.raises(ValueError, match="orchestrator"):
        restricted.call(
            "platform_context", **args, query=platform["request"]["context"]
        )
    packet = client.call(
        "platform_context", **args, query=platform["request"]["context"]
    )
    with pytest.raises(ValueError, match="another task"):
        client.call(
            "platform_validate_context",
            **dict(args, task="foreign-task"),
            context_ref=packet["context_ref"],
        )
    item = start(platform)
    with pytest.raises(ValueError, match="unavailable"):
        client.call(
            "platform_read_result", **dict(args, task="foreign-task"), id=item["id"]
        )


@pytest.mark.parametrize("cause", ["memory", "file", "runtime", "revocation"])
def test_changed_evidence_withholds_the_pending_response(platform, cause):
    platform["worker"].release.clear()
    item = start(platform)
    assert platform["worker"].entered.wait(2)
    if cause == "memory":
        seed(platform, 31)
    elif cause == "file":
        platform["path"].write_text("Changed file after dispatch", encoding="utf-8")
    elif cause == "runtime":
        platform["app"].platform.inspector.snapshot["fingerprint"] = "changed-runtime"
    else:
        platform["client"].call(
            "worker_revoke", **platform["args"], grant=platform["grant"]["id"]
        )
    platform["worker"].release.set()
    result = finished(platform, item)
    assert result["status"] in {"stale", "failed"}
    assert "synthesis" not in (result["result"] or {})


def test_cancel_and_deadline_stop_existing_worker_without_replay(platform):
    platform["worker"].release.clear()
    item = start(platform)
    stopped = platform["client"].call(
        "platform_read_cancel", **platform["args"], id=item["id"]
    )
    assert stopped["status"] == "cancelled"
    assert start(platform)["id"] == item["id"]
    platform["worker"].release.set()
    until = time.monotonic() + 3
    while platform["app"].workers.stops and time.monotonic() < until:
        time.sleep(0.01)
    platform["worker"].release.clear()
    now = [time.time()]
    platform["app"].platform.clock = lambda: now[0]
    item = start(platform, request_id="deadline", deadline_seconds=5)
    now[0] += 6
    assert finished(platform, item)["status"] == "timed_out"
    assert len(platform["worker"].payloads) <= 2


def test_deadline_cancels_even_without_result_polling(platform):
    platform["worker"].release.clear()
    item = start(platform, deadline_seconds=5)
    until = time.monotonic() + 7
    while time.monotonic() < until:
        with platform["app"].db() as db:
            status = db.execute(
                "SELECT status FROM platform_workflows WHERE id=?", (item["id"],)
            ).fetchone()[0]
        if status == "timed_out":
            break
        time.sleep(0.05)
    assert status == "timed_out"


def test_restart_interrupts_and_never_redispatches(platform):
    platform["worker"].release.clear()
    item = start(platform)
    platform["app"].platform.close()
    platform["app"].platform = PlatformService(platform["app"])
    result = platform["client"].call(
        "platform_read_result", **platform["args"], id=item["id"]
    )
    assert result["status"] == "interrupted"
    assert start(platform)["id"] == item["id"]
    assert len(platform["worker"].payloads) <= 1


def test_uninspected_runtime_and_verified_metadata_do_not_authorize_dispatch(platform):
    platform["app"].platform.inspector.snapshot = None
    assert start(platform)["status"] == "blocked"
    assert platform["worker"].payloads == []
    platform["app"].platform.inspector.snapshot = dict(
        compatible=True, fingerprint="fixture", expires=time.time() + 300
    )
    platform["app"].platform.catalog.searcher = lambda *args, **kwargs: [
        CapabilityCandidate(
            id="system.terminal_exec", status="verified", name="Execute shell"
        )
    ]
    assert start(platform, request_id="forged-candidate")["status"] == "blocked"
    assert platform["worker"].payloads == []


@pytest.mark.parametrize(
    "changes",
    [dict(runtime="Other"), dict(effective_tools=["terminal"]), dict(text="")],
)
def test_invalid_worker_output_never_completes(platform, changes):
    platform["worker"].result.update(changes)
    assert finished(platform, start(platform))["status"] == "stale"


def test_scoped_memory_conflicts_remain_explicit(platform):
    seed(platform, 31)
    result = finished(platform, start(platform))
    assert result["status"] == "completed"
    memory = result["result"]["evidence"]["memory"]
    assert memory["status"] == "disputed"
    assert {row["value"] for row in memory["evidence"]} == {30, 31}
    assert result["result"]["warnings"]


def test_context_expiry_is_task_bound(platform):
    p = platform["app"].platform
    scope = Scope(owner=platform["app"].owner, **platform["args"])
    packet = platform["client"].call(
        "platform_context", **platform["args"], query=platform["request"]["context"]
    )
    p.context.clock = lambda: packet["expires"] + 1
    with pytest.raises(ValueError, match="expired"):
        p.context.validate(Identity(scope.owner), scope, packet["context_ref"])


def test_capability_discovery_never_returns_authority(platform):
    result = platform["client"].call(
        "platform_capabilities",
        **platform["args"],
        query="local file document analysis",
    )
    assert any(
        row["availability"] == "runtime_qualified" for row in result["candidates"]
    )
    assert all(row["executable"] is False for row in result["candidates"])


def test_inspector_failure_clears_qualification(monkeypatch):
    inspector = RuntimeInspector()
    inspector.snapshot = dict(
        compatible=True, fingerprint="old", expires=time.time() + 300
    )
    monkeypatch.setattr(
        "wayfinder.platform.runtime.subprocess.run",
        lambda *a, **k: type("Run", (), dict(returncode=1, stdout=""))(),
    )
    with pytest.raises(ValueError, match="inspection failed"):
        inspector.inspect()
    assert inspector.current()["compatible"] is False


@pytest.mark.skipif(
    os.environ.get("WAYFINDER_PLATFORM_LIVE") != "1",
    reason="Explicit live-Hermes opt-in required",
)
def test_live_installed_hermes_read_workflow(platform):
    from wayfinder.workers.hermes import HermesBridge

    platform["app"].workers.bridge = HermesBridge()
    inspected = platform["client"].call("platform_inspect", **platform["args"])
    assert inspected["compatible"] is True
    assert inspected["isolation"]["effective_tools"] == []
    item = start(platform, request_id="live-installed-hermes")
    deadline = time.monotonic() + 115
    while item["status"] == "worker_running" and time.monotonic() < deadline:
        time.sleep(0.25)
        item = platform["client"].call(
            "platform_read_result", **platform["args"], id=item["id"]
        )
    answer = (item.get("result") or {}).get("synthesis", "").lower()
    passed = (
        item["status"] == "completed"
        and "30" in answer
        and "42" in answer
        and any(w in answer for w in ("conflict", "differ", "discrep", "mismatch"))
    )
    report = dict(
        tier="live_provider_with_synthetic_data",
        hermes="installed managed runtime",
        memory="real disposable FalkorDB and embedded Qdrant; fixture embeddings",
        native_ui=False,
        private_data=False,
        passed=passed,
        inspection=inspected,
        workflow=item,
    )
    path = (
        Path(__file__).resolve().parents[1] / ".local/verification/platform-live.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert passed, item
