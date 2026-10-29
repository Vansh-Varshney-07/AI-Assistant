"""Unit tests for workflow DAG validation and models (P09.01, P09.02)."""
import pytest
from wayfinder.platform.workflows import Node, Definition, Request
from wayfinder.platform.worker_bindings import SOURCE_ROLES

def test_node_validation_valid():
    node = Node(
        id="step1",
        role="W35",
        reference="ref-123",
        question="Summarize the key conclusions.",
        dependencies=(),
    )
    assert node.id == "step1"
    assert node.role == "W35"

def test_node_validation_rejects_unqualified_role():
    with pytest.raises(ValueError, match="No qualified workflow operation"):
        Node(
            id="step1",
            role="UNQUALIFIED_ROLE",
            reference="ref-123",
            question="Summarize.",
            dependencies=(),
        )

def test_node_validation_rejects_blank_question():
    with pytest.raises(ValueError, match="No qualified workflow operation"):
        Node(
            id="step1",
            role="W35",
            reference="ref-123",
            question="   ",
            dependencies=(),
        )

def test_node_validation_rejects_duplicate_dependencies():
    with pytest.raises(ValueError, match="Duplicate dependency"):
        Node(
            id="step2",
            role="W35",
            reference="ref-123",
            question="Compare.",
            dependencies=("step1", "step1"),
        )

def test_definition_valid_single_step():
    d = Definition(
        title="Single step review",
        nodes=(
            Node(id="step1", role="W35", reference="r1", question="Read doc."),
        ),
        concurrency=1,
        deadline_seconds=30,
    )
    assert d.title == "Single step review"
    assert len(d.nodes) == 1

def test_definition_valid_dag_chain():
    d = Definition(
        title="Chain review",
        nodes=(
            Node(id="step1", role="W35", reference="r1", question="Read doc."),
            Node(id="step2", role="W03", reference="r1", question="Plan.", dependencies=("step1",)),
            Node(id="step3", role="W06", reference="r1", question="Validate.", dependencies=("step2",)),
            Node(id="step4", role="W07", reference="r1", question="Synthesize.", dependencies=("step3",)),
        ),
        concurrency=2,
        deadline_seconds=60,
    )
    assert len(d.nodes) == 4

def test_definition_rejects_cycle():
    with pytest.raises(ValueError, match="Cycle"):
        Definition(
            title="Cycle workflow",
            nodes=(
                Node(id="step1", role="W35", reference="r1", question="Step 1", dependencies=("step2",)),
                Node(id="step2", role="W35", reference="r1", question="Step 2", dependencies=("step1",)),
            ),
            concurrency=1,
            deadline_seconds=30,
        )

def test_definition_rejects_self_dependency():
    with pytest.raises(ValueError, match="Cycle"):
        Definition(
            title="Self loop",
            nodes=(
                Node(id="step1", role="W35", reference="r1", question="Step 1", dependencies=("step1",)),
            ),
            concurrency=1,
            deadline_seconds=30,
        )

def test_definition_rejects_missing_dependency():
    with pytest.raises(ValueError, match="Cycle"):
        Definition(
            title="Missing dep",
            nodes=(
                Node(id="step1", role="W35", reference="r1", question="Step 1", dependencies=("nonexistent",)),
            ),
            concurrency=1,
            deadline_seconds=30,
        )

def test_definition_rejects_blank_title():
    with pytest.raises(ValueError, match="nonblank title"):
        Definition(
            title="   ",
            nodes=(
                Node(id="step1", role="W35", reference="r1", question="Step 1"),
            ),
            concurrency=1,
            deadline_seconds=30,
        )

def test_definition_rejects_duplicate_node_ids():
    with pytest.raises(ValueError, match="Unique nodes"):
        Definition(
            title="Duplicate IDs",
            nodes=(
                Node(id="step1", role="W35", reference="r1", question="First"),
                Node(id="step1", role="W35", reference="r1", question="Second"),
            ),
            concurrency=1,
            deadline_seconds=30,
        )

def test_definition_concurrency_bounds():
    with pytest.raises(ValueError):
        Definition(
            title="Over concurrency",
            nodes=(Node(id="step1", role="W35", reference="r1", question="First"),),
            concurrency=3,
        )
    with pytest.raises(ValueError):
        Definition(
            title="Zero concurrency",
            nodes=(Node(id="step1", role="W35", reference="r1", question="First"),),
            concurrency=0,
        )

def test_definition_deadline_bounds():
    with pytest.raises(ValueError):
        Definition(
            title="Too short deadline",
            nodes=(Node(id="step1", role="W35", reference="r1", question="First"),),
            deadline_seconds=4,
        )
    with pytest.raises(ValueError):
        Definition(
            title="Too long deadline",
            nodes=(Node(id="step1", role="W35", reference="r1", question="First"),),
            deadline_seconds=111,
        )

def test_request_contract():
    req = Request(
        request_id="req-001",
        definition=Definition(
            title="Test run",
            nodes=(Node(id="step1", role="W35", reference="r1", question="Read"),),
        ),
    )
    assert req.request_id == "req-001"
    assert req.definition.title == "Test run"
