"""
wayfinder/atlas/harness
───────────────────────
General-purpose application harnesses and provider adapters.
"""

from wayfinder.atlas.harness.base import (
    KnowledgeItem,
    KnowledgeProvider,
    TaskItem,
    TaskProvider,
    MessageItem,
    MessagingProvider,
    DesktopProvider,
)
from wayfinder.atlas.harness.notion_adapter import NotionAdapter
from wayfinder.atlas.harness.desktop_adapter import DesktopAdapter

__all__ = [
    "KnowledgeItem",
    "KnowledgeProvider",
    "TaskItem",
    "TaskProvider",
    "MessageItem",
    "MessagingProvider",
    "DesktopProvider",
    "NotionAdapter",
    "DesktopAdapter",
]
