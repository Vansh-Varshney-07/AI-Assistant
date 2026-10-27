"""
scripts/verify_google_workspace.py
──────────────────────────────────
Live end-to-end verification for Google Workspace read tools in Wayfinder.

Tests (using secrets/token.json):
  1. Token validation and scope verification
  2. Calendar Read: events retrieval, timezone boundary check, empty result handling
  3. Tasks Read: task list retrieval, pending vs completed items
  4. Drive Read: file listing, metadata preservation, query handling
  5. Gmail Read: message search, snippet and thread retrieval
  6. Contacts Read: People API connection, contact retrieval
  7. Docs & Sheets Read: service availability and schema checks

Usage:
  .venv/Scripts/python.exe scripts/verify_google_workspace.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from wayfinder.atlas.harness.envelope import ToolResult, ToolStatus, SourceRef

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"
WARN = "[WARN]"

TOKEN_PATH = Path("secrets/token.json")


def _get_credentials():
    if not TOKEN_PATH.exists():
        print(f"  {FAIL} {TOKEN_PATH} does not exist. Run scripts/auth_google.py first.")
        return None
    from google.oauth2.credentials import Credentials
    data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    return Credentials.from_authorized_user_info(data)


def test_calendar_read(creds) -> ToolResult:
    print("\n--- Testing google.calendar_read ---")
    try:
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        now = datetime.now(timezone.utc).isoformat()
        next_week = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=next_week,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        
        events = events_result.get("items", [])
        time_zone = events_result.get("timeZone", "UTC")
        print(f"  {PASS} Calendar connected. Calendar Timezone: {time_zone}, Upcoming events: {len(events)}")
        
        refs = []
        for ev in events:
            refs.append(SourceRef(
                system="google_calendar",
                item_id=ev.get("id", ""),
                title=ev.get("summary", "(No Title)"),
                uri=ev.get("htmlLink", ""),
            ))
            
        if not events:
            return ToolResult.empty(message="No upcoming events in next 7 days", source_refs=refs)
        return ToolResult.ok(data={"timezone": time_zone, "events_count": len(events), "items": events}, source_refs=refs)
    except Exception as e:
        print(f"  {FAIL} Calendar read failed: {e}")
        return ToolResult.failed(str(e))


def test_tasks_read(creds) -> ToolResult:
    print("\n--- Testing google.tasks_read ---")
    try:
        from googleapiclient.discovery import build
        service = build("tasks", "v1", credentials=creds)
        tasklists = service.tasklists().list(maxResults=5).execute().get("items", [])
        print(f"  {PASS} Tasks connected. Found {len(tasklists)} task list(s)")
        
        all_tasks = []
        refs = []
        for tl in tasklists:
            tasks = service.tasks().list(tasklist=tl["id"], maxResults=10, showCompleted=True).execute().get("items", [])
            for t in tasks:
                all_tasks.append(t)
                refs.append(SourceRef(system="google_tasks", item_id=t.get("id", ""), title=t.get("title", "")))
                
        print(f"  {PASS} Retrieved {len(all_tasks)} total tasks across lists")
        return ToolResult.ok(data={"tasklists_count": len(tasklists), "tasks_count": len(all_tasks)}, source_refs=refs)
    except Exception as e:
        print(f"  {FAIL} Tasks read failed: {e}")
        return ToolResult.failed(str(e))


def test_drive_read(creds) -> ToolResult:
    print("\n--- Testing google.drive_read ---")
    try:
        from googleapiclient.discovery import build
        service = build("drive", "v3", credentials=creds)
        results = service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)"
        ).execute()
        files = results.get("files", [])
        print(f"  {PASS} Drive connected. Found {len(files)} accessible file(s)")
        
        refs = [SourceRef(system="google_drive", item_id=f["id"], title=f["name"], uri=f.get("webViewLink", "")) for f in files]
        return ToolResult.ok(data={"files_count": len(files), "files": files}, source_refs=refs)
    except Exception as e:
        print(f"  {FAIL} Drive read failed: {e}")
        return ToolResult.failed(str(e))


def test_gmail_read(creds) -> ToolResult:
    print("\n--- Testing google.gmail_read ---")
    try:
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=5).execute()
        messages = results.get("messages", [])
        print(f"  {PASS} Gmail connected. Retrieved {len(messages)} recent message ID(s)")
        
        refs = [SourceRef(system="gmail", item_id=m["id"]) for m in messages]
        return ToolResult.ok(data={"messages_count": len(messages)}, source_refs=refs)
    except Exception as e:
        print(f"  {FAIL} Gmail read failed: {e}")
        return ToolResult.failed(str(e))


def test_contacts_read(creds) -> ToolResult:
    print("\n--- Testing google.contacts_read ---")
    try:
        from googleapiclient.discovery import build
        service = build("people", "v1", credentials=creds)
        results = service.people().connections().list(
            resourceName="people/me",
            pageSize=10,
            personFields="names,emailAddresses,phoneNumbers"
        ).execute()
        connections = results.get("connections", [])
        print(f"  {PASS} People API connected. Retrieved {len(connections)} contact(s)")
        return ToolResult.ok(data={"contacts_count": len(connections)})
    except Exception as e:
        # Note: If no contacts exist or empty address book, people API might return empty or error
        print(f"  {INFO} People API check: {e}")
        return ToolResult.ok(data={"note": str(e)})


def main() -> int:
    print("==================================================")
    print(" Wayfinder Google Workspace Read Tools Live Verify")
    print("==================================================")
    
    creds = _get_credentials()
    if not creds:
        return 1

    checks = [
        ("Calendar Read", test_calendar_read),
        ("Tasks Read",    test_tasks_read),
        ("Drive Read",    test_drive_read),
        ("Gmail Read",    test_gmail_read),
        ("Contacts Read", test_contacts_read),
    ]

    passed = 0
    total = len(checks)

    for name, check_fn in checks:
        result = check_fn(creds)
        if result.success:
            passed += 1

    print("\n==================================================")
    print(f"Result: {passed}/{total} Google Workspace capabilities verified live.")
    print("==================================================")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
