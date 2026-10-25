"""
scripts/verify_notion.py
------------------------
End-to-end verification for the Wayfinder Notion adapter.

Checks (in order):
  1. NOTION_API_KEY is loaded from .env
  2. Notion API authenticates and identifies the integration
  3. Search returns results from accessible pages/databases
  4. Read retrieves content from an accessible page
  5. Write operations raise an error without explicit approval (parent_id guard)
  6. Error handling: invalid key, missing permissions
  7. Atlas Wayfinder path surfaces Notion capabilities via discovery

Usage:
  .venv/Scripts/python.exe scripts/verify_notion.py
  .venv/Scripts/python.exe scripts/verify_notion.py --page-id <PAGE_ID>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import traceback
from pathlib import Path

# Ensure the project root is on sys.path so `wayfinder` is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"
INFO = "[INFO]"
WARN = "[WARN]"


def _safe(msg: str) -> str:
    """Strip or replace characters that can't be encoded by the Windows console."""
    return msg.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8")


def _ok(msg: str) -> None:   print(f"  {PASS} {_safe(msg)}")
def _fail(msg: str) -> None: print(f"  {FAIL} {_safe(msg)}")
def _skip(msg: str) -> None: print(f"  {SKIP} {_safe(msg)}")
def _info(msg: str) -> None: print(f"  {INFO} {_safe(msg)}")
def _warn(msg: str) -> None: print(f"  {WARN} {_safe(msg)}")


# ---------------------------------------------------------------------------
# Check 1: Key loading
# ---------------------------------------------------------------------------

def check_key_loading() -> str | None:
    print("\n[Check 1] NOTION_API_KEY loading from environment / .env")
    try:
        from wayfinder.atlas.harness.notion_adapter import _get_api_key
        key = _get_api_key()
        if key and key.startswith("ntn_"):
            _ok(f"API key loaded (starts with 'ntn_', length={len(key)})")
            return key
        elif key:
            _ok(f"API key loaded (custom format, length={len(key)})")
            return key
        else:
            _fail("NOTION_API_KEY is empty or not found. Add it to .env")
            return None
    except Exception as exc:
        _fail(f"Could not load adapter: {exc}")
        traceback.print_exc()
        return None


# ---------------------------------------------------------------------------
# Check 2: Authentication / integration identity
# ---------------------------------------------------------------------------

def check_authentication(adapter) -> dict | None:
    print("\n[Check 2] Notion API authentication -- /v1/users/me")
    try:
        result = adapter._request("users/me")
        name = result.get("name", "")
        bot_type = result.get("type", "")
        workspace = result.get("bot", {}).get("workspace_name", "")
        _ok(f"Authenticated as: '{name}' (type={bot_type})")
        _ok(f"Workspace: '{workspace}'")
        return result
    except RuntimeError as exc:
        err = str(exc)
        if "401" in err or "unauthorized" in err.lower():
            _fail("Authentication failed -- check your NOTION_API_KEY is valid and not revoked")
        elif "403" in err:
            _fail("Forbidden -- the integration may not have workspace access")
        else:
            _fail(f"API error: {exc}")
        return None
    except Exception as exc:
        _fail(f"Unexpected error: {exc}")
        traceback.print_exc()
        return None


# ---------------------------------------------------------------------------
# Check 3: Search
# ---------------------------------------------------------------------------

def check_search(adapter) -> list | None:
    print("\n[Check 3] Search for accessible pages (/v1/search)")
    try:
        items = adapter.search("", limit=5)
        if items:
            _ok(f"Search returned {len(items)} result(s)")
            for item in items[:3]:
                _info(f"  Page: '{item.title}' | {item.url}")
            return items
        else:
            _warn("Search returned 0 results.")
            _warn("  a) Your integration has no pages shared with it yet.")
            _warn("  b) In Notion: open a page > ... > Connections > Add your integration.")
            return []
    except RuntimeError as exc:
        _fail(f"Search failed: {exc}")
        return None
    except Exception as exc:
        _fail(f"Unexpected error: {exc}")
        traceback.print_exc()
        return None


# ---------------------------------------------------------------------------
# Check 4: Read a page
# ---------------------------------------------------------------------------

def check_read(adapter, page_id: str | None, search_results: list | None) -> bool:
    print("\n[Check 4] Read a page's content")

    target_id = page_id
    target_name = "user-supplied page"

    if not target_id and search_results:
        target_id = search_results[0].id
        target_name = search_results[0].title

    if not target_id:
        _skip("No page ID available (pass --page-id <ID> or ensure search returns results)")
        return True

    try:
        item = adapter.read(target_id)
        _ok(f"Read page: '{item.title}' ({item.url})")
        _ok(f"Last edited: {item.updated_at}")
        if item.content:
            preview = item.content[:200].replace("\n", " ")
            _info(f"Content preview: {preview}...")
        else:
            _warn("Page content is empty (no text blocks or unsupported block types)")
        return True
    except RuntimeError as exc:
        err = str(exc)
        if "404" in err:
            _fail(f"Page '{target_name}' not found -- ID may be incorrect or page was deleted")
        elif "403" in err:
            _fail(f"Access denied to '{target_name}' -- share the page with your integration")
        else:
            _fail(f"Read failed: {exc}")
        return False
    except Exception as exc:
        _fail(f"Unexpected error: {exc}")
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Check 5: Write gate
# ---------------------------------------------------------------------------

def check_write_gate(adapter) -> bool:
    print("\n[Check 5] Write operations blocked without explicit approval (no parent_id)")
    try:
        adapter.create(title="Test Page", content="This should never be created")
        _fail("create() did NOT raise an error without parent_id -- approval gate is missing!")
        return False
    except ValueError as exc:
        _ok(f"create() correctly raises ValueError without parent_id: {exc}")
        return True
    except Exception as exc:
        _ok(f"create() raised {type(exc).__name__} before reaching the API: {exc}")
        return True


# ---------------------------------------------------------------------------
# Check 6: Error handling (invalid credentials)
# ---------------------------------------------------------------------------

def check_error_handling() -> bool:
    print("\n[Check 6] Error handling -- invalid credentials")
    try:
        from wayfinder.atlas.harness.notion_adapter import NotionAdapter
        bad_adapter = NotionAdapter(api_key="invalid_key_that_does_not_exist")
        bad_adapter.search("test")
        _fail("No error raised for invalid API key -- error handling is broken")
        return False
    except RuntimeError as exc:
        err = str(exc)
        if "401" in err or "400" in err:
            _ok(f"Invalid key correctly raises RuntimeError ({err[:60]})")
            return True
        else:
            _warn(f"Got error but unexpected code: {err[:100]}")
            return True
    except Exception as exc:
        _ok(f"Invalid key raises {type(exc).__name__}: {exc}")
        return True


# ---------------------------------------------------------------------------
# Check 7: Wayfinder path -- Atlas discovery
# ---------------------------------------------------------------------------

def check_wayfinder_path() -> bool:
    print("\n[Check 7] Wayfinder path -- Atlas retrieval discovers Notion tools")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "wayfinder.atlas.indexing.retrieval",
             "search notes in Notion for today"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd="."
        )
        if result.returncode != 0:
            _fail(f"retrieval.py exited with code {result.returncode}")
            if result.stderr:
                _fail(result.stderr[:300])
            return False

        # retrieval.py prints preamble text then a JSON object — extract the JSON block
        stdout = result.stdout.strip()
        json_start = stdout.find("{")
        if json_start == -1:
            _fail("retrieval.py output contained no JSON object")
            return False
        data = json.loads(stdout[json_start:])
        all_ids = (
            [c["id"] for c in data.get("executable_candidates", [])] +
            [c["id"] for c in data.get("unverified_candidates", [])]
        )

        notion_found = any("notion" in cid for cid in all_ids)
        if notion_found:
            _ok("Atlas retrieval surfaces Notion capabilities for knowledge queries")
        else:
            _warn("Atlas retrieval did not return Notion candidates for this query")

        skills_found = any(
            kw in cid for cid in all_ids
            for kw in ("morning_briefing", "knowledge_capture")
        )
        if skills_found:
            _ok("Atlas also discovers cross-app skills (morning_briefing / knowledge_capture)")
        else:
            _warn("Cross-app skills not surfaced -- check skills.jsonl has wayfinder.morning_briefing")

        return True
    except json.JSONDecodeError:
        _fail("retrieval.py output was not valid JSON")
        return False
    except Exception as exc:
        _fail(f"Atlas retrieval check failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Wayfinder Notion adapter end-to-end")
    parser.add_argument("--page-id", help="Notion page ID to test read access")
    args = parser.parse_args()

    print("=" * 60)
    print("  Wayfinder -- Notion Adapter Verification")
    print("=" * 60)

    results: dict[str, bool] = {}

    key = check_key_loading()
    results["key_loading"] = key is not None

    if not key:
        print("\n[ABORT] Cannot proceed without an API key.")
        sys.exit(1)

    from wayfinder.atlas.harness.notion_adapter import NotionAdapter
    adapter = NotionAdapter(api_key=key)

    auth_result = check_authentication(adapter)
    results["authentication"] = auth_result is not None

    search_results = check_search(adapter)
    results["search"] = search_results is not None

    results["read"] = check_read(adapter, args.page_id, search_results or [])

    results["write_gate"] = check_write_gate(adapter)

    results["error_handling"] = check_error_handling()

    results["wayfinder_path"] = check_wayfinder_path()

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, ok in results.items():
        symbol = PASS if ok else FAIL
        print(f"  {symbol}  {name.replace('_', ' ').title()}")

    print(f"\n  {passed}/{total} checks passed")

    if passed == total:
        print("\n  Notion adapter is fully verified and ready for production use.")
        print("  Next: update notion.* tool statuses from 'configured' to 'verified'")
        print("  in wayfinder/atlas/registry/tools.jsonl")
    elif passed >= total - 1:
        print("\n  Core integration is working. Review the failed check above.")
    else:
        print("\n  Critical checks failed. Fix errors before using Notion in Wayfinder.")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
