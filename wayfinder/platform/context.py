"""Orchestrator-only gateway over existing Iron Web recall and freshness proofs."""

import json
import secrets
from threading import RLock
import time

from wayfinder.platform.contracts import ContextPacket


class ContextGateway:
    def __init__(self, service, *, clock=time.time):
        self.service, self.clock, self.tickets = service, clock, {}
        self.lock = RLock()

    def retrieve(self, who, scope, query):
        self.service.authorize(who)
        exact = self.service.scope(who, scope.space, scope.task)
        if who.owner != scope.owner:
            raise ValueError("Context owner mismatch.")
        response = self.service.call(
            who,
            "recall",
            dict(
                space=scope.space,
                task_id=scope.task,
                subject=query.subject,
                predicate=query.predicate,
            ),
        )
        packet = response["packet"]
        rows = packet.get("evidence", [])
        if len(rows) > 8:
            raise ValueError("Context exceeds the v1 evidence budget.")
        evidence = []
        for row in rows:
            if row.get("scope") != exact or row.get("predicate") != query.predicate:
                raise ValueError(
                    "Memory evidence escaped the requested scope or field."
                )
            if packet["answer_status"] == "supported" and not row.get(
                "accepted_for_current_use"
            ):
                raise ValueError("Supported memory requires current accepted evidence.")
            evidence.append(
                {
                    key: row[key]
                    for key in (
                        "claim_id",
                        "memory_id",
                        "value",
                        "predicate",
                        "scope",
                        "accepted_for_current_use",
                    )
                    if key in row
                }
            )
        reference = secrets.token_urlsafe(24)
        result = ContextPacket(
            context_ref=reference,
            status=packet["answer_status"],
            subject=query.subject,
            predicate=query.predicate,
            evidence=evidence,
            warnings=packet.get("warnings", []),
            revision=response["revision"],
            expires=float(self.clock() + 120),
        ).model_dump()
        if len(json.dumps(result, ensure_ascii=False).encode()) > 2600:
            raise ValueError(
                "Context exceeds the v1 byte budget; request a narrower field."
            )
        with self.lock:
            self.tickets = {
                k: v for k, v in self.tickets.items() if v["expires"] > self.clock()
            }
            if len(self.tickets) >= 256:
                raise ValueError("Context ticket budget reached.")
            self.tickets[reference] = dict(
                scope=scope, proof=response["proof"], expires=result["expires"]
            )
        return result

    def validate(self, who, scope, reference):
        self.service.authorize(who)
        self.service.space(who, scope.space)
        with self.lock:
            item = self.tickets.get(reference)
            if not item or item["scope"] != scope or item["expires"] <= self.clock():
                raise ValueError(
                    "Context unavailable, expired, or belongs to another task."
                )
            proof = item["proof"]
        return self.service.call(
            who, "validate_context", dict(space=scope.space, proof=proof)
        )

    def clear(self):
        with self.lock:
            self.tickets.clear()
