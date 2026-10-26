"""Real scoped local files; explicitly mocked Google HTTP transport. No account reads."""

import csv
import json
from pathlib import Path

import pytest

from wayfinder.api import Client, serve
from wayfinder.platform.activity import FIELDS
from wayfinder.platform.google_read import GoogleRead
from wayfinder.service import AppService, Identity


@pytest.fixture
def sources(tmp_path):
    class NoMemory:
        def close(self):
            pass

    app = AppService(tmp_path / "runtime", NoMemory())
    server = serve(app)
    client = Client(server.server_port, app.token)
    args = dict(
        space=client.call("create_space", name="Synthetic sources")["id"],
        task="source-test",
    )
    yield app, client, args, tmp_path
    server.shutdown()
    server.server_close()
    app.close()


def select(sources, rows=None):
    app, client, args, root = sources
    path = root / "activity.csv"
    if rows is None:
        path.write_bytes(
            (
                Path(__file__).parents[1]
                / "docs/personal-ai-companion/manual-test-kit/fitness-provider-a.csv"
            ).read_bytes()
        )
    else:
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    grant = client.call("worker_grant", **args, path=str(path))
    ref = client.call("worker_search", **args, grant=grant["id"])["files"][0]["id"]
    return grant, ref, path


def row(**changes):
    return dict(
        dict(
            provider="fixture",
            record_id="one",
            revision=1,
            metric="steps",
            value=4000,
            unit="count",
            start_time="2026-10-12T00:00:00+05:30",
            end_time="2026-10-13T00:00:00+05:30",
            timezone="Asia/Kolkata",
        ),
        **changes,
    )


def test_actual_activity_csv_uses_granted_source_and_provenance(sources):
    _, client, args, _ = sources
    _, ref, _ = select(sources)
    result = client.call("platform_activity_read", **args, reference=ref)
    assert len(result["records"]) == 7
    assert {s["metric"]: s["total"] for s in result["summaries"]} == {
        "steps": 30000,
        "workout_duration": 60,
    }
    assert len(result["source"]["sha256"]) == 64
    assert result["memory_written"] is False and result["provider_live"] is False


@pytest.mark.parametrize(
    "changes",
    [
        dict(value="NaN"),
        dict(value=-1),
        dict(value=1.5),
        dict(unit="minute"),
        dict(timezone="Unknown/Zone"),
        dict(start_time="2026-10-12T00:00:00"),
        dict(start_time="2026-10-12T00:00:00+00:00"),
        dict(end_time="2026-10-11T00:00:00+05:30"),
        dict(provider="=EXEC()"),
        dict(revision=0),
        dict(metric="medical_diagnosis"),
    ],
)
def test_invalid_activity_is_rejected(sources, changes):
    _, client, args, _ = sources
    _, ref, _ = select(sources, [row(**changes)])
    with pytest.raises(ValueError):
        client.call("platform_activity_read", **args, reference=ref)


def test_activity_duplicate_overlap_and_multiple_providers(sources):
    _, client, args, _ = sources
    _, ref, _ = select(sources, [row(), row(revision=2)])
    with pytest.raises(ValueError, match="Repeated"):
        client.call("platform_activity_read", **args, reference=ref)
    _, ref, _ = select(sources, [row(), row(record_id="two"), row(provider="second")])
    result = client.call("platform_activity_read", **args, reference=ref)
    assert result["summaries"][0]["total"] is None
    assert result["summaries"][1]["total"] == 4000
    assert any("cross-provider" in w for w in result["warnings"])


def test_activity_scopes_revocation_changed_file_and_budget(sources):
    app, client, args, _ = sources
    grant, ref, path = select(sources)
    with pytest.raises(ValueError):
        client.call("platform_activity_read", **dict(args, task="other"), reference=ref)
    with pytest.raises(ValueError):
        app.call(
            Identity(app.owner, "worker"),
            "platform_activity_read",
            dict(args, reference=ref),
        )
    client.call("worker_revoke", **args, grant=grant["id"])
    with pytest.raises(ValueError):
        client.call("platform_activity_read", **args, reference=ref)
    _, ref, path = select(sources)
    path.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError):
        client.call("platform_activity_read", **args, reference=ref)
    _, ref, _ = select(sources, [row(record_id="r" + str(i)) for i in range(367)])
    with pytest.raises(ValueError, match="budget"):
        client.call("platform_activity_read", **args, reference=ref)


class Response:
    def __init__(self, value, status=200):
        self.raw, self.status_code = json.dumps(value).encode(), status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def iter_content(self, **kwargs):
        yield self.raw


class Session:
    def __init__(self, output, calls):
        self.output, self.calls = output, calls

    def close(self):
        pass

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.output


def mock_google(sources, output):
    app, _, _, root = sources
    calls = []
    app.platform.google.close()
    app.platform.google = GoogleRead(
        app,
        token_path=root / "missing-token.json",
        session_factory=lambda service: Session(output, calls),
    )
    return app.platform.google, calls


@pytest.mark.parametrize(
    "service,resource,response",
    [
        (
            "calendar",
            "primary",
            {
                "items": [
                    {
                        "id": "event1",
                        "summary": "Synthetic event",
                        "start": {"dateTime": "2026-10-26T09:00:00Z"},
                        "private": "must not escape",
                    }
                ],
                "nextPageToken": "opaque",
            },
        ),
        (
            "tasks",
            "@default",
            {
                "items": [
                    {
                        "id": "task1",
                        "title": "Synthetic task",
                        "notes": "Source data, not instructions",
                    }
                ]
            },
        ),
        (
            "gmail",
            "INBOX",
            {
                "messages": [
                    {"id": "message1", "threadId": "thread1", "body": "must not escape"}
                ]
            },
        ),
    ],
)
def test_google_fixed_read_routes_with_mock_transport(
    sources, service, resource, response
):
    _, client, args, _ = sources
    _, calls = mock_google(sources, Response(response))
    extra = (
        dict(time_min="2026-10-26T00:00:00Z", time_max="2026-10-27T00:00:00Z")
        if service == "calendar"
        else {}
    )
    grant = client.call(
        "platform_google_grant", **args, service=service, resource=resource, **extra
    )
    assert calls == []
    result = client.call("platform_google_read", **args, grant=grant["id"])
    assert len(calls) == 1 and calls[0][1]["allow_redirects"] is False
    assert result["external_writes"] is False and result["provider_live"] is False
    assert "must not escape" not in json.dumps(result)
    assert result["records"][0]["id"] in {"event1", "task1", "message1"}
    assert client.call("platform_google_status", **args)["live_qualified"] is False


def test_google_scope_revoke_expiry_and_invalid_resource_denied_before_http(sources):
    app, client, args, _ = sources
    adapter, calls = mock_google(sources, Response({"items": []}))
    with pytest.raises(ValueError):
        client.call(
            "platform_google_grant",
            **args,
            service="tasks",
            resource="https://attacker.invalid",
        )
    with pytest.raises(ValueError):
        client.call(
            "platform_google_grant", **args, service="calendar", resource="primary"
        )
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )
    with pytest.raises(ValueError):
        client.call(
            "platform_google_read", **dict(args, task="other"), grant=grant["id"]
        )
    client.call("platform_google_revoke", **args, grant=grant["id"])
    with pytest.raises(ValueError):
        client.call("platform_google_read", **args, grant=grant["id"])
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )
    adapter.clock = lambda: grant["expires"] + 1
    with pytest.raises(ValueError):
        client.call("platform_google_read", **args, grant=grant["id"])
    assert calls == []
    with pytest.raises(ValueError):
        app.call(Identity(app.owner, "worker"), "platform_google_status", args)
    other = Identity("another-owner")
    other_space = app.call(
        other, "create_space", dict(name="Separate synthetic owner")
    )["id"]
    with pytest.raises(ValueError, match="authenticated owner"):
        app.call(
            other,
            "platform_google_grant",
            dict(
                space=other_space,
                task=args["task"],
                service="tasks",
                resource="@default",
            ),
        )


@pytest.mark.parametrize(
    "response",
    [
        Response({}, 302),
        Response({}, 401),
        Response({"items": "invalid"}),
        Response({"items": [{}]}),
        Response({"items": [{"id": "bad", "notes": "x" * 3000}]}),
        Response({"items": [], "padding": "x" * 128000}),
    ],
)
def test_google_refuses_redirects_failures_and_oversized_responses(sources, response):
    _, client, args, _ = sources
    mock_google(sources, response)
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )
    with pytest.raises(ValueError):
        client.call("platform_google_read", **args, grant=grant["id"])


def test_google_missing_connection_is_explicit_and_secrets_never_echo(sources):
    app, client, args, root = sources
    app.platform.google.token_path = root / "absent.json"
    assert (
        client.call("platform_google_status", **args)["credential_file_present"]
        is False
    )
    with pytest.raises(ValueError, match="connection unavailable"):
        client.call(
            "platform_google_grant", **args, service="tasks", resource="@default"
        )


def test_google_changed_connection_invalidates_existing_grant(sources):
    _, client, args, _ = sources
    adapter, calls = mock_google(sources, Response({"items": []}))
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )
    adapter.session_factory = lambda service: Session(Response({"items": []}), calls)
    with pytest.raises(ValueError, match="connection changed"):
        client.call("platform_google_read", **args, grant=grant["id"])
    assert calls == []


def test_google_real_credential_loader_checks_scopes_and_file_binding_without_network(
    sources, monkeypatch
):
    app, client, args, root = sources
    from google.auth.transport.requests import AuthorizedSession

    calls = []

    def forbidden(*values, **kwargs):
        calls.append(1)
        raise AssertionError("No network permitted in credential-loading tests")

    monkeypatch.setattr(AuthorizedSession, "get", forbidden)
    token = root / "synthetic-connection.json"
    info = dict(
        client_id="fixture",
        client_secret="synthetic-not-a-real-secret",
        refresh_token="synthetic-not-a-real-token",
        scopes=["https://www.googleapis.com/auth/tasks.readonly"],
    )
    token.write_text(json.dumps(info), encoding="utf-8")
    app.platform.google = GoogleRead(app, token_path=token)
    session = app.platform.google.session("tasks")
    assert session.trust_env is False
    assert session._auth_request_session.trust_env is False
    assert session._auth_request_session.max_redirects == 0
    assert all(
        a.max_retries.total == 0
        for a in session._auth_request_session.adapters.values()
    )
    session.close()
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )
    token.write_text(
        json.dumps(dict(info, refresh_token="different-synthetic-token")),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="connection unavailable"):
        client.call("platform_google_read", **args, grant=grant["id"])
    with pytest.raises(ValueError, match="connection unavailable"):
        client.call("platform_google_grant", **args, service="gmail", resource="INBOX")
    assert calls == []


def test_google_revocation_during_response_withholds_delivery(sources):
    _, client, args, _ = sources
    response = Response({"items": []})
    adapter, _ = mock_google(sources, response)
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )

    def revoke(**kwargs):
        client.call("platform_google_revoke", **args, grant=grant["id"])
        yield response.raw

    response.iter_content = revoke
    with pytest.raises(ValueError, match="revoked"):
        client.call("platform_google_read", **args, grant=grant["id"])


def test_google_transport_value_errors_never_echo_secrets(sources):
    _, client, args, _ = sources
    response = Response({"items": []})
    mock_google(sources, response)
    grant = client.call(
        "platform_google_grant", **args, service="tasks", resource="@default"
    )

    def fail(**kwargs):
        raise ValueError("SYNTHETIC-SECRET-MUST-NOT-ECHO")

    response.iter_content = fail
    with pytest.raises(ValueError) as error:
        client.call("platform_google_read", **args, grant=grant["id"])
    assert "SYNTHETIC-SECRET" not in str(error.value)
