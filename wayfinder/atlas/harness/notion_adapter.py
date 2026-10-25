"""
wayfinder/atlas/harness/notion_adapter.py
─────────────────────────────────────────
Implements KnowledgeProvider for Notion using the Notion REST API.

Authentication:
  Configured via NOTION_API_KEY in .env.
  Integration token from: https://www.notion.so/my-integrations

Design:
  Uses lightweight HTTP requests (requests / urllib) adhering to standard
  Notion API version 2022-06-28. Translates Notion pages and block hierarchies
  into standardized KnowledgeItem models.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any
from pathlib import Path

from wayfinder.atlas.harness.base import KnowledgeItem, KnowledgeProvider

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"


def _get_api_key() -> str:
    # Check environment variable or read from .env directly
    key = os.environ.get("NOTION_API_KEY")
    if not key:
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("NOTION_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return key or ""


class NotionAdapter(KnowledgeProvider):
    provider_name: str = "notion"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or _get_api_key()

    def _request(self, endpoint: str, method: str = "GET", data: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("NOTION_API_KEY is not set. Add it to .env or pass to NotionAdapter.")

        url = f"{NOTION_BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            raise RuntimeError(f"Notion API error ({exc.code}): {err_body}")

    def search(self, query: str, limit: int = 5) -> list[KnowledgeItem]:
        payload: dict[str, Any] = {
            "query": query,
            "page_size": limit,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        }
        res = self._request("search", method="POST", data=payload)
        items: list[KnowledgeItem] = []

        for result in res.get("results", []):
            item_id = result.get("id", "")
            title = "Untitled"
            props = result.get("properties", {})
            # Extract page title
            for prop in props.values():
                if prop.get("type") == "title" and prop.get("title"):
                    title = "".join(t.get("plain_text", "") for t in prop["title"])
                    break

            items.append(KnowledgeItem(
                id=item_id,
                title=title,
                content="",  # fetched on demand via read()
                provider="notion",
                url=result.get("url", ""),
                updated_at=result.get("last_edited_time", ""),
                metadata={"object": result.get("object", "page")},
            ))

        return items

    def read(self, item_id: str) -> KnowledgeItem:
        # 1. Get page metadata
        page = self._request(f"pages/{item_id}")
        title = "Untitled"
        for prop in page.get("properties", {}).values():
            if prop.get("type") == "title" and prop.get("title"):
                title = "".join(t.get("plain_text", "") for t in prop["title"])
                break

        # 2. Get children blocks (content)
        blocks = self._request(f"blocks/{item_id}/children")
        lines: list[str] = []

        for b in blocks.get("results", []):
            b_type = b.get("type", "")
            data = b.get(b_type, {})
            rich_text = data.get("rich_text", [])
            text = "".join(t.get("plain_text", "") for t in rich_text)

            if b_type.startswith("heading_"):
                level = b_type.split("_")[1]
                lines.append(f"{'#' * int(level)} {text}")
            elif b_type == "bulleted_list_item":
                lines.append(f"- {text}")
            elif b_type == "numbered_list_item":
                lines.append(f"1. {text}")
            elif b_type == "to_do":
                checked = "x" if data.get("checked") else " "
                lines.append(f"- [{checked}] {text}")
            elif b_type == "code":
                lines.append(f"```{data.get('language', '')}\n{text}\n```")
            elif text:
                lines.append(text)

        content = "\n\n".join(lines)
        return KnowledgeItem(
            id=item_id,
            title=title,
            content=content,
            provider="notion",
            url=page.get("url", ""),
            updated_at=page.get("last_edited_time", ""),
            metadata={"archived": page.get("archived", False)},
        )

    def create(self, title: str, content: str, parent_id: str | None = None) -> KnowledgeItem:
        if not parent_id:
            raise ValueError("parent_id (Page ID or Database ID) is required to create a Notion page.")

        payload = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": [{"text": {"content": title}}]
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]
        }
        res = self._request("pages", method="POST", data=payload)
        return KnowledgeItem(
            id=res.get("id", ""),
            title=title,
            content=content,
            provider="notion",
            url=res.get("url", ""),
            updated_at=res.get("created_time", ""),
        )

    def update(self, item_id: str, content: str) -> KnowledgeItem:
        # Append content as a new block to the existing page
        payload = {
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]
        }
        self._request(f"blocks/{item_id}/children", method="PATCH", data=payload)
        return self.read(item_id)
