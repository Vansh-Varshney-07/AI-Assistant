"""
wayfinder/atlas/harness/base.py
───────────────────────────────
General-Purpose Application Harness Architecture.

Defines standardized, reusable provider protocols so that individual apps
(Notion, Google Workspace, WhatsApp, Tavily, Windows Desktop, and future apps)
plug into general-purpose agent harnesses rather than requiring custom,
brittle agent runtimes for every single tool.

Harness Types:
  1. KnowledgeProvider: Unified interface for notes, docs, and knowledge bases.
  2. TaskProvider:      Unified interface for tasks, to-dos, and deadlines.
  3. MessagingProvider: Unified interface for chat, email, and notifications.
  4. DesktopProvider:   Unified interface for local OS file and app automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


# ── Common Data Models ────────────────────────────────────────────────────────

@dataclass
class KnowledgeItem:
    id: str
    title: str
    content: str
    provider: str                      # "notion", "google_docs", "google_drive", "local_file"
    url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""


@dataclass
class TaskItem:
    id: str
    title: str
    provider: str                      # "google_tasks", "todoist", "internal_todo"
    due_date: str = ""
    status: str = "pending"            # "pending", "completed"
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageItem:
    id: str
    sender: str
    recipient: str
    content: str
    provider: str                      # "whatsapp", "gmail"
    timestamp: str = ""
    attachments: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ── General-Purpose Provider Protocols ────────────────────────────────────────

@runtime_checkable
class KnowledgeProvider(Protocol):
    """Protocol for any knowledge base: Notion, Google Docs, Drive, Markdown."""
    provider_name: str

    def search(self, query: str, limit: int = 5) -> list[KnowledgeItem]:
        """Search notes, pages, or documents matching query."""
        ...

    def read(self, item_id: str) -> KnowledgeItem:
        """Read full content of a specific page or document."""
        ...

    def create(self, title: str, content: str, parent_id: str | None = None) -> KnowledgeItem:
        """Create a new note/page (approval-gated)."""
        ...

    def update(self, item_id: str, content: str) -> KnowledgeItem:
        """Append or update content of an existing note (approval-gated)."""
        ...


@runtime_checkable
class TaskProvider(Protocol):
    """Protocol for any task manager: Google Tasks, Todoist, internal todos."""
    provider_name: str

    def list_tasks(self, status: str = "pending", limit: int = 20) -> list[TaskItem]:
        """List tasks matching status."""
        ...

    def create_task(self, title: str, due_date: str = "", notes: str = "") -> TaskItem:
        """Create a new task."""
        ...

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        ...


@runtime_checkable
class MessagingProvider(Protocol):
    """Protocol for communication channels: WhatsApp, Gmail, Slack."""
    provider_name: str

    def send_message(self, recipient: str, text: str) -> bool:
        """Send message after explicit approval."""
        ...

    def send_media(self, recipient: str, file_path: str, caption: str = "") -> bool:
        """Send media attachment after approval."""
        ...


@runtime_checkable
class DesktopProvider(Protocol):
    """Protocol for desktop OS automation: Windows Explorer, App launcher, Clipboard."""
    def find_files(self, pattern: str, directory: str | None = None) -> list[str]:
        """Find local files matching pattern in approved directories."""
        ...

    def read_document(self, path: str) -> str:
        """Extract text from local files (PDF, DOCX, TXT, MD)."""
        ...

    def open_application(self, app_name: str) -> bool:
        """Launch an allowlisted Windows application."""
        ...

    def read_clipboard(self) -> str:
        """Get current text from system clipboard."""
        ...

    def set_clipboard(self, text: str) -> bool:
        """Copy text to system clipboard."""
        ...
