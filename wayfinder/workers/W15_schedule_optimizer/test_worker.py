"""
wayfinder/workers/W15_schedule_optimizer/test_worker.py
────────────────────────────────────────────────────────
Offline contract tests for W15 Schedule Optimizer.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import ScheduleProposal


def make_proposal(**overrides) -> ScheduleProposal:
    defaults = dict(
        proposal_id="sched-prop-001",
        target_date="2026-10-27",
        assigned_slots=[
            {
                "task_title": "Draft Proposal",
                "start": "2026-10-27T09:00:00+00:00",
                "end": "2026-10-27T10:30:00+00:00",
            }
        ],
        unassigned_tasks=[],
        score=95.0,
        conflicts_resolved=["Moved personal focus block 30 mins earlier"],
        trade_offs_explained="Placed high priority task at peak morning focus window; zero deadline violations.",
        approval_required=True,
    )
    defaults.update(overrides)
    return ScheduleProposal(**defaults)


class TestScheduleProposalSchema:
    def test_valid_proposal_passes(self):
        prop = make_proposal()
        assert prop.validate() == []

    def test_approval_required_invariant(self):
        prop = make_proposal(approval_required=False)
        errors = prop.validate()
        assert any("approval_required" in e for e in errors)

    def test_missing_trade_offs_fails(self):
        prop = make_proposal(trade_offs_explained="")
        errors = prop.validate()
        assert any("trade_offs_explained" in e for e in errors)


class TestW15DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W15"
        assert "Schedule Optimizer" in data["name"]
        assert "google.calendar_read" in data["capabilities"]
        assert "google.calendar_write" in data["approval_gated_capabilities"]
        assert data["output_contract"] == "ScheduleProposal"
