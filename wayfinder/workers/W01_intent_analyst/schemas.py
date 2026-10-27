"""
wayfinder/workers/W01_intent_analyst/schemas.py
------------------------------------------------
Pydantic-compatible dataclasses for W01 Intent Analyst
input and output contracts.

No runtime dependencies beyond stdlib — importable in tests
without Hermes or any provider being live.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class ActionType(str, Enum):
    RESEARCH     = "research"
    CREATE       = "create"
    UPDATE       = "update"
    SCHEDULE     = "schedule"
    REVIEW       = "review"
    COMMUNICATE  = "communicate"
    ANALYSE      = "analyse"
    RECALL       = "recall"
    CLARIFY      = "clarify"


class Urgency(str, Enum):
    IMMEDIATE   = "immediate"
    TODAY       = "today"
    THIS_WEEK   = "this_week"
    UNSPECIFIED = "unspecified"


@dataclass
class IntentInput:
    raw_input: str
    session_context: Optional[str] = None   # from memory.session_search


@dataclass
class IntentOutput:
    intent_id: str
    raw_input: str
    primary_goal: str
    action_type: ActionType
    subject_entities: list[str]
    urgency: Urgency
    ambiguities: list[str]
    requires_clarification: bool
    confidence: float                        # 0.0-1.0

    def __post_init__(self):
        if not self.intent_id:
            self.intent_id = str(uuid.uuid4())
        assert 0.0 <= self.confidence <= 1.0, "confidence must be in [0, 1]"
        # Invariant: low confidence or non-empty ambiguities → clarification required
        if self.ambiguities or self.confidence < 0.6:
            object.__setattr__(self, "requires_clarification", True)

    def validate(self) -> list[str]:
        """Return list of schema violations (empty = valid)."""
        errors: list[str] = []
        if not self.primary_goal:
            errors.append("primary_goal must be non-empty")
        if self.action_type not in ActionType:
            errors.append(f"action_type '{self.action_type}' not in allowed enum")
        if not isinstance(self.subject_entities, list):
            errors.append("subject_entities must be a list")
        if not isinstance(self.ambiguities, list):
            errors.append("ambiguities must be a list")
        return errors
