"""
wayfinder/workers/W01_intent_analyst/fixtures.py
-------------------------------------------------
Synthetic fixtures for W01 Intent Analyst.
No live tool calls. Tests validate schema contract only.
"""
from __future__ import annotations
from wayfinder.workers.W01_intent_analyst.schemas import (
    ActionType, IntentOutput, Urgency
)

# ── Success fixtures ──────────────────────────────────────────────────────────

SUCCESS_CLEAR_RESEARCH = IntentOutput(
    intent_id="test-w01-001",
    raw_input="Research the best Python async frameworks and summarise findings",
    primary_goal="Research async Python frameworks and produce a summary",
    action_type=ActionType.RESEARCH,
    subject_entities=["Python", "async frameworks"],
    urgency=Urgency.UNSPECIFIED,
    ambiguities=[],
    requires_clarification=False,
    confidence=0.92,
)

SUCCESS_SCHEDULE_TODAY = IntentOutput(
    intent_id="test-w01-002",
    raw_input="Block 2 hours on my calendar for deep work this afternoon",
    primary_goal="Create a 2-hour deep work calendar block for today",
    action_type=ActionType.SCHEDULE,
    subject_entities=["calendar", "deep work block"],
    urgency=Urgency.TODAY,
    ambiguities=[],
    requires_clarification=False,
    confidence=0.88,
)

SUCCESS_COMMUNICATE = IntentOutput(
    intent_id="test-w01-003",
    raw_input="Draft a reply to Rahul's WhatsApp asking about Friday's meeting",
    primary_goal="Draft a WhatsApp reply to Rahul about Friday meeting",
    action_type=ActionType.COMMUNICATE,
    subject_entities=["Rahul", "Friday meeting", "WhatsApp"],
    urgency=Urgency.TODAY,
    ambiguities=[],
    requires_clarification=False,
    confidence=0.85,
)

# ── Failure / clarification fixtures ─────────────────────────────────────────

CLARIFICATION_AMBIGUOUS = IntentOutput(
    intent_id="test-w01-004",
    raw_input="Do it",
    primary_goal="Unknown — insufficient context",
    action_type=ActionType.CLARIFY,
    subject_entities=[],
    urgency=Urgency.UNSPECIFIED,
    ambiguities=["What action should be performed?", "What is the target subject?"],
    requires_clarification=True,
    confidence=0.1,
)

CLARIFICATION_LOW_CONFIDENCE = IntentOutput(
    intent_id="test-w01-005",
    raw_input="Handle the email thing from yesterday",
    primary_goal="Process an email from the previous day",
    action_type=ActionType.COMMUNICATE,
    subject_entities=["email"],
    urgency=Urgency.UNSPECIFIED,
    ambiguities=["Which email is being referred to?", "What action is needed: read, reply, or forward?"],
    requires_clarification=True,
    confidence=0.45,
)

ALL_FIXTURES = [
    SUCCESS_CLEAR_RESEARCH,
    SUCCESS_SCHEDULE_TODAY,
    SUCCESS_COMMUNICATE,
    CLARIFICATION_AMBIGUOUS,
    CLARIFICATION_LOW_CONFIDENCE,
]
