import json

import pytest

from memory.engine import MemoryEngine
from memory.shared.hosted import route_fields, HostedOutputError
from memory.workbench import Workbench
from tests.test_hosted_boundaries import Client, body


def test_field_router_rejects_invented_fields():
    raw = json.dumps({"predicates": ["invented"]})
    with pytest.raises(HostedOutputError):
        route_fields(
            Client(raw, raw),
            "test",
            "question",
            [{"predicate": "actual", "kind": "fact", "examples": []}],
        )


def test_unrelated_dispute_does_not_taint_current_field_answer(tmp_path):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "v")
    ) as engine:
        bench = Workbench(engine)
        for predicate, value in [
            ("workspace", "North"),
            ("workspace", "South"),
            ("review", "2026-11-22"),
        ]:
            result = bench.run(
                body(
                    mode="claim",
                    claims=[
                        dict(
                            subject="manual-user",
                            scope={},
                            predicate=predicate,
                            value=value,
                            kind="fact",
                        )
                    ],
                )
            )
            assert result["ok"]
            if predicate == "review":
                mid = result["stored"]["memory_id"]
        client = Client(
            json.dumps({"predicates": ["review"]}),
            json.dumps(
                dict(answer="2026-11-22", citations=[mid], evidence_status="supported")
            ),
        )
        bench.hosted_clients = {"test": client}
        result = bench.run(body(mode="retrieve", model="test"))
        assert result["ok"]
        assert result["assistant"]["evidence_status"] == "supported"
        assert result["diagnostics"]["generation_memory_ids"] == [mid]
        assert result["field_recall"][0]["requested_predicate"] == "review"
        assert result[
            "retrieved"
        ]  # Original semantic results remain visible separately.
