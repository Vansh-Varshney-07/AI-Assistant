"""
wayfinder/workers/W16_commitment_tracker/test_worker.py
────────────────────────────────────────────────────────
Offline contract tests for W16 Commitment Tracker.
"""
from pathlib import Path
import pytest
import yaml
from wayfinder.workers.schemas import CommitmentInventory, CommitmentRecord


def make_commitment_inventory(**overrides) -> CommitmentInventory:
    defaults = dict(
        inventory_id="comm-inv-001",
        commitments=[
            CommitmentRecord(
                commitment_id="c-001",
                statement="send the revised architecture doc",
                owner="me",
                recipient="team",
                deadline="Friday EOD",
                source_ref={"system": "gmail", "item_id": "thread-123"},
                evidence_quote="I will send the revised architecture doc by Friday EOD.",
                confidence=0.88,
                status="proposed",
                supersedes=None,
            )
        ],
        duplicates_suppressed_count=1,
        unresolved_ambiguities=[],
    )
    defaults.update(overrides)
    return CommitmentInventory(**defaults)


class TestCommitmentInventorySchema:
    def test_valid_inventory_passes(self):
        inv = make_commitment_inventory()
        assert inv.validate() == []

    def test_missing_evidence_quote_fails(self):
        bad_comm = CommitmentRecord(
            commitment_id="c-bad",
            statement="deliver feature",
            owner="me",
            recipient="lead",
            deadline=None,
            source_ref={"system": "gmail", "item_id": "m1"},
            evidence_quote="",  # missing
            confidence=0.8,
            status="proposed",
        )
        inv = make_commitment_inventory(commitments=[bad_comm])
        errors = inv.validate()
        assert any("missing evidence_quote" in e for e in errors)

    def test_confidence_out_of_bounds_fails(self):
        bad_comm = CommitmentRecord(
            commitment_id="c-bad",
            statement="deliver feature",
            owner="me",
            recipient="lead",
            deadline=None,
            source_ref={"system": "gmail", "item_id": "m1"},
            evidence_quote="I will deliver feature",
            confidence=1.5,  # out of bounds
            status="proposed",
        )
        inv = make_commitment_inventory(commitments=[bad_comm])
        errors = inv.validate()
        assert any("confidence out of bounds" in e for e in errors)


class TestW16DefinitionContract:
    def test_definition_yaml_exists_and_valid(self):
        p = Path(__file__).parent / "definition.yaml"
        assert p.exists()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["id"] == "W16"
        assert "Commitment Tracker" in data["name"]
        assert "google.gmail_read" in data["capabilities"]
        assert "whatsapp.reply_text" in data["denied_capabilities"]
        assert data["output_contract"] == "CommitmentInventory"
