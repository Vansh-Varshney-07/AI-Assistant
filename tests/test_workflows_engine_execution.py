"""Unit tests for Workflows state machine and execution coordination (P09.03 - P09.07)."""
import sqlite3
import time
from unittest.mock import MagicMock
import pytest
from wayfinder.platform.contracts import Scope
from wayfinder.platform.workflows import Workflows, Definition, Node, Request

class MockDB:
    def __init__(self, conn):
        self.conn = conn
    def __enter__(self):
        return self.conn
    def __exit__(self, *args):
        self.conn.commit()

class MockApp:
    def __init__(self, conn):
        self.conn = conn
        self.workers = MagicMock()
        self.workers.stops = []
        self.workers.subscribe_completion.return_value = lambda: None
        self.workers.files.read.return_value = {"name": "sample.txt", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
        self.workers.start.return_value = {"id": "job-001"}
        self.workers.get.return_value = {
            "id": "job-001",
            "status": "completed",
            "result": {
                "text": "Analysis complete.",
                "evidence": {"name": "sample.txt", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "truncated": False},
                "truncated": False,
            },
        }

    def db(self):
        return MockDB(self.conn)

class MockPlatform:
    def __init__(self, conn):
        self.app = MockApp(conn)
        self.clock = time.time
        self.closed = False
        self.inspector = MagicMock()
        self.inspector.require.return_value = {"fingerprint": "test-fp-1"}

@pytest.fixture
def workflow_svc():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    platform = MockPlatform(conn)
    svc = Workflows(platform)
    yield svc
    svc.close()
    conn.close()

def test_workflow_start_and_advance(workflow_svc):
    scope = Scope(owner="owner1", space="space1", task="task1")
    req = Request(
        request_id="req-1",
        definition=Definition(
            title="Step review",
            nodes=(
                Node(id="step1", role="W35", reference="ref1", question="Read doc."),
            ),
            concurrency=1,
            deadline_seconds=30,
        ),
    )
    result = workflow_svc.start(scope, req)
    assert result["status"] == "running"
    assert result["definition"]["title"] == "Step review"
    assert len(result["nodes"]) == 1

def test_workflow_idempotent_duplicate_request(workflow_svc):
    scope = Scope(owner="owner1", space="space1", task="task1")
    req = Request(
        request_id="req-2",
        definition=Definition(
            title="Idempotent review",
            nodes=(
                Node(id="step1", role="W35", reference="ref1", question="Read doc."),
            ),
            concurrency=1,
            deadline_seconds=30,
        ),
    )
    res1 = workflow_svc.start(scope, req)
    res2 = workflow_svc.start(scope, req)
    assert res1["id"] == res2["id"]
    assert res1["digest"] == res2["digest"]

def test_workflow_changed_definition_rejected(workflow_svc):
    scope = Scope(owner="owner1", space="space1", task="task1")
    req1 = Request(
        request_id="req-3",
        definition=Definition(
            title="Original",
            nodes=(Node(id="step1", role="W35", reference="ref1", question="Read doc."),),
        ),
    )
    req2 = Request(
        request_id="req-3",
        definition=Definition(
            title="Changed Title",
            nodes=(Node(id="step1", role="W35", reference="ref1", question="Read doc."),),
        ),
    )
    workflow_svc.start(scope, req1)
    with pytest.raises(ValueError, match="immutable input"):
        workflow_svc.start(scope, req2)

def test_workflow_cancel_marks_cancelled(workflow_svc):
    scope = Scope(owner="owner1", space="space1", task="task1")
    req = Request(
        request_id="req-4",
        definition=Definition(
            title="Cancel test",
            nodes=(Node(id="step1", role="W35", reference="ref1", question="Read doc."),),
        ),
    )
    row = workflow_svc.start(scope, req)
    canceled = workflow_svc.call(None, scope, "platform_workflow_cancel", {"id": row["id"]})
    assert canceled["status"] == "cancelled"

def test_workflow_runs_lists_recent(workflow_svc):
    scope = Scope(owner="owner1", space="space1", task="task1")
    req = Request(
        request_id="req-5",
        definition=Definition(
            title="Listing test",
            nodes=(Node(id="step1", role="W35", reference="ref1", question="Read doc."),),
        ),
    )
    workflow_svc.start(scope, req)
    runs = workflow_svc.call(None, scope, "platform_workflow_runs", {})
    assert len(runs) >= 1
    assert any(r["definition"]["title"] == "Listing test" for r in runs)
