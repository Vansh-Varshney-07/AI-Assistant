"""
tests/test_approval_service.py
──────────────────────────────
Unit tests for Wayfinder Atlas Approval & Execution Governance Service.

Tests:
  - Action request & human-readable preview generation
  - Authorization & single-use token issuance
  - Denial & rejection of execution
  - Token expiration & invalidation
  - Single-use token enforcement (prevents replay)
  - Idempotency & duplicate submission deduplication
"""

from datetime import datetime, timezone, timedelta
import pytest

from wayfinder.atlas.harness.approval_service import (
    ApprovalService,
    ApprovalStatus,
    ApprovalToken,
)
from wayfinder.atlas.harness.envelope import ToolStatus


class TestApprovalService:
    def test_request_approval_and_preview(self):
        svc = ApprovalService()
        action = svc.request_approval(
            worker_id="W14_task_manager",
            tool_id="google.tasks_write",
            description="Create task: 'Review pull request #42'",
            payload={"title": "Review pull request #42", "due": "2026-10-30T17:00:00Z"},
            risk_level="medium",
        )
        assert action.action_id.startswith("act-")
        assert action.status == ApprovalStatus.PENDING

        preview = svc.format_preview(action.action_id)
        assert "google.tasks_write" in preview
        assert "Review pull request #42" in preview
        assert "MEDIUM" in preview

    def test_authorize_approved_issues_token(self):
        svc = ApprovalService()
        action = svc.request_approval(
            worker_id="W15_schedule_optimizer",
            tool_id="google.calendar_write",
            description="Schedule focus block",
            payload={"summary": "Focus Block", "start": "2026-10-27T09:00:00Z"},
        )
        token = svc.authorize(action.action_id, approved=True, reason="User confirmed")
        assert token is not None
        assert token.is_valid()
        assert action.status == ApprovalStatus.APPROVED

    def test_authorize_denied_blocks_token(self):
        svc = ApprovalService()
        action = svc.request_approval(
            worker_id="W14_task_manager",
            tool_id="google.tasks_write",
            description="Delete all tasks",
            payload={"action": "delete_all"},
            risk_level="high",
        )
        token = svc.authorize(action.action_id, approved=False, reason="Too destructive")
        assert token is None
        assert action.status == ApprovalStatus.DENIED

        # Execution without token must fail
        res = svc.execute_gated(action.action_id, token=None, executor=lambda p: True)
        assert res.success is False
        assert res.status == ToolStatus.PERMISSION_DENIED

    def test_execute_gated_success_and_spent_token(self):
        svc = ApprovalService()
        action = svc.request_approval(
            worker_id="W10_document_analyst",
            tool_id="google.docs_write",
            description="Append executive summary to Google Doc",
            payload={"doc_id": "doc-99", "text": "Summary content"},
        )
        token = svc.authorize(action.action_id, approved=True)

        executed_payloads = []
        def mock_executor(payload):
            executed_payloads.append(payload)
            return {"updated": True, "revision": 2}

        res = svc.execute_gated(action.action_id, token=token, executor=mock_executor)
        assert res.success is True
        assert res.status == ToolStatus.OK
        assert len(executed_payloads) == 1
        assert token.spent is True

        # Re-executing with the now-spent token must be denied
        replay_res = svc.execute_gated(action.action_id, token=token, executor=mock_executor)
        assert replay_res.status in {ToolStatus.PARTIAL, ToolStatus.PERMISSION_DENIED}

    def test_duplicate_request_idempotency(self):
        svc = ApprovalService()
        payload = {"title": "Send invoice", "amount": 500}
        act1 = svc.request_approval("W14", "notion.create_page", "Create page", payload)
        act2 = svc.request_approval("W14", "notion.create_page", "Create page", payload)

        assert act1.action_id == act2.action_id
        assert act1.fingerprint == act2.fingerprint

    def test_expired_action_cannot_be_approved(self):
        # Service with negative/zero TTL for testing
        svc = ApprovalService(default_ttl_seconds=-10)
        action = svc.request_approval("W14", "google.tasks_write", "Overdue approval", {})
        token = svc.authorize(action.action_id, approved=True)
        assert token is None
        assert action.status == ApprovalStatus.EXPIRED
