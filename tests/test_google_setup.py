"""Consent setup fixtures; no browser, callback listener or Google network request."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import auth_google as setup


def configuration(root, **changes):
    folder = root / "secrets"
    folder.mkdir(exist_ok=True)
    value = dict(
        client_id="synthetic-client",
        client_secret="synthetic-secret",
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
    )
    value.update(changes)
    (folder / "credentials.json").write_text(
        json.dumps(dict(installed=value)), encoding="utf-8"
    )


class Credentials:
    granted_scopes = setup.SCOPES

    def has_scopes(self, scopes):
        return set(scopes) <= set(self.granted_scopes)

    def to_json(self):
        return json.dumps(
            dict(
                refresh_token="synthetic-token",
                token_uri="https://oauth2.googleapis.com/token",
                client_id="synthetic-client",
                client_secret="synthetic-secret",
            )
        )


class Session:
    def __init__(self):
        self.closed = False
        self.requests = []

    def request(self, *args, **kwargs):
        self.requests.append(kwargs)

    def close(self):
        self.closed = True


class Flow:
    def __init__(self):
        self.oauth2session = Session()
        self.options = None
        self.credentials = Credentials()

    def run_local_server(self, **kwargs):
        self.options = kwargs
        return self.credentials


def test_selected_scope_consent_is_manual_loopback_and_token_stays_private(tmp_path):
    configuration(tmp_path)
    flow = Flow()
    calls = []

    def factory(config, scopes, **kwargs):
        calls.append((scopes, kwargs))
        return flow

    result = setup.connect(tmp_path, flow_factory=factory)
    assert result["token_saved"] and result["account_reads"] is False
    assert flow.options["open_browser"] is False
    assert flow.options["host"] == flow.options["bind_addr"] == "127.0.0.1"
    assert flow.options["timeout_seconds"] == 300
    assert calls == [(setup.SCOPES, {"autogenerate_code_verifier": True})]
    assert len(setup.SCOPES) == 3 and all(s.endswith(".readonly") for s in setup.SCOPES)
    flow.oauth2session.request(
        "POST",
        "https://oauth2.googleapis.com/token",
        timeout=None,
        allow_redirects=True,
    )
    assert flow.oauth2session.requests == [dict(timeout=10, allow_redirects=False)]
    assert (
        flow.oauth2session.trust_env is False and flow.oauth2session.max_redirects == 0
    )
    assert flow.oauth2session.closed
    saved = json.loads((tmp_path / "secrets/token.json").read_text())
    assert saved["scopes"] == setup.SCOPES
    assert "synthetic-token" not in json.dumps(result)


def test_existing_token_is_not_overwritten_or_reauthorized(tmp_path):
    configuration(tmp_path)
    token = tmp_path / "secrets/token.json"
    token.write_text("existing synthetic token", encoding="utf-8")
    with pytest.raises(setup.SetupError, match="preserved"):
        setup.connect(
            tmp_path, flow_factory=lambda *a, **k: pytest.fail("Must not authorize")
        )
    with pytest.raises(FileExistsError):
        setup.publish(tmp_path, dict(refresh_token="new"))
    assert token.read_text() == "existing synthetic token"


@pytest.mark.parametrize(
    "changes",
    [
        dict(auth_uri="https://attacker.invalid/auth"),
        dict(token_uri="http://oauth2.googleapis.com/token"),
        dict(client_secret=""),
    ],
)
def test_bad_client_endpoints_are_rejected_before_oauth(tmp_path, changes):
    configuration(tmp_path, **changes)
    with pytest.raises(setup.SetupError, match="Invalid"):
        setup.connect(
            tmp_path, flow_factory=lambda *a, **k: pytest.fail("Must not authorize")
        )
    assert not (tmp_path / "secrets/token.json").exists()


def test_missing_client_is_actionable_without_starting_flow(tmp_path):
    with pytest.raises(setup.SetupError, match="credentials.json"):
        setup.connect(
            tmp_path, flow_factory=lambda *a, **k: pytest.fail("Must not authorize")
        )


def test_partial_consent_is_not_saved(tmp_path):
    configuration(tmp_path)
    flow = Flow()
    flow.credentials.granted_scopes = setup.SCOPES[:1]
    with pytest.raises(setup.SetupError, match="not all granted"):
        setup.connect(tmp_path, flow_factory=lambda *a, **k: flow)
    assert flow.oauth2session.closed
    assert not (tmp_path / "secrets/token.json").exists()


def test_provider_errors_are_sanitized_in_console(tmp_path, monkeypatch, capsys):
    configuration(tmp_path)
    monkeypatch.setattr(setup, "ROOT", tmp_path)

    def fail(root):
        raise ValueError("SYNTHETIC-TOKEN-MUST-NOT-ECHO")

    monkeypatch.setattr(setup, "connect", fail)
    assert setup.main([]) == 2
    assert "SYNTHETIC-TOKEN" not in capsys.readouterr().err


def test_module_import_and_check_do_not_start_authentication(tmp_path, monkeypatch):
    monkeypatch.setattr(setup, "ROOT", tmp_path)
    monkeypatch.setattr(
        setup, "connect", lambda *a: pytest.fail("Check cannot authorize")
    )
    assert setup.main(["--check"]) == 0
    result = subprocess.run(
        [sys.executable, "-c", "from scripts import auth_google; print('import-only')"],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0 and result.stdout.strip() == "import-only"


def test_installed_sdk_accepts_pkce_configuration_without_network():
    root = Path(__file__).parents[1]
    source = """import sys,inspect,json
sys.path.insert(0,'.local/google-oauth')
from google_auth_oauthlib.flow import InstalledAppFlow
from scripts.auth_google import SCOPES
flow=InstalledAppFlow.from_client_config({'installed':{'client_id':'synthetic','client_secret':'synthetic','auth_uri':'https://accounts.google.com/o/oauth2/auth','token_uri':'https://oauth2.googleapis.com/token'}},SCOPES,autogenerate_code_verifier=True)
flow.redirect_uri='http://127.0.0.1:12345/'
url,state=flow.authorization_url()
assert 'code_challenge=' in url and state
assert 'open_browser' in inspect.signature(flow.run_local_server).parameters
flow.oauth2session.close()
print('SDK PKCE configuration verified without network')
"""
    if not (root / ".local/google-oauth/google_auth_oauthlib").exists():
        pytest.skip("Local optional OAuth SDK not prepared")
    result = subprocess.run(
        [sys.executable, "-c", source],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, "Installed OAuth SDK configuration check failed"


def test_read_qualification_is_bounded_revokes_grants_and_omits_source_content():
    from scripts.test_google_connection import qualify

    class Client:
        def __init__(self):
            self.calls = []

        def call(self, operation, **body):
            self.calls.append((operation, body))
            if operation == "platform_google_grant":
                assert body["limit"] == 3
                return dict(id=body["service"])
            if operation == "platform_google_read":
                return dict(
                    provider_live=True,
                    external_writes=False,
                    possibly_truncated=False,
                    records=[dict(title="PRIVATE-SOURCE-MUST-NOT-APPEAR-IN-REPORT")],
                )
            return dict(revoked=True)

    client = Client()
    result = qualify(client, dict(space="fixture", task="fixture"))
    assert result["passed"] and result["calendar_window_hours"] == 24
    assert "PRIVATE-SOURCE" not in json.dumps(result)
    assert [b["grant"] for op, b in client.calls if op == "platform_google_revoke"] == [
        "calendar",
        "tasks",
        "gmail",
    ]


def test_failed_account_read_is_reported_without_provider_error_or_success_claim():
    from scripts.test_google_connection import qualify

    class Client:
        def call(self, *args, **kwargs):
            raise ValueError("PRIVATE-PROVIDER-DETAIL")

    result = qualify(Client(), dict(space="fixture", task="fixture"))
    assert result["passed"] is False
    assert len(result["results"]) == 3
    assert "PRIVATE-PROVIDER" not in json.dumps(result)
