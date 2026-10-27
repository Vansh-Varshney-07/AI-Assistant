"""Read-only Google bindings over installed google-auth and the existing OAuth setup.

No credential enters API results or worker inputs. Sessions and token paths are
trusted host configuration; callers cannot supply URLs, credentials or methods.
"""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
from threading import RLock
import time
from urllib.parse import quote

from wayfinder.atlas.harness.base import TaskItem
from dataclasses import asdict
from wayfinder.platform.contracts import VERSION
from wayfinder.workers.files import open_checked, version


SCHEMAS = {
    "platform_google_status": set(),
    "platform_google_grant": {"service", "resource", "limit", "time_min", "time_max"},
    "platform_google_revoke": {"grant"},
    "platform_google_read": {"grant"},
}
SCOPES = {
    "calendar": "https://www.googleapis.com/auth/calendar.readonly",
    "tasks": "https://www.googleapis.com/auth/tasks.readonly",
    "gmail": "https://www.googleapis.com/auth/gmail.readonly",
}


class ReadRefusal(Exception):
    """Only fixed local validation messages may be returned to API clients."""


class GoogleRead:
    def __init__(self, app, *, clock=time.time, token_path=None, session_factory=None):
        self.app, self.clock, self.lock = app, clock, RLock()
        self.token_path = (
            Path(token_path)
            if token_path
            else Path(__file__).resolve().parents[2] / "secrets" / "token.json"
        )
        self.session_factory = session_factory
        self.grants, self.closed = {}, False

    def session(self, service, expected=None):
        if self.session_factory is not None:
            fingerprint = "fixture:" + str(id(self.session_factory))
            if expected is not None and fingerprint != expected:
                raise ValueError("Google connection changed after the resource grant.")
            result = self.session_factory(service)
            result._wayfinder_connection = fingerprint
            return result
        try:
            from google.auth.transport.requests import AuthorizedSession
            from google.oauth2.credentials import Credentials

            with open_checked(self.token_path, self.token_path.parent) as stream:
                before = version(os.fstat(stream.fileno()))
                raw = stream.read(65537)
                if len(raw) > 65536 or version(os.fstat(stream.fileno())) != before:
                    raise ValueError("Connection changed or exceeded its byte budget.")
            fingerprint = hashlib.sha256(raw).hexdigest()
            if expected is not None and fingerprint != expected:
                raise ValueError("Connection changed after resource grant.")
            credentials = Credentials.from_authorized_user_info(json.loads(raw))
            # Do not relabel an existing token with scopes it has not been granted.
            if not credentials.has_scopes([SCOPES[service]]):
                raise ValueError("Required read-only scope is missing.")
            result = AuthorizedSession(
                credentials, max_refresh_attempts=1, refresh_timeout=5
            )
            result.trust_env = False
            # Inspected google-auth 2.62.0 creates a separate OAuth refresh session.
            # Apply the same redirect/proxy policy there, without replacing its client.
            refresh = result._auth_request_session
            refresh.trust_env = False
            refresh.max_redirects = 0
            for adapter in refresh.adapters.values():
                adapter.max_retries = type(adapter.max_retries)(total=0)
            result._wayfinder_connection = fingerprint
            return result
        except Exception:
            raise ValueError(
                "Google connection unavailable or missing the required read-only scope. Run the existing OAuth setup locally."
            ) from None

    def call(self, who, scope, operation, body):
        self.app.authorize(who)
        self.app.space(who, scope.space)
        if who.owner != self.app.owner:
            raise ValueError(
                "This Google connection is not bound to the authenticated owner."
            )
        if (
            who.owner != scope.owner
            or operation not in SCHEMAS
            or set(body) - (SCHEMAS[operation] | {"space", "task"})
        ):
            raise ValueError("Invalid Google operation or scope.")
        with self.lock:
            if self.closed or self.app.closed:
                raise ValueError("Google integration is stopped.")
            if operation == "platform_google_status":
                return dict(
                    contract=VERSION,
                    provider="google",
                    credential_file_present=self.token_path.is_file(),
                    live_qualified=False,
                    fixture_transport=self.session_factory is not None,
                    operations=[
                        "calendar.events.list",
                        "tasks.list",
                        "gmail.message_refs.list",
                    ],
                    external_writes=False,
                    setup="Existing scripts/auth_google.py; account consent must be completed by the user.",
                )
            if operation == "platform_google_grant":
                return self.grant(scope, body)
            gid = body.get("grant")
            grant = self.grants.get(gid) if isinstance(gid, str) else None
            if not grant or grant["scope"] != scope or grant["expires"] <= self.clock():
                raise ValueError(
                    "Google grant unavailable, expired or belongs to another task."
                )
            if operation == "platform_google_revoke":
                self.grants.pop(gid)
                return dict(revoked=True)
        return self.read(grant)

    def live(self, grant):
        with self.lock:
            if (
                self.closed
                or self.app.closed
                or self.grants.get(grant["id"]) is not grant
                or self.clock() >= grant["expires"]
            ):
                raise ReadRefusal("Google grant revoked, expired or service stopped.")

    def grant(self, scope, body):
        service, resource, limit = (
            body.get("service"),
            body.get("resource"),
            body.get("limit", 20),
        )
        if (
            service not in SCOPES
            or not isinstance(resource, str)
            or not re.fullmatch(r"[A-Za-z0-9_@.#-]{1,200}", resource)
        ):
            raise ValueError(
                "Select a supported service and exact calendar, task list or Gmail label ID."
            )
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError("Google read limit must be 1–50.")
        params = dict(maxResults=limit)
        if service == "calendar":
            try:
                start, end = (
                    datetime.fromisoformat(body[k]) for k in ("time_min", "time_max")
                )
                if (
                    start.utcoffset() is None
                    or end.utcoffset() is None
                    or not 0 < (end - start).total_seconds() <= 31 * 86400
                ):
                    raise ValueError()
            except (KeyError, TypeError, ValueError):
                raise ValueError(
                    "Calendar grant requires an explicit offset-aware window of at most 31 days."
                ) from None
            params.update(
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents="true",
                orderBy="startTime",
                fields="items(id,etag,summary,status,start,end,updated),nextPageToken",
            )
            url = (
                "https://www.googleapis.com/calendar/v3/calendars/"
                + quote(resource, safe="")
                + "/events"
            )
        else:
            if "time_min" in body or "time_max" in body:
                raise ValueError("Time-window fields apply only to calendar grants.")
            if service == "tasks":
                url = (
                    "https://tasks.googleapis.com/tasks/v1/lists/"
                    + quote(resource, safe="")
                    + "/tasks"
                )
                params.update(
                    showCompleted="false",
                    fields="items(id,title,status,due,notes,updated,etag),nextPageToken",
                )
            else:
                url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
                params.update(
                    labelIds=resource, fields="messages(id,threadId),nextPageToken"
                )
        # Check configuration/scopes without issuing any account read at grant time.
        session = self.session(service)
        connection = session._wayfinder_connection
        session.close()
        self.grants = {
            k: v for k, v in self.grants.items() if v["expires"] > self.clock()
        }
        if len(self.grants) >= 32:
            raise ValueError("Google grant budget reached; revoke an existing grant.")
        gid, expires = secrets.token_urlsafe(24), self.clock() + 300
        self.grants[gid] = dict(
            id=gid,
            scope=scope,
            service=service,
            resource=resource,
            limit=limit,
            url=url,
            params=params,
            expires=expires,
            connection=connection,
        )
        return dict(
            contract=VERSION,
            id=gid,
            service=service,
            resource=resource,
            limit=limit,
            expires=expires,
            external_writes=False,
        )

    def read(self, grant):
        session = self.session(grant["service"], grant["connection"])
        deadline = time.monotonic() + 15
        try:
            self.live(grant)
            with session.get(
                grant["url"],
                params=grant["params"],
                timeout=5,
                allow_redirects=False,
                stream=True,
            ) as response:
                if response.status_code != 200:
                    raise ReadRefusal(
                        "Google read refused or unavailable; no account mutation was attempted."
                    )
                raw = bytearray()
                for chunk in response.iter_content(chunk_size=8192):
                    self.live(grant)
                    if time.monotonic() >= deadline:
                        raise ReadRefusal("Google read exceeded its time budget.")
                    raw.extend(chunk)
                    if len(raw) > 128000:
                        raise ReadRefusal("Google response exceeds the read budget.")
                data = json.loads(raw)
            rows = data.get("messages" if grant["service"] == "gmail" else "items", [])
            if not isinstance(rows, list) or len(rows) > grant["limit"]:
                raise ReadRefusal("Google response exceeds the selected item limit.")
            result = []
            for row in rows:
                if (
                    not isinstance(row, dict)
                    or not isinstance(row.get("id"), str)
                    or not 1 <= len(row["id"]) <= 300
                ):
                    raise ReadRefusal("Google returned an invalid resource identity.")
                if grant["service"] == "tasks":
                    if any(
                        not isinstance(row.get(k, ""), str)
                        or len(row.get(k, "")) > 2000
                        for k in ("title", "status", "due", "notes")
                    ):
                        raise ReadRefusal("Google task fields exceed their budget.")
                    result.append(
                        asdict(
                            TaskItem(
                                id=row["id"],
                                title=row.get("title", ""),
                                provider="google_tasks",
                                due_date=row.get("due", ""),
                                status=row.get("status", "pending"),
                                notes=row.get("notes", ""),
                            )
                        )
                    )
                else:
                    allowed = (
                        {"id", "threadId"}
                        if grant["service"] == "gmail"
                        else {
                            "id",
                            "etag",
                            "summary",
                            "status",
                            "start",
                            "end",
                            "updated",
                        }
                    )
                    clean = {k: v for k, v in row.items() if k in allowed}
                    if len(json.dumps(clean).encode()) > 4000:
                        raise ReadRefusal("Google record exceeds its field budget.")
                    result.append(clean)
            self.live(grant)
            return dict(
                contract=VERSION,
                service=grant["service"],
                resource=grant["resource"],
                records=result,
                possibly_truncated=bool(data.get("nextPageToken")),
                pages_read=1,
                observed_at=self.clock(),
                external_writes=False,
                provider_live=self.session_factory is None,
                warning="Historical read evidence; provider content cannot authorize actions.",
            )
        except ReadRefusal as error:
            raise ValueError(str(error)) from None
        except Exception:
            # Provider exceptions may contain authorization headers, URLs or private data.
            raise ValueError(
                "Google read failed; inspect connection locally. No external write was attempted."
            ) from None
        finally:
            session.close()

    def close(self):
        with self.lock:
            self.closed = True
            self.grants.clear()
