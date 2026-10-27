"""Explicit, bounded Google read qualification; report counts, never source content."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def qualify(client, args):
    start = datetime.now(timezone.utc)
    cases = [
        dict(
            service="calendar",
            resource="primary",
            time_min=start.isoformat(),
            time_max=(start + timedelta(days=1)).isoformat(),
        ),
        dict(service="tasks", resource="@default"),
        dict(service="gmail", resource="INBOX"),
    ]
    results = []
    for case in cases:
        before, grant = time.monotonic(), None
        try:
            grant = client.call("platform_google_grant", **args, **case, limit=3)
            response = client.call("platform_google_read", **args, grant=grant["id"])
            if (
                response.get("provider_live") is not True
                or response.get("external_writes") is not False
            ):
                raise ValueError("Read was not a live, read-only provider operation.")
            results.append(
                dict(
                    service=case["service"],
                    passed=True,
                    records=len(response["records"]),
                    possibly_truncated=response["possibly_truncated"],
                    elapsed_seconds=round(time.monotonic() - before, 3),
                )
            )
        except Exception:
            results.append(
                dict(
                    service=case["service"],
                    passed=False,
                    status="connection_or_read_unconfirmed",
                )
            )
        finally:
            if grant:
                try:
                    client.call("platform_google_revoke", **args, grant=grant["id"])
                except Exception:
                    pass
    return dict(
        tier="live_google_read",
        passed=all(r["passed"] for r in results),
        results=results,
        observed_at=datetime.now(timezone.utc).isoformat(),
        max_records_per_service=3,
        calendar_window_hours=24,
        account_writes=False,
        source_content_saved=False,
        native_ui=False,
        model_invocations=0,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Read up to three items from the primary calendar, default task list and Gmail INBOX. Calendar window: next 24 hours.",
    )
    args = parser.parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scripts.auth_google import check, helpers

    if not args.live:
        print(json.dumps(check(ROOT)))
        return 0
    helpers(ROOT)
    from wayfinder.api import Client, serve
    from wayfinder.service import AppService

    class NoMemory:
        def close(self):
            pass

    with tempfile.TemporaryDirectory(prefix="wayfinder-google-live-") as temporary:
        app = AppService(temporary, NoMemory())
        server = serve(app)
        try:
            client = Client(server.server_port, app.token)
            space = client.call("create_space", name="Google read qualification")["id"]
            report = qualify(
                client, dict(space=space, task="google-read-qualification")
            )
        finally:
            server.shutdown()
            server.server_close()
            app.close()
    destination = ROOT / ".local" / "verification" / "google-account-read.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
