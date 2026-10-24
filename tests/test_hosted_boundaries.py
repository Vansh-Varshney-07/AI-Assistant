"""Provider-independent boundary regressions; no network and no synthetic production records."""

import json
from types import SimpleNamespace
import uuid

import pytest

from memory.engine import MemoryEngine
from memory.shared.hosted import (
    HostedEvidenceAnswerer,
    HostedOutputError,
    parse_object,
    field_catalog,
)
from memory.shared.interpreter import HostedClaimInterpreter
from memory.workbench import Workbench
from workbench_server import wire_value


class Client:
    def __init__(self, *outputs):
        self.outputs = list(outputs)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        value = self.outputs.pop(0)
        if isinstance(value, Exception):
            raise value
        content, finish = value if isinstance(value, tuple) else (value, "stop")
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content), finish_reason=finish
                )
            ]
        )


def claim(value="A", predicate="label", evidence_quote="source", **extra):
    return dict(
        subject="manual-user",
        scope={"test_namespace": "boundary"},
        predicate=predicate,
        value=value,
        kind="fact",
        evidence_quote=evidence_quote,
        **extra,
    )


def body(mode="store", **kwargs):
    return dict(
        prompt="source",
        mode=mode,
        namespace="boundary",
        session_id=uuid.uuid4().hex,
        request_id=uuid.uuid4().hex,
        confirmed=True,
        **kwargs,
    )


def test_parser_rejects_embedded_examples_and_duplicate_nonfinite_objects():
    assert parse_object('```json\n{"claims":[]}\n```') == {"claims": []}
    for text in [
        'Here is code: {"claims":[]}',
        '{"a":1,"a":2}',
        '{"a":NaN}',
        "[]",
        "",
        "null",
    ]:
        with pytest.raises(ValueError):
            parse_object(text)


def test_nemotron_json_mode_bounded_repair_and_truncation():
    client = Client(("{}", "length"), json.dumps({"claims": [claim()]}))
    claims, trace = HostedClaimInterpreter(
        client, "nvidia/nemotron-3-ultra-550b-a55b"
    ).interpret(
        "source",
        dict(subject="manual-user", scope={"test_namespace": "boundary"}),
    )
    assert claims[0]["value"] == "A" and len(trace["attempts"]) == 2
    assert client.calls[0]["response_format"]["type"] == "json_schema"
    assert (
        client.calls[0]["extra_body"]["chat_template_kwargs"]["enable_thinking"]
        is False
    )
    bad = Client('Some code {"claims":[]}', "Still not JSON")
    with pytest.raises(HostedOutputError):
        HostedClaimInterpreter(bad, "test-model")(
            "text", dict(subject="manual-user", scope={})
        )
    assert len(bad.calls) == 2


@pytest.mark.parametrize(
    "mutation",
    [
        {"subject": "another-user"},
        {"scope": {}},
        {"protected": True},
        {"action": "alias"},
        {"targets": ["invented"]},
        {"references": ["other"]},
        {"aliases": ["override"]},
    ],
)
def test_model_cannot_broaden_source_authority_or_scope(mutation):
    raw = json.dumps({"claims": [dict(claim(), **mutation)]})
    with pytest.raises(HostedOutputError):
        HostedClaimInterpreter(Client(raw, raw), "test")(
            "source", dict(subject="manual-user", scope={"test_namespace": "boundary"})
        )


def test_unknown_change_field_is_rejected_instead_of_orphaning_a_correction():
    bad = json.dumps(
        {
            "claims": [
                claim(predicate="new_name", action="correct", reason="User correction")
            ]
        }
    )
    good = json.dumps(
        {
            "claims": [
                claim(predicate="label", action="correct", reason="User correction")
            ]
        }
    )
    client = Client(bad, good)
    claims = HostedClaimInterpreter(client, "test")(
        "source",
        dict(
            subject="manual-user",
            scope={"test_namespace": "boundary"},
            field_catalog=[{"predicate": "label", "kind": "fact", "examples": ["old"]}],
        ),
    )
    assert claims[0]["predicate"] == "label" and len(client.calls) == 2
    assert "field_catalog" in client.calls[0]["messages"][0]["content"]


def test_answer_validates_memory_ids_and_preserves_dispute_status():
    packet = dict(
        recall=dict(
            answer_status="disputed",
            evidence=[
                dict(memory_id="wb_a", value="North"),
                dict(memory_id="wb_b", value="South"),
            ],
        )
    )
    client = Client(
        json.dumps(
            dict(answer="North", citations=["claim_a"], evidence_status="supported")
        ),
        json.dumps(
            dict(
                answer="The values conflict.",
                citations=["wb_a", "wb_b"],
                evidence_status="disputed",
            )
        ),
    )
    answer, trace = HostedEvidenceAnswerer(client, "test").answer(
        "Current workspace?", packet
    )
    assert (
        answer["citations"] == ["wb_a", "wb_b"]
        and answer["evidence_status"] == "disputed"
    )
    assert len(trace["attempts"]) == 2


def test_missing_evidence_cannot_gain_fabricated_citations():
    bad = json.dumps(
        dict(answer="A", citations=["invented"], evidence_status="missing")
    )
    with pytest.raises(HostedOutputError):
        HostedEvidenceAnswerer(Client(bad, bad), "test").answer(
            "Question?", dict(retrieved=[])
        )


def test_wire_format_preserves_int64_without_changing_engine_values():
    original = {"valid_until": 2**63 - 1, "count": 2, "flags": [True, None]}
    wire = wire_value(original)
    assert (
        wire["valid_until"] == "9223372036854775807"
        and original["valid_until"] == 2**63 - 1
    )
    assert wire["count"] == 2 and wire["flags"] == [True, None]


def test_failed_extraction_leaves_both_real_test_stores_unchanged(tmp_path):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "v")
    ) as engine:
        client = Client("Not JSON", "Still not JSON")
        bench = Workbench(engine, {"test": client})
        result = bench.run(body(model="test"))
        assert not result["ok"] and not result["diagnostics"]["pipeline_invoked"]
        assert engine.storage_status()["memories"] == 0
        assert engine.graph_store.get_node_counts()["Observation"] == 0


def test_hosted_correction_uses_real_catalog_targets_and_retains_evidence(tmp_path):
    old = json.dumps({"claims": [claim("Alpha")]})
    new = json.dumps(
        {"claims": [claim("Beta", action="correct", reason="Explicit correction")]}
    )
    answer = json.dumps(dict(answer="Beta", citations=[], evidence_status="supported"))
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "v")
    ) as engine:
        client = Client(old, new)
        bench = Workbench(engine, {"test": client})
        a = bench.run(body(model="test"))
        b = bench.run(body(model="test"))
        assert a["ok"] and b["ok"]
        original = bench.inspection.detail(a["stored"]["memory_id"])
        assert original["claims"][0]["status"] == "corrected"
        assert (
            original["claims"][0]["changed_by"] == b["stored"]["claims"][0]["claim_id"]
        )
        assert field_catalog(engine, "manual-user", {"test_namespace": "other"}) == []
        assert (
            field_catalog(engine, "manual-user", {"test_namespace": "boundary"})[0][
                "predicate"
            ]
            == "label"
        )
        client.outputs.extend(
            [
                answer,
                json.dumps(
                    dict(
                        answer="Beta",
                        citations=[b["stored"]["memory_id"]],
                        evidence_status="supported",
                    )
                ),
            ]
        )
        result = bench.run(body(mode="recall", predicate="label", model="test"))
        assert result["ok"] and result["assistant"]["citations"] == [
            b["stored"]["memory_id"]
        ]


def test_hosted_api_failure_is_sanitized(tmp_path):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "v")
    ) as engine:
        bench = Workbench(
            engine, {"test": Client(RuntimeError("API_SECRET_DO_NOT_EXPOSE"))}
        )
        result = bench.run(body(model="test"))
        assert not result["ok"] and "API_SECRET_DO_NOT_EXPOSE" not in json.dumps(result)


def test_hosted_write_retry_reuses_durable_extraction_without_another_api_call(
    tmp_path,
):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "v")
    ) as engine:
        client = Client(json.dumps({"claims": [claim("Alpha")]}))
        bench = Workbench(engine, {"test": client})
        original = body(model="test")
        first = bench.run(original)
        second = bench.run(original)
        assert first["ok"] and second["ok"]
        assert len(client.calls) == 1 and engine.storage_status()["memories"] == 1
        assert second["diagnostics"]["hosted"]["extraction"]["replayed"]
        changed = bench.run(dict(original, prompt="Changed input"))
        assert not changed["ok"] and len(client.calls) == 1


def test_context_metadata_cannot_be_extracted_as_a_source_fact():
    raw = json.dumps(
        {
            "claims": [
                claim(
                    value="boundary",
                    predicate="test_namespace",
                    evidence_quote="boundary",
                )
            ]
        }
    )
    with pytest.raises(HostedOutputError):
        HostedClaimInterpreter(Client(raw, raw), "test")(
            "source", dict(subject="manual-user", scope={"test_namespace": "boundary"})
        )


def test_reschedule_must_be_a_supported_change_not_an_unrelated_assertion():
    source = "The meeting has been rescheduled to next week."
    raw = json.dumps(
        {
            "claims": [
                claim(
                    value="next week", predicate="meeting_date", evidence_quote=source
                )
            ]
        }
    )
    with pytest.raises(HostedOutputError):
        HostedClaimInterpreter(Client(raw, raw), "test")(
            source,
            dict(
                subject="manual-user",
                scope={"test_namespace": "boundary"},
                field_catalog=[
                    {"predicate": "meeting_date", "kind": "fact", "examples": ["old"]}
                ],
            ),
        )


def test_nvidia_schema_avoids_unsupported_unique_items_keyword():
    from memory.shared.hosted import route_fields

    client = Client('{"predicates":["label"]}')
    route_fields(
        client,
        "nvidia/nemotron-3.5-lightning-30b-a3b",
        "Which label?",
        [{"predicate": "label", "kind": "fact", "examples": ["A"]}],
    )
    assert "uniqueItems" not in json.dumps(client.calls[0]["response_format"])


def test_unrelated_namespace_record_failure_does_not_block_request(
    tmp_path, monkeypatch
):
    with MemoryEngine(
        config={"extraction_policy": "none"}, qdrant_path=str(tmp_path / "v")
    ) as engine:
        bench = Workbench(engine)
        first = bench.run(body())
        other = bench.run(dict(body(), namespace="other"))
        original = bench.inspection.detail

        def detail(mid, point=None):
            if mid == other["stored"]["memory_id"]:
                raise RuntimeError("Unrelated record unavailable")
            return original(mid, point)

        monkeypatch.setattr(bench.inspection, "detail", detail)
        result = bench.run(body(mode="retrieve"))
        assert (
            result["ok"]
            and first["stored"]["memory_id"]
            in result["diagnostics"]["retrieved_memory_ids"]
        )
