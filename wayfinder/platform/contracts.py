"""Platform-owned v1 contracts. Existing worker task/result contracts are unchanged."""

from typing import Annotated, Literal
import json
from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSION = "wayfinder.platform/1"


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Scope(Contract):
    owner: str = Field(min_length=1, max_length=200)
    space: str = Field(min_length=1, max_length=200)
    task: str = Field(min_length=1, max_length=100)

    def worker_scope(self):
        return (self.owner, self.space, self.task)


class ArtifactReference(Contract):
    """Opaque, scoped broker reference. A path or model-supplied URL is not a grant."""
    reference: str = Field(min_length=1, max_length=200)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    media_type: str = Field(min_length=1, max_length=100)


class TaskEnvelope(Contract):
    """Platform transport wrapper; worker-owned output schemas remain unchanged."""
    contract: Literal['wayfinder.task-envelope/1'] = 'wayfinder.task-envelope/1'
    request_id: str = Field(min_length=1, max_length=100)
    run_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    worker_role: str = Field(pattern=r'^(W(0[1-9]|[1-3][0-9]|4[0-7])|CHAT)$')
    scope: Scope
    artifacts: tuple[ArtifactReference, ...] = Field(default=(), max_length=8)
    deadline: float = Field(gt=0, allow_inf_nan=False)
    cancellation_id: str = Field(min_length=1, max_length=100)


class WorkerOutcome(Contract):
    contract: Literal['wayfinder.worker-outcome/1'] = 'wayfinder.worker-outcome/1'
    run_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    status: Literal['completed','failed','cancelled','interrupted','stale','uncertain']
    output: dict | None = None
    evidence: tuple[ArtifactReference, ...] = Field(default=(), max_length=8)
    warnings: tuple[Annotated[str, Field(max_length=2000)], ...] = Field(default=(), max_length=16)
    execution_ref: str = Field(min_length=1, max_length=200)
    error_ref: str | None = Field(default=None, max_length=200)

    @model_validator(mode='after')
    def completed_requires_output(self):
        if self.status == 'completed' and self.output is None:
            raise ValueError('A completed worker outcome requires structured output.')
        try:
            if len(json.dumps(self.output,allow_nan=False).encode('utf-8'))>32000:
                raise ValueError('Worker output exceeds the bounded transport limit.')
        except (TypeError,ValueError):
            raise ValueError('Worker output must be bounded finite JSON.') from None
        return self


class ContextQuery(Contract):
    subject: str = Field(default="me", min_length=1, max_length=200)
    predicate: str = Field(min_length=1, max_length=128)


class ContextPacket(Contract):
    contract: Literal["wayfinder.platform/1"] = VERSION
    context_ref: str
    status: str
    subject: str
    predicate: str
    evidence: list[dict] = Field(max_length=8)
    warnings: list[str]
    revision: str
    expires: float


class ReadRequest(Contract):
    """One fixed read-only workflow; no arbitrary tool, worker or DAG dispatch."""

    contract: Literal["wayfinder.platform/1"] = VERSION
    request_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=1000)
    reference: str = Field(min_length=1, max_length=200)
    context: ContextQuery
    deadline_seconds: int = Field(default=110, ge=5, le=110)


class ActionBinding(Contract):
    """Versioned reference; the trusted plan binding and ActionGate enforce authority."""

    contract: Literal["wayfinder.platform/1"] = VERSION
    action_ref: str
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    expires: float
    backend: Literal["desktop_action_gate", "git_branch_gate", "memory_event_gate"] = (
        "desktop_action_gate"
    )
