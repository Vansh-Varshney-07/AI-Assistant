"""
wayfinder/workers/W03_task_planner/tests.py
-------------------------------------------
Offline contract tests for W03 Task Planner.
"""
import pytest
from wayfinder.workers.schemas import TaskPlan, PlannedStep


def make_plan(**overrides) -> TaskPlan:
    defaults = dict(
        plan_id="test-w03-001",
        intent_id="test-w01-001",
        goal="Research async Python frameworks",
        steps=[
            PlannedStep(
                step_number=1,
                description="Search the web for async Python frameworks",
                assigned_worker="W08_web_researcher",
                required_capabilities=["tavily_search", "tavily_extract"],
                expected_output="List of candidate frameworks with URLs",
            ),
            PlannedStep(
                step_number=2,
                description="Synthesise findings into a structured summary",
                assigned_worker="W12_knowledge_synthesizer",
                required_capabilities=["memory.session_search"],
                expected_output="SynthesisReport with key_findings and sources",
            ),
        ],
        estimated_worker_count=2,
        requires_external_writes=False,
        requires_approval=False,
    )
    defaults.update(overrides)
    return TaskPlan(**defaults)


class TestTaskPlanSchema:
    def test_valid_plan_passes(self):
        plan = make_plan()
        assert plan.validate() == []

    def test_empty_steps_fails(self):
        plan = make_plan(steps=[])
        assert any("at least one step" in e for e in plan.validate())

    def test_external_write_requires_approval(self):
        plan = make_plan(requires_external_writes=True, requires_approval=False)
        errors = plan.validate()
        assert any("approval" in e for e in errors)

    def test_step_without_capabilities_fails(self):
        plan = make_plan(steps=[
            PlannedStep(
                step_number=1,
                description="A step with no capabilities",
                assigned_worker="W08_web_researcher",
                required_capabilities=[],   # invalid
                expected_output="Something",
            )
        ])
        errors = plan.validate()
        assert any("required_capabilities" in e for e in errors)

    def test_approval_gated_step_propagates(self):
        plan = make_plan(
            steps=[
                PlannedStep(
                    step_number=1,
                    description="Send WhatsApp reply",
                    assigned_worker="W32_message_action_worker",
                    required_capabilities=["whatsapp.reply_text"],
                    expected_output="Message sent",
                    is_approval_gated=True,
                )
            ],
            requires_external_writes=True,
            requires_approval=True,
        )
        assert plan.validate() == []
        assert any(s.is_approval_gated for s in plan.steps)

    def test_steps_link_to_intent(self):
        plan = make_plan(intent_id="test-w01-002")
        assert plan.intent_id == "test-w01-002"
