"""Local manual validation adapter; no model, parser, or retrieval policy of its own."""

import re
import time
import json
import hashlib
from pathlib import Path
from threading import RLock

from memory.lifecycle.models import ClaimInput
from memory.spaces import SpaceDirectory, validate_space_id


class Inspection:
    def __init__(self, engine):
        self.engine = engine

    def _rows(self, query, params=None):
        return self.engine.graph_store.execute(query, params).rows

    def inventory(self, namespace=None):
        """Read both stores under the engine's own publication/operation locks."""
        engine = self.engine
        with engine.graph_store.write_lock, engine._operation_lock:
            points, offset = {}, None
            while True:
                batch, offset = engine.vector_store.scroll(limit=100, offset=offset)
                for point in batch:
                    if (
                        namespace is None
                        or point.payload.get("test_namespace") == namespace
                    ):
                        points[point.payload["memory_id"]] = point
                if offset is None:
                    break
            observations = self._rows(
                "MATCH(o:Observation) RETURN o.id,o.entity_id,o.source_memory_id"
            )
            ids = set(points)
            if namespace is not None:
                for mid, raw in self._rows(
                    "MATCH(s:MemorySource) RETURN s.memory_id,s.metadata_json"
                ):
                    metadata = json.loads(raw or "{}")
                    if metadata.get("test_namespace") == namespace:
                        ids.add(mid)
            orphan_ids = []
            for oid, eid, mid in observations:
                if namespace is not None:
                    continue  # Graph-only sources remain visible in the unfiltered inspection inventory.
                if mid:
                    ids.add(mid)
                elif oid.startswith("obs_"):
                    candidate = oid[4:]
                    suffix = "_" + str(eid)
                    ids.add(
                        candidate[: -len(suffix)]
                        if candidate.endswith(suffix)
                        else candidate
                    )
                elif oid == eid:
                    ids.add(oid)
                else:
                    orphan_ids.append(oid)
            records = [self.detail(mid, points.get(mid)) for mid in sorted(ids)]
            return dict(
                records=[r for r in records if r is not None],
                unowned_observation_ids=orphan_ids,
                coverage="Qdrant source records plus attributable FalkorDB observations; graph-only nodes are not source records.",
            )

    def detail(self, mid, point=None):
        engine = self.engine
        with engine.graph_store.write_lock, engine._operation_lock:
            record = engine.get(mid)
            if record is None:
                return None
            if point is None:
                raw = engine.vector_store.get_memory(mid)
                payload = raw["payload"] if raw else None
                point_id = raw["id"] if raw else None
            else:
                payload, point_id = point.payload, str(point.id)
            claims = [
                engine.inspect_claim(row[0])
                for row in self._rows(
                    "MATCH(c:MemoryClaim {memory_id:$mid}) RETURN c.id", {"mid": mid}
                )
            ]
            sources = [
                dict(row[0])
                for row in self._rows(
                    "MATCH(s:MemorySource {memory_id:$mid}) RETURN properties(s)",
                    {"mid": mid},
                )
            ]
            obs = [
                {k: v for k, v in o.items() if k != "embedding"}
                for o in engine.graph_store.get_memory_observations(mid)
            ]
            source_metadata = (
                json.loads(sources[0].get("metadata_json") or "{}") if sources else {}
            )
            space_id = (payload or {}).get(
                "test_namespace", source_metadata.get("test_namespace")
            )
            return dict(
                **record.model_dump(),
                payload=payload,
                claims=claims,
                sources=sources,
                observations=obs,
                relations=engine.graph_store.get_memory_relations(mid),
                namespace=space_id,
                memory_space_id=space_id,
                types=sorted(
                    {c["kind"] for c in claims}
                    | (
                        {payload["memory_type"]}
                        if payload and payload.get("memory_type")
                        else set()
                    )
                ),
                statuses=sorted({c["status"] for c in claims}),
                status_basis="Existing lifecycle view of stored claims"
                if claims
                else "Unavailable: no claim status exists",
                created_timestamp=(payload or {}).get(
                    "timestamp", obs[0].get("created_at") if obs else None
                ),
                updated_timestamp=None,
                backend=dict(
                    qdrant_point_id=point_id,
                    collection=engine.vector_store.collection_name,
                    graph=engine.graph_name,
                ),
            )


class Workbench:
    def __init__(self, engine, hosted_clients=None):
        self.engine = engine
        self.inspection = Inspection(engine)
        self.lock = RLock()
        self.hosted_clients = hosted_clients or {}
        self.spaces = SpaceDirectory(
            Path(engine.qdrant_path).with_name("memory_spaces.sqlite3")
        )
        self.list_spaces()  # Register existing test namespaces without rewriting memories.

    def list_spaces(self):
        with self.lock, self.engine.graph_store.write_lock, self.engine._operation_lock:
            ids, offset = set(), None
            while True:
                batch, offset = self.engine.vector_store.scroll(
                    limit=100, offset=offset
                )
                ids.update(p.payload.get("test_namespace") for p in batch)
                if offset is None:
                    break
            for row in self.inspection._rows(
                "MATCH(s:MemorySource) RETURN s.metadata_json"
            ):
                ids.add(json.loads(row[0] or "{}").get("test_namespace"))
            for space_id in ids - {None}:
                self.spaces.ensure(space_id)
        return self.spaces.list()

    def inventory(self, space_id):
        self.spaces.require(space_id)
        return dict(
            self.inspection.inventory(namespace=space_id), memory_space_id=space_id
        )

    def _memory_id(self, body):
        # Keep old records replayable, but never reuse an ID owned by another space.
        legacy = "wb_" + body["request_id"]
        record = self.engine.get(legacy)
        if record and self.inspection.detail(legacy)["namespace"] == body["namespace"]:
            return legacy
        digest = hashlib.sha256(
            (body["namespace"] + "\0" + body["request_id"]).encode()
        ).hexdigest()
        return "wb_" + digest

    def status(self):
        e = self.engine
        return dict(
            storage=e.storage_status(),
            graph=e.graph_name,
            falkordb=f"{e.config_data['falkordb']['host']}:{e.config_data['falkordb']['port']}",
            qdrant_path=e.qdrant_path,
            collection=e.vector_store.collection_name,
            embedding=e.config_data["embeddings"]["model"],
            reranker_enabled=e.config_data["retrieval"]["reranker_enabled"],
            extraction_policy=e.config_data["extraction_policy"],
            response_generation="Opt-in NVIDIA models available; evidence-only mode makes no hosted calls."
            if self.hosted_clients
            else "Evidence only; start with --nvidia to enable the configured Nemotron models.",
            models=list(self.hosted_clients),
            isolation="Required memory_space_id; legacy namespace maps to the same scope. IDs are not authentication.",
            sqlite_journal="Inactive on this direct MemoryEngine path; used by shared_server.py only.",
        )

    @staticmethod
    def validate(body):
        if not isinstance(body, dict) or set(body) - {
            "prompt",
            "mode",
            "namespace",
            "memory_space_id",
            "session_id",
            "request_id",
            "subject",
            "predicate",
            "claims",
            "confirmed",
            "top_k",
            "temporal_mode",
        }:
            raise ValueError("Unknown request fields.")
        prompt = body.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 20000:
            raise ValueError("Prompt must contain 1–20000 characters.")
        mode = body.get("mode", "retrieve")
        if mode not in {"retrieve", "store", "claim", "recall"}:
            raise ValueError("Unknown workbench operation.")
        namespace = validate_space_id(
            body.get("memory_space_id", body.get("namespace"))
        )
        if "namespace" in body and body["namespace"] != namespace:
            raise ValueError(
                "namespace and memory_space_id must identify the same space."
            )
        for key in ("request_id", "session_id"):
            if not isinstance(body.get(key), str) or not re.fullmatch(
                r"[a-f0-9-]{16,64}", body[key]
            ):
                raise ValueError("A valid request and session ID are required.")
        k = body.get("top_k", 5)
        if type(k) is not int or not 1 <= k <= 50:
            raise ValueError("Top K must be between 1 and 50.")
        if body.get("temporal_mode", "now") not in {"now", "auto", "historical"}:
            raise ValueError("Unknown temporal mode.")
        if type(body.get("confirmed", False)) is not bool:
            raise ValueError("Confirmation must be a boolean.")
        subject = body.get("subject", "manual-user")
        if not isinstance(subject, str) or not subject.strip() or len(subject) > 200:
            raise ValueError("Subject must contain 1–200 characters.")
        predicate = body.get("predicate") or None
        if predicate is not None and (
            not isinstance(predicate, str) or len(predicate) > 128
        ):
            raise ValueError("Predicate must contain at most 128 characters.")
        claims = None
        if mode == "claim":
            raw = body.get("claims")
            if not isinstance(raw, list) or not 1 <= len(raw) <= 32:
                raise ValueError("Provide 1–32 explicit ClaimInput objects.")
            claims = []
            for value in raw:
                c = ClaimInput.model_validate(value)
                if c.scope.pop("memory_space_id", namespace) != namespace:
                    raise ValueError(
                        "Claim scope differs from the selected memory space."
                    )
                if c.action == "alias" or c.aliases or c.references:
                    raise ValueError(
                        "Graph-wide aliases and reference links are unavailable in the test namespace."
                    )
                if c.scope.get("test_namespace", namespace) != namespace:
                    raise ValueError(
                        "Claim scope differs from the selected test namespace."
                    )
                c.scope["test_namespace"] = namespace
                if c.action in {"correct", "supersede", "retract"}:
                    if not c.targets:
                        raise ValueError(
                            "Select explicit target claim IDs for a change."
                        )
                    if not body.get("confirmed") or not c.reason.strip():
                        raise ValueError(
                            "Changes require user confirmation and a reason."
                        )
                if c.protected and not body.get("confirmed"):
                    raise ValueError("Protected claims require user confirmation.")
                claims.append(c.model_dump())
        elif body.get("claims"):
            raise ValueError(
                "Claims are only accepted in the explicit claim operation."
            )
        return prompt, mode, namespace, k, subject, predicate, claims

    def run(self, body):
        if not isinstance(body, dict):
            raise ValueError("Request must be an object.")
        body = dict(body)
        model = body.pop("model", None)
        _, _, namespace, *_ = self.validate(body)
        if "memory_space_id" in body:
            self.spaces.require(namespace)
        else:
            self.spaces.ensure(
                namespace
            )  # Compatibility for existing local validation scripts.
        body.pop(
            "memory_space_id", None
        )  # One canonical request contract for both spellings.
        body["namespace"] = namespace
        if model:
            if model not in self.hosted_clients:
                raise ValueError("Selected model is not enabled on this server.")
            result = self._run_hosted(body, model)
        else:
            result = self._run_local(body)
        result["memory_space_id"] = namespace
        result["diagnostics"]["memory_space_id"] = namespace
        return result

    def _run_hosted(self, body, model):
        from memory.shared.hosted import (
            field_catalog,
            HostedEvidenceAnswerer,
            HostedOutputError,
            route_fields,
        )
        from memory.shared.interpreter import HostedClaimInterpreter

        started = time.perf_counter()
        client = self.hosted_clients[model]
        result = dict(
            ok=False,
            retrieved=[],
            recall=None,
            stored=None,
            diagnostics=dict(
                pipeline_invoked=False,
                methods=[],
                retrieval_ran=False,
                retrieval_completed=False,
                retrieved_memory_ids=[],
                created_memory_ids=[],
                updated_memory_ids=[],
                changed_claims=[],
                retrieval_ms=None,
                total_ms=None,
                storage_confirmed=None,
                errors=[],
            ),
        )
        hosted = dict(model=model, extraction=None, generation=None)
        stage = "extraction"
        try:
            local = dict(body)
            metadata_extra = None
            if body.get("mode", "retrieve") == "store":
                import hashlib
                from memory.lifecycle.models import canonical_json

                digest = hashlib.sha256(
                    canonical_json(dict(body, model=model)).encode()
                ).hexdigest()
                scope = {"test_namespace": body["namespace"]}
                subject = body.get("subject", "manual-user")
                with self.lock, self.engine.graph_store.write_lock, self.engine._operation_lock:
                    snapshot = [
                        r
                        for r in self.inspection.inventory(namespace=body["namespace"])[
                            "records"
                        ]
                        if r["namespace"] == body["namespace"]
                    ]
                    catalog = field_catalog(self.engine, subject, scope)
                    existing = self.engine.get(self._memory_id(body))
                if existing:
                    if existing.metadata.get("hosted_request_digest") != digest:
                        raise ValueError(
                            "This request ID already belongs to different immutable input."
                        )
                    claims = existing.metadata["hosted_claims"]
                    trace = dict(
                        model=model, replayed=True, attempts=[], inference_ms=0
                    )
                else:
                    claims, trace = HostedClaimInterpreter(client, model).interpret(
                        body["prompt"],
                        dict(subject=subject, scope=scope, field_catalog=catalog),
                    )
                hosted["extraction"] = dict(trace, claims=claims)
                for claim in claims:
                    if existing:
                        continue
                    if claim["action"] in {"correct", "supersede", "retract"}:
                        targets = [
                            c["claim_id"]
                            for r in snapshot
                            for c in r["claims"]
                            if c["current_eligible"]
                            and c["subject"] == subject
                            and c["predicate"] == claim["predicate"]
                            and c["scope"] == scope
                        ]
                        if not targets:
                            raise ValueError(
                                "No eligible target exists for this inferred change; nothing was written."
                            )
                        claim["targets"] = targets
                if claims:
                    local.update(mode="claim", claims=claims)
                metadata_extra = dict(
                    hosted_request_digest=digest,
                    hosted_model=model,
                    hosted_claims=claims,
                )
            stage = "memory"
            result = self._run_local(local, metadata_extra=metadata_extra)
            if result["ok"] and body.get("mode", "retrieve") in {"retrieve", "recall"}:
                stage = "generation"
                answer_input = result
                if body.get("mode", "retrieve") == "retrieve":
                    scope = {"test_namespace": body["namespace"]}
                    subject = body.get("subject", "manual-user")
                    catalog = field_catalog(self.engine, subject, scope)
                    if catalog:
                        stage = "field_routing"
                        predicates, hosted["field_routing"] = route_fields(
                            client, model, body["prompt"], catalog
                        )
                        packets = []
                        retrieval_started = time.perf_counter()
                        for predicate in predicates:
                            packets.append(
                                self.engine.recall(
                                    body["prompt"],
                                    subject=subject,
                                    predicate=predicate,
                                    scope=scope,
                                    temporal_mode=body.get("temporal_mode", "now"),
                                )
                            )
                            result["diagnostics"]["methods"].append(
                                "MemoryEngine.recall"
                            )
                        if packets:
                            result["field_recall"] = packets
                            evidence = [e for p in packets for e in p["evidence"]]
                            statuses = {p["answer_status"] for p in packets}
                            status = (
                                "disputed"
                                if "disputed" in statuses
                                else "unconfirmed"
                                if "unconfirmed" in statuses
                                else "missing"
                                if not evidence
                                else "supported"
                            )
                            answer_input = dict(
                                recall=dict(evidence=evidence, answer_status=status)
                            )
                            result["diagnostics"]["generation_memory_ids"] = sorted(
                                {e["memory_id"] for e in evidence}
                            )
                            result["diagnostics"]["routed_fields"] = predicates
                            result["diagnostics"]["field_retrieval_ms"] = round(
                                (time.perf_counter() - retrieval_started) * 1000, 3
                            )
                stage = "generation"
                result["assistant"], hosted["generation"] = HostedEvidenceAnswerer(
                    client, model
                ).answer(body["prompt"], answer_input)
        except Exception as error:
            if isinstance(error, HostedOutputError):
                hosted[stage] = error.trace
            message = (
                str(error)
                if isinstance(error, ValueError)
                else "Hosted request failed; no model output was accepted."
            )
            result["ok"] = False
            result["diagnostics"]["errors"].append(
                dict(
                    stage=stage,
                    type=type(error).__name__,
                    message=message,
                    http_status=getattr(error, "status_code", None),
                )
            )
        result["diagnostics"]["hosted"] = hosted
        result["diagnostics"]["total_ms"] = round(
            (time.perf_counter() - started) * 1000, 3
        )
        return result

    def _run_local(self, body, metadata_extra=None):
        prompt, mode, namespace, k, subject, predicate, claims = self.validate(body)
        started = time.perf_counter()
        diag = dict(
            pipeline_invoked=False,
            methods=[],
            retrieval_ran=False,
            retrieval_completed=False,
            retrieved_memory_ids=[],
            created_memory_ids=[],
            updated_memory_ids=[],
            changed_claims=[],
            retrieval_ms=None,
            total_ms=None,
            storage_confirmed=None,
            errors=[],
        )
        result = dict(
            ok=False, diagnostics=diag, retrieved=[], recall=None, stored=None
        )
        with self.lock, self.engine.graph_store.write_lock, self.engine._operation_lock:
            try:
                inventory = self.inspection.inventory(namespace=namespace)["records"]
                scoped = [r for r in inventory if r["namespace"] == namespace]
                if claims:
                    owned = {c["claim_id"] for r in scoped for c in r["claims"]}
                    for c in claims:
                        if set(c.get("targets") or []) - owned:
                            raise ValueError(
                                "Change targets must belong to the selected test namespace."
                            )
                before = {c["claim_id"]: c for r in scoped for c in r["claims"]}
                t = time.perf_counter()
                diag["pipeline_invoked"] = True
                if mode == "recall":
                    diag["retrieval_ran"] = True
                    diag["methods"].append("MemoryEngine.recall")
                    packet = self.engine.recall(
                        prompt,
                        subject=subject,
                        predicate=predicate,
                        scope={"test_namespace": namespace},
                        temporal_mode=body.get("temporal_mode", "now"),
                    )
                    result["recall"] = packet
                    diag["retrieved_memory_ids"] = sorted(
                        {c["memory_id"] for c in packet["evidence"]}
                    )
                else:
                    diag["retrieval_ran"] = bool(scoped)
                    diag["methods"].append("MemoryEngine.search")
                    hits = self.engine.search(
                        prompt,
                        k=k,
                        temporal_mode=body.get("temporal_mode", "now"),
                        document_ids=[r["memory_id"] for r in scoped],
                    )
                    result["retrieved"] = [h.model_dump() for h in hits]
                    diag["retrieved_memory_ids"] = [h.memory_id for h in hits]
                    if not scoped:
                        diag["retrieval_note"] = (
                            "Search called with an empty namespace inventory; engine short-circuited before embedding/vector retrieval."
                        )
                diag["retrieval_ms"] = round((time.perf_counter() - t) * 1000, 3)
                diag["retrieval_completed"] = True
                if mode in {"store", "claim"}:
                    diag["methods"].append("MemoryEngine.add")
                    mid = self._memory_id(body)
                    existing = self.engine.get(mid)
                    existed = existing is not None
                    space_metadata = {"memory_space_id": namespace}
                    if existing and "memory_space_id" not in existing.metadata:
                        space_metadata = {}  # Preserve pre-space immutable receipt metadata.
                    mid = self.engine.add(
                        prompt,
                        memory_id=mid,
                        claims=claims,
                        source_info=dict(
                            origin="user",
                            actor_id="workbench:" + namespace,
                            user_confirmed=body.get("confirmed", False),
                            event_id=body["request_id"],
                            quality=0.9,
                        ),
                        metadata=dict(
                            source="manual_workbench",
                            test_namespace=namespace,
                            **space_metadata,
                            session_id=body["session_id"],
                            **(metadata_extra or {}),
                        ),
                    )
                    if not existed:
                        diag["created_memory_ids"] = [mid]
                    result["stored"] = self.inspection.detail(mid)
                    diag["storage_confirmed"] = bool(
                        result["stored"]
                        and result["stored"]["vector_stored"]
                        and result["stored"]["graph_stored"]
                    )
                    after = self.inspection.inventory(namespace=namespace)["records"]
                    for r in after:
                        for c in r["claims"]:
                            prior = before.get(c["claim_id"])
                            if prior and (prior["status"], prior["changed_by"]) != (
                                c["status"],
                                c["changed_by"],
                            ):
                                diag["changed_claims"].append(
                                    dict(
                                        claim_id=c["claim_id"],
                                        memory_id=c["memory_id"],
                                        before=prior["status"],
                                        after=c["status"],
                                        changed_by=c["changed_by"],
                                    )
                                )
                result["ok"] = True
            except Exception as error:
                # Never return driver exceptions containing connection details or credentials.
                from memory.models import EngineStorageError

                message = (
                    str(error)
                    if isinstance(error, ValueError)
                    else "Operation failed. Inspect the local console and storage; no completion is asserted."
                )
                info = dict(type=type(error).__name__, message=message)
                if isinstance(error, EngineStorageError):
                    info.update(
                        memory_id=error.memory_id, rolled_back=error.rolled_back
                    )
                diag["errors"].append(info)
            finally:
                diag["total_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return result
