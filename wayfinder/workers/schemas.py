"""
wayfinder/workers — Shared schemas reused across all worker contracts.

TaskPlan (W03), EvidenceVerdict (W09), SynthesisReport (W07/W12),
RepositoryInsight (W19), CodeReview (W24).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ── Shared enums ──────────────────────────────────────────────────────────────

class ValidationStatus(str, Enum):
    PASS    = "pass"
    FAIL    = "fail"
    PARTIAL = "partial"

class EvidenceVerdict(str, Enum):
    SUPPORTED           = "supported"
    CONTRADICTED        = "contradicted"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNVERIFIED          = "unverified"

class ReviewSeverity(str, Enum):
    CRITICAL  = "critical"
    MAJOR     = "major"
    MINOR     = "minor"
    INFO      = "info"


# ── W03 Task Planner ──────────────────────────────────────────────────────────

@dataclass
class PlannedStep:
    step_number: int
    description: str
    assigned_worker: str                 # worker ID e.g. "W08_web_researcher"
    required_capabilities: list[str]     # Atlas tool IDs
    expected_output: str
    is_approval_gated: bool = False

@dataclass
class TaskPlan:
    plan_id: str
    intent_id: str                       # links back to W01 output
    goal: str
    steps: list[PlannedStep]
    estimated_worker_count: int
    requires_external_writes: bool
    requires_approval: bool
    open_questions: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.steps:
            errors.append("plan must have at least one step")
        if self.requires_external_writes and not self.requires_approval:
            errors.append("external writes always require approval")
        for step in self.steps:
            if not step.required_capabilities:
                errors.append(f"step {step.step_number} has no required_capabilities")
        return errors


# ── W06 Result Validator ──────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    validation_id: str
    target_worker: str
    target_output_id: str
    status: ValidationStatus
    checks_passed: list[str]
    checks_failed: list[str]
    corrective_actions: list[str] = field(default_factory=list)
    confidence: float = 1.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.status == ValidationStatus.FAIL and not self.corrective_actions:
            errors.append("FAIL status must include at least one corrective_action")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be in [0, 1]")
        return errors


# ── W07 / W12 Synthesis ───────────────────────────────────────────────────────

@dataclass
class SourceReference:
    url: str
    title: str
    excerpt: str
    accessed_at: str = ""

@dataclass
class SynthesisReport:
    report_id: str
    query: str
    executive_summary: str
    key_findings: list[str]
    sources: list[SourceReference]
    confidence: float
    unresolved_questions: list[str] = field(default_factory=list)
    knowledge_gaps: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.executive_summary:
            errors.append("executive_summary must be non-empty")
        if not self.key_findings:
            errors.append("key_findings must be non-empty")
        if self.confidence < 0.5 and not self.unresolved_questions:
            errors.append("low confidence report must document unresolved_questions")
        return errors


# ── W09 Source Verifier ───────────────────────────────────────────────────────

@dataclass
class EvidenceItem:
    source_url: str
    excerpt: str
    supports_claim: bool
    freshness_date: str = ""
    contradicts_claim: bool = False

@dataclass
class VerificationResult:
    verification_id: str
    claim: str
    cited_url: str
    verdict: EvidenceVerdict
    evidence: list[EvidenceItem]
    confidence: float
    reasoning: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.verdict == EvidenceVerdict.UNVERIFIED and len(self.evidence) > 0:
            errors.append("UNVERIFIED verdict should not have supporting evidence items")
        if not self.reasoning:
            errors.append("reasoning must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be in [0, 1]")
        return errors


# ── W19 Repository Analyst ────────────────────────────────────────────────────

@dataclass
class RepositoryInsight:
    analysis_id: str
    repo_path: str
    language: str
    key_modules: list[str]
    entry_points: list[str]
    dependencies: list[str]
    architectural_notes: str
    test_coverage_notes: str
    security_notes: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.key_modules:
            errors.append("key_modules must be non-empty")
        if not self.architectural_notes:
            errors.append("architectural_notes must be non-empty")
        return errors


# ── W24 Code Reviewer ─────────────────────────────────────────────────────────

@dataclass
class ReviewFinding:
    finding_id: str
    severity: ReviewSeverity
    file_path: str
    line_reference: str
    description: str
    suggestion: str

@dataclass
class CodeReview:
    review_id: str
    diff_reference: str
    summary: str
    findings: list[ReviewFinding]
    approved: bool
    blocking_issues: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.approved and self.blocking_issues:
            errors.append("approved review must not have blocking_issues")
        critical = [f for f in self.findings if f.severity == ReviewSeverity.CRITICAL]
        if critical and self.approved:
            errors.append("review with CRITICAL findings must not be approved")
        return errors


# ── W10 Document Analyst ──────────────────────────────────────────────────────

@dataclass
class DocumentFinding:
    statement: str
    quote: str
    section: str
    document_id: str
    document_title: str

@dataclass
class DocumentAnalysisReport:
    analysis_id: str
    query: str
    documents_consulted: list[dict[str, str]]
    findings: list[DocumentFinding]
    unsupported_claims: list[str] = field(default_factory=list)
    partial: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.documents_consulted:
            errors.append("documents_consulted must not be empty")
        for f in self.findings:
            if not f.quote or not f.document_id:
                errors.append(f"finding '{f.statement}' must cite both quote and document_id")
        return errors


# ── W13 Calendar Analyst ──────────────────────────────────────────────────────

@dataclass
class CalendarAnalysis:
    analysis_id: str
    query_window: dict[str, str]       # {"start": iso, "end": iso}
    timezone_name: str
    scheduled_events_count: int
    conflicts: list[dict[str, Any]]
    available_slots: list[dict[str, Any]]
    is_partial: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.timezone_name:
            errors.append("timezone_name must be specified")
        if "start" not in self.query_window or "end" not in self.query_window:
            errors.append("query_window must specify start and end")
        return errors


# ── W14 Task Manager ──────────────────────────────────────────────────────────

@dataclass
class ProposedTaskAction:
    action_type: str                   # "create" | "update" | "complete" | "delete"
    task_id: Optional[str]
    title: str
    due_date: Optional[str]
    notes: str
    requires_approval: bool = True

@dataclass
class TaskInventory:
    inventory_id: str
    task_lists_count: int
    pending_tasks: list[dict[str, Any]]
    completed_tasks: list[dict[str, Any]]
    overdue_tasks: list[dict[str, Any]]
    proposed_actions: list[ProposedTaskAction] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        for act in self.proposed_actions:
            if not act.requires_approval:
                errors.append(f"action '{act.action_type}' must require approval")
        return errors


# ── W18 Meeting Preparation Worker ────────────────────────────────────────────

@dataclass
class MeetingBrief:
    brief_id: str
    meeting_id: str
    meeting_title: str
    start_time: str
    end_time: str
    attendees: list[str]
    agenda: list[str]
    related_notes: list[str]
    related_emails: list[str]
    open_tasks: list[str]
    unresolved_questions: list[str] = field(default_factory=list)
    cited_sources: list[dict[str, str]] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.meeting_title:
            errors.append("meeting_title must not be empty")
        if not self.start_time:
            errors.append("start_time must not be empty")
        return errors


# ── W11 Data Analyst ──────────────────────────────────────────────────────────

@dataclass
class DataAnalysisReport:
    analysis_id: str
    dataset_name: str
    schema_summary: dict[str, Any]
    quality_issues: list[dict[str, Any]]
    deterministic_metrics: dict[str, Any]
    findings: list[str]
    caveats: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.findings:
            errors.append("findings must not be empty")
        if self.quality_issues and not self.caveats:
            errors.append("datasets with quality issues must include caveats")
        return errors


# ── W15 Schedule Optimizer ────────────────────────────────────────────────────

@dataclass
class ScheduleProposal:
    proposal_id: str
    target_date: str
    assigned_slots: list[dict[str, Any]]
    unassigned_tasks: list[str]
    score: float
    conflicts_resolved: list[str]
    trade_offs_explained: str
    approval_required: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.approval_required:
            errors.append("schedule proposal must always be approval_required")
        if not self.trade_offs_explained:
            errors.append("trade_offs_explained must be non-empty")
        return errors


# ── W16 Commitment Tracker ────────────────────────────────────────────────────

@dataclass
class CommitmentRecord:
    commitment_id: str
    statement: str
    owner: str
    recipient: str
    deadline: Optional[str]
    source_ref: dict[str, str]
    evidence_quote: str
    confidence: float
    status: str                        # "proposed" | "active" | "fulfilled" | "cancelled" | "uncertain"
    supersedes: Optional[str] = None

@dataclass
class CommitmentInventory:
    inventory_id: str
    commitments: list[CommitmentRecord]
    duplicates_suppressed_count: int
    unresolved_ambiguities: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        for c in self.commitments:
            if not c.evidence_quote:
                errors.append(f"commitment '{c.commitment_id}' missing evidence_quote")
            if not 0.0 <= c.confidence <= 1.0:
                errors.append(f"commitment '{c.commitment_id}' confidence out of bounds")
        return errors

