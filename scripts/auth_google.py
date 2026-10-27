"""User-run Google consent through the existing SDK; no automatic browser launch."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks.readonly",
]


class SetupError(ValueError):
    """A fixed local message safe to show without credential/provider details."""


def helpers(root):
    directory = root / ".local" / "google-oauth"
    if directory.is_dir() and str(directory) not in sys.path:
        sys.path.insert(0, str(directory))


def paths(root):
    return root / "secrets" / "credentials.json", root / "secrets" / "token.json"


def client_config(root):
    from wayfinder.workers.files import open_checked, version

    client, _ = paths(root)
    if not client.is_file():
        raise SetupError(
            "Save the downloaded Google Desktop OAuth client at secrets/credentials.json first."
        )
    try:
        with open_checked(client, client.parent) as stream:
            before = version(os.fstat(stream.fileno()))
            raw = stream.read(65537)
            if len(raw) > 65536 or version(os.fstat(stream.fileno())) != before:
                raise SetupError()
        value = json.loads(raw)
        installed = value["installed"]
        if (
            installed["auth_uri"]
            not in {
                "https://accounts.google.com/o/oauth2/auth",
                "https://accounts.google.com/o/oauth2/v2/auth",
            }
            or installed["token_uri"] != "https://oauth2.googleapis.com/token"
        ):
            raise SetupError()
        if any(
            not isinstance(installed.get(k), str) or not 0 < len(installed[k]) <= 2000
            for k in ("client_id", "client_secret")
        ):
            raise SetupError()
        return value
    except Exception:
        raise SetupError(
            "Invalid, redirected or unavailable Google Desktop OAuth configuration. Download a fresh Desktop client JSON from Google."
        ) from None


def check(root):
    helpers(root)
    client, token = paths(root)
    result = dict(
        providers=["Google Calendar", "Google Tasks", "Gmail"],
        fitness="deferred",
        oauth_helper_installed=importlib.util.find_spec("google_auth_oauthlib")
        is not None,
        client_file_present=client.is_file(),
        token_file_present=token.is_file(),
        scopes=SCOPES,
        account_reads=False,
        live_qualified=False,
    )
    if client.is_file():
        try:
            client_config(root)
            result["client_configuration_valid"] = True
        except ValueError:
            result["client_configuration_valid"] = False
    return result


def publish(root, value):
    from wayfinder.workers.files import checked_path

    client, token = paths(root)
    checked_path(client.parent)
    raw = json.dumps(value, allow_nan=False).encode("utf-8")
    if len(raw) > 65536:
        raise SetupError("Google returned an oversized token; nothing was saved.")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(token, flags, 0o600)
    created = os.fstat(fd)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        current = token.lstat()
        if (current.st_dev, current.st_ino) == (created.st_dev, created.st_ino):
            token.unlink()
        raise


def connect(root, *, flow_factory=None):
    from wayfinder.workers.files import checked_path

    client, token = paths(root)
    checked_path(root)
    if not client.parent.exists():
        client.parent.mkdir(mode=0o700)
    checked_path(client.parent)
    if os.path.lexists(token):
        raise SetupError(
            "A token already exists; it was preserved. Check the existing connection before requesting new consent."
        )
    config = client_config(root)
    if flow_factory is None:
        helpers(root)
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise SetupError(
                "Install the local OAuth helper with ops/Connect-Google.ps1 -Prepare first."
            ) from None
        flow_factory = InstalledAppFlow.from_client_config
    flow = flow_factory(config, SCOPES, autogenerate_code_verifier=True)
    session = flow.oauth2session
    session.trust_env, session.max_redirects = False, 0
    original = session.request

    def bounded_request(*args, **kwargs):
        kwargs.update(timeout=10, allow_redirects=False)
        return original(*args, **kwargs)

    session.request = bounded_request
    try:
        credentials = flow.run_local_server(
            host="127.0.0.1",
            bind_addr="127.0.0.1",
            port=0,
            open_browser=False,
            timeout_seconds=300,
            prompt="consent",
            access_type="offline",
            include_granted_scopes="false",
            authorization_prompt_message="Open this URL yourself to select your account and approve read-only access:\n{url}",
            success_message="Wayfinder consent received. You may close this browser tab.",
        )
        granted = credentials.granted_scopes
        if not credentials.has_scopes(SCOPES) or (
            granted is not None and not set(SCOPES) <= set(granted)
        ):
            raise SetupError(
                "Required read-only permissions were not all granted; no token was saved."
            )
        value = json.loads(credentials.to_json())
        if (
            not value.get("refresh_token")
            or value.get("token_uri") != "https://oauth2.googleapis.com/token"
        ):
            raise SetupError(
                "Google did not return a usable offline credential; no token was saved."
            )
        value["scopes"] = list(SCOPES)
        publish(root, value)
        return dict(
            connected=True,
            token_saved=True,
            scopes=SCOPES,
            account_reads=False,
            live_qualified=False,
        )
    finally:
        session.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check local setup only; no login, browser or account request.",
    )
    args = parser.parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        result = check(ROOT) if args.check else connect(ROOT)
        print(json.dumps(result))
        return 0
    except SetupError as error:
        print(str(error), file=sys.stderr)
        return 2
    except Exception:
        print(
            "Google consent did not finish or token publication failed. Existing credentials were preserved; no account-read success is claimed.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
