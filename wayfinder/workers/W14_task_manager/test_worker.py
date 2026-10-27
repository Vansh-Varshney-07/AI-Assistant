"""
wayfinder/workers/W14_task_manager/test_worker.py
──────────────────────────────────────────────────
Offline contract tests for W14 Task Manager.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import TaskInventory, ProposedTaskAction


def make_inventory(**overrides) -> TaskInventory:
    defaults = dict(
        inventory_id="inv-001",
        task_lists_count=1,
        pending_tasks=[
            {"id": "t1", "title": "Submit Quarterly Review", "due": "2026-10-30T17:00:00Z"}
        ],
        completed_tasks=[],
        overdue_tasks=[],
        proposed_actions=[
            ProposedTaskAction(
                action_type="create",
                task_id=None,
                title="Prepare Agenda for Friday",
                due_date="2026-10-29T12:00:00Z",
                notes="Created based on email thread",
                requires_approval=True,
            )
        ],
    )
    defaults.update(overrides)
    return TaskInventory(**defaults)


class TestTaskInventorySchema:
    def test_valid_inventory_passes(self):
        inv = make_inventory()
        assert inv.validate() == []

    def test_action_without_approval_fails(self):
        unapproved_action = ProposedTaskAction(
            action_type="delete",
            task_id="t1",
            title="Submit Quarterly Review",
            due_date=None,
            notes="Deleting",
            requires_approval=False,
        )
        inv = make_inventory(proposed_actions=[unapproved_action])
        errors = inv.validate()
        assert any("must require approval" in e for e in errors)


class TestW14DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W14"
        assert "Task Manager" in data["name"]
        assert "google.tasks_read" in data["capabilities"]
        assert "google.tasks_write" in data["approval_gated_capabilities"]
        assert data["output_contract"] == "TaskInventory"
