"""Platform-owned v1 contracts. Existing worker task/result contracts are unchanged."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

VERSION = "wayfinder.platform/1"


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Scope(Contract):
    owner: str = Field(min_length=1, max_length=200)
    space: str = Field(min_length=1, max_length=200)
    task: str = Field(min_length=1, max_length=100)

    def worker_scope(self):
        return (self.owner, self.space, self.task)


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
