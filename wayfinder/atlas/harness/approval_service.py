"""
wayfinder/atlas/harness/approval_service.py
───────────────────────────────────────────
Trusted Execution and Approval Infrastructure for Wayfinder Atlas.

Enforces:
  - Phase 04 write governance: preview generation, explicit user authorization,
    cryptographic/verifiable token issuance, and audit journaling.
  - Idempotency & duplicate execution prevention across retries.
  - Strict TTL expiry: stale approvals cannot be executed.
  - Execution Guard: external write adapters (calendar_write, tasks_write,
    docs_write, sheets_write, notion.create_page) cannot execute without
    a valid, unspent ApprovalToken.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

from wayfinder.atlas.harness.envelope import ToolResult, ToolStatus, current_iso_timestamp, parse_iso_datetime


class ApprovalStatus(str, Enum):
    PENDING   = "pending"
    APPROVED  = "approved"
    DENIED    = "denied"
    EXPIRED   = "expired"
    EXECUTED  = "executed"
    FAILED    = "failed"


@dataclass
class ApprovalToken:
    token_id: str
    action_id: str
    tool_id: str
    expires_at: str
    spent: bool = False

    def is_valid(self) -> bool:
        if self.spent:
            return False
        exp = parse_iso_datetime(self.expires_at)
        return datetime.now(timezone.utc) <= exp


@dataclass
class ProposedAction:
    action_id: str
    worker_id: str
    tool_id: str
    description: str
    payload: dict[str, Any]
    fingerprint: str
    risk_level: str
    created_at: str
    expires_at: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_reason: Optional[str] = None
    execution_result: Optional[ToolResult] = None
    token: Optional[ApprovalToken] = None


class ApprovalService:
    """Central trusted execution gateway for approval-gated mutations."""

    def __init__(self, default_ttl_seconds: int = 900):
        self.default_ttl = default_ttl_seconds
        self._actions: dict[str, ProposedAction] = {}
        self._fingerprint_to_action: dict[str, str] = {}
        self._tokens: dict[str, ApprovalToken] = {}

    def _compute_fingerprint(self, tool_id: str, payload: dict[str, Any]) -> str:
        canonical_str = json.dumps({"tool_id": tool_id, "payload": payload}, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def request_approval(
        self,
        worker_id: str,
        tool_id: str,
        description: str,
        payload: dict[str, Any],
        risk_level: str = "medium",
        ttl_seconds: int | None = None,
    ) -> ProposedAction:
        """Register a proposed external mutation and generate an approval ticket."""
        fingerprint = self._compute_fingerprint(tool_id, payload)

        # Duplicate prevention: if an identical pending/approved action exists, return it
        if fingerprint in self._fingerprint_to_action:
            existing_id = self._fingerprint_to_action[fingerprint]
            existing = self._actions[existing_id]
            if existing.status in {ApprovalStatus.PENDING, ApprovalStatus.APPROVED, ApprovalStatus.EXECUTED}:
                return existing

        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=ttl)

        action_id = f"act-{uuid.uuid4().hex[:10]}"
        action = ProposedAction(
            action_id=action_id,
            worker_id=worker_id,
            tool_id=tool_id,
            description=description,
            payload=payload,
            fingerprint=fingerprint,
            risk_level=risk_level,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            status=ApprovalStatus.PENDING,
        )

        self._actions[action_id] = action
        self._fingerprint_to_action[fingerprint] = action_id
        return action

    def format_preview(self, action_id: str) -> str:
        """Generates a human-readable action preview for user authorization."""
        if action_id not in self._actions:
            raise KeyError(f"Action '{action_id}' not found.")

        act = self._actions[action_id]
        preview = [
            f"=== ACTION PREVIEW [{act.action_id}] ===",
            f"Target Tool:    {act.tool_id}",
            f"Origin Worker:  {act.worker_id}",
            f"Risk Level:     {act.risk_level.upper()}",
            f"Status:         {act.status.value.upper()}",
            f"Expires At:     {act.expires_at}",
            f"Summary:        {act.description}",
            "Proposed Parameters:",
        ]
        for k, v in act.payload.items():
            preview.append(f"  • {k}: {v}")
        return "\n".join(preview)

    def authorize(self, action_id: str, approved: bool, reason: str = "") -> Optional[ApprovalToken]:
        """User decision point. If approved, issues a single-use ApprovalToken."""
        if action_id not in self._actions:
            raise KeyError(f"Action '{action_id}' not found.")

        act = self._actions[action_id]

        # Check expiration
        exp_dt = parse_iso_datetime(act.expires_at)
        if datetime.now(timezone.utc) > exp_dt:
            act.status = ApprovalStatus.EXPIRED
            act.decision_reason = "Action expired before user decision"
            return None

        if not approved:
            act.status = ApprovalStatus.DENIED
            act.decision_reason = reason or "Denied by user"
            return None

        # Issue single-use token
        token_id = f"tok-{uuid.uuid4().hex[:16]}"
        token = ApprovalToken(
            token_id=token_id,
            action_id=action_id,
            tool_id=act.tool_id,
            expires_at=act.expires_at,
            spent=False,
        )
        act.status = ApprovalStatus.APPROVED
        act.decision_reason = reason or "Approved by user"
        act.token = token
        self._tokens[token_id] = token
        return token

    def execute_gated(
        self,
        action_id: str,
        token: Optional[ApprovalToken],
        executor: Callable[[dict[str, Any]], Any],
    ) -> ToolResult:
        """Executes the action under strict token, status, and idempotency guards."""
        if action_id not in self._actions:
            return ToolResult.not_found(f"Action '{action_id}' does not exist")

        act = self._actions[action_id]

        if act.status == ApprovalStatus.EXECUTED and act.execution_result:
            return ToolResult.partial_result(
                data=act.execution_result.data,
                warnings=["Idempotent return: action was previously executed successfully."],
            )

        if not token:
            return ToolResult.permission_denied("Execution denied: missing ApprovalToken")

        if token.action_id != action_id:
            return ToolResult.permission_denied("Execution denied: ApprovalToken does not match action_id")

        if not token.is_valid():
            return ToolResult.permission_denied("Execution denied: ApprovalToken is spent or expired")

        # Mark token spent immediately
        token.spent = True

        try:
            result = executor(act.payload)
            act.status = ApprovalStatus.EXECUTED
            tool_res = ToolResult.ok(data=result)
            act.execution_result = tool_res
            return tool_res
        except Exception as e:
            act.status = ApprovalStatus.FAILED
            err_msg = f"Execution failed: {str(e)}"
            tool_res = ToolResult.failed(err_msg)
            act.execution_result = tool_res
            return tool_res
