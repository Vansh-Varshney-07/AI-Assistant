"""Real Git in generated repositories; no project refs, remote writes or native UI."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from wayfinder.api import Client, serve
from wayfinder.platform.connectors import ConnectorService
from wayfinder.platform.git_connector import GitPlan
from wayfinder.service import AppService, Identity
from wayfinder.workers.actions import ActionGate


def git(root, *args, accepted=(0,)):
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_SYSTEM=os.devnull,
    )
    result = subprocess.run(
        [
            shutil.which("git"),
            "--no-pager",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "user.name=Synthetic Test",
            "-c",
            "user.email=fixture@localhost",
            "-C",
            str(root),
            *args,
        ],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    assert result.returncode in accepted, result.stderr
    return result.stdout.strip()


def repository(path):
    path.mkdir()
    git(path, "init", "--quiet", "--initial-branch=main", "--template=")
    git(path, "commit", "--quiet", "--allow-empty", "-m", "Synthetic base only")
    return path


@pytest.fixture
def connector(tmp_path):
    if not shutil.which("git"):
        pytest.skip("Installed Git required")

    class NoMemory:
        def close(self):
            pass

    app = AppService(tmp_path / "app", NoMemory())
    server = serve(app)
    client = Client(server.server_port, app.token)
    args = dict(
        space=client.call("create_space", name="Synthetic Git qualification")["id"],
        task="bounded-git-test",
    )
    root = repository(tmp_path / "synthetic_repo")
    grant = client.call("platform_git_grant", **args, path=str(root))
    fixture = dict(
        app=app,
        client=client,
        args=args,
        root=root,
        grant=grant,
        port=server.server_port,
    )
    yield fixture
    server.shutdown()
    server.server_close()
    app.close()


def call(fixture, operation, **body):
    return fixture["client"].call(operation, **fixture["args"], **body)


def propose(fixture, request="branch-1", branch="refs/heads/codex/synthetic-handoff"):
    return call(
        fixture,
        "platform_git_propose",
        grant=fixture["grant"]["id"],
        branch=branch,
        expected_head=fixture["grant"]["head"],
        request_id=request,
    )


def approve(fixture, action, value=True, **extra):
    return call(
        fixture,
        "platform_action_decide",
        id=action["id"],
        digest=action["digest"],
        approve=value,
        **extra,
    )


def ref(fixture, branch="refs/heads/codex/synthetic-handoff"):
    return git(
        fixture["root"], "show-ref", "--verify", "--hash", branch, accepted=(0, 1, 128)
    )


def test_real_branch_write_requires_exact_approval_and_independent_receipt(connector):
    action = propose(connector)
    assert GitPlan.model_validate(action["plan"]).repository_identity
    assert action["status"] == "pending" and not ref(connector)
    result = approve(connector, action)
    assert result["status"] == "completed", result
    assert result["result"]["verified"] is True
    assert ref(connector) == connector["grant"]["head"]
    # Independent Git calls, outside the connector/gate, confirm target and receipt.
    log = git(
        connector["root"],
        "reflog",
        "show",
        "-1",
        "--format=%H %gs",
        action["plan"]["branch"],
    )
    assert log == connector["grant"]["head"] + " wayfinder:" + action["plan"]["nonce"]
    assert git(connector["root"], "branch", "--show-current") == "main"
    assert git(connector["root"], "rev-parse", "HEAD") == connector["grant"]["head"]
    audit = call(connector, "platform_action_audit", id=action["id"])
    assert [row["event"] for row in audit] == ["pending", "completed"]
    report = dict(
        tier="real_git_provider_synthetic_repository",
        git_version=git(connector["root"], "--version"),
        passed=True,
        action=result,
        independent_ref=ref(connector),
        independent_reflog=log,
        checkout_changed=False,
        remote_write=False,
        native_ui=False,
    )
    path = (
        Path(__file__).resolve().parents[1] / ".local/verification/git-connector.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def test_duplicate_submission_and_approval_dispatch_once(connector):
    with ThreadPoolExecutor(max_workers=2) as pool:
        actions = list(pool.map(lambda _: propose(connector), range(2)))
    assert actions[0]["id"] == actions[1]["id"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: approve(connector, actions[0]), range(2)))
    assert all(row["status"] == "completed" for row in results)
    assert connector["app"].platform.connectors.git.dispatches == 1
    with pytest.raises(ValueError, match="immutable"):
        propose(connector, branch="refs/heads/codex/changed-input")


@pytest.mark.parametrize(
    "case", ["reject", "expire", "revoke", "grant_revoke", "grant_expire", "stale_head"]
)
def test_denials_produce_no_branch(connector, case):
    action = propose(connector)
    service = connector["app"].platform.connectors
    if case == "reject":
        result = approve(connector, action, False)
    else:
        if case == "expire":
            service.actions.clock = lambda: action["expires"] + 1
        elif case == "revoke":
            call(connector, "platform_action_revoke", id=action["id"])
        elif case == "grant_revoke":
            call(connector, "platform_git_revoke", grant=connector["grant"]["id"])
        elif case == "grant_expire":
            service.git.clock = lambda: connector["grant"]["expires"] + 1
        else:
            git(
                connector["root"],
                "commit",
                "--quiet",
                "--allow-empty",
                "-m",
                "Changed synthetic HEAD",
            )
        result = approve(connector, action)
    expected = dict(
        reject="rejected",
        expire="expired",
        revoke="revoked",
        grant_revoke="revoked",
        grant_expire="failed",
        stale_head="failed",
    )
    assert result["status"] == expected[case]
    assert service.git.dispatches == 0
    assert not ref(connector)


def test_changed_review_digest_and_tampered_payload_are_denied(connector):
    action = propose(connector)
    with pytest.raises(ValueError, match="digest"):
        call(
            connector,
            "platform_action_decide",
            id=action["id"],
            digest="0" * 64,
            approve=True,
        )
    service = connector["app"].platform.connectors
    body = dict(action["plan"], branch="refs/heads/codex/tampered")
    with connector["app"].db() as db:
        db.execute(
            "UPDATE connector_actions SET body=? WHERE id=?",
            (json.dumps(body), action["id"]),
        )
    with pytest.raises(ValueError, match="digest"):
        approve(connector, action)
    assert service.git.dispatches == 0 and not ref(connector)
    assert (
        call(connector, "platform_action_audit", id=action["id"])[-1]["event"]
        == "decision_failed"
    )


def test_worker_and_cross_task_access_cannot_mint_grants_or_approve(connector):
    app = connector["app"]
    app.credentials["synthetic-worker-token"] = Identity(app.owner, "worker")
    client = Client(connector["port"], "synthetic-worker-token")
    with pytest.raises(ValueError, match="orchestrator"):
        client.call(
            "platform_git_grant", **connector["args"], path=str(connector["root"])
        )
    action = propose(connector)
    with pytest.raises(ValueError, match="orchestrator"):
        client.call(
            "platform_action_decide",
            **connector["args"],
            id=action["id"],
            digest=action["digest"],
            approve=True,
        )
    foreign = dict(connector["args"], task="foreign-task")
    with pytest.raises(ValueError, match="unavailable"):
        connector["client"].call("platform_action_result", **foreign, id=action["id"])
    with pytest.raises(ValueError, match="another task"):
        connector["client"].call(
            "platform_git_observe",
            **foreign,
            grant=connector["grant"]["id"],
            branch=action["plan"]["branch"],
        )
    assert not ref(connector)


@pytest.mark.parametrize(
    "branch",
    [
        "refs/heads/main",
        "refs/heads/codex/../escape",
        "refs/heads/codex/x\ncreate refs/heads/main deadbeef",
        "--help",
    ],
)
def test_branch_injection_and_unbounded_targets_are_rejected(connector, branch):
    with pytest.raises(ValueError):
        propose(connector, branch=branch)
    assert connector["app"].platform.connectors.git.dispatches == 0


def test_existing_branch_is_never_overwritten(connector):
    action = propose(connector)
    assert approve(connector, action)["status"] == "completed"
    with pytest.raises(ValueError, match="already exists"):
        propose(connector, request="second-action")
    assert connector["app"].platform.connectors.git.dispatches == 1


def test_untrusted_reference_transaction_hook_is_disabled(connector):
    hooks = connector["root"] / ".git/hooks"
    hooks.mkdir(exist_ok=True)
    hook = hooks / "reference-transaction"
    hook.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
    hook.chmod(0o755)
    git(connector["root"], "config", "core.hooksPath", str(hooks))
    action = propose(connector)
    assert approve(connector, action)["status"] == "completed"
    assert hook.read_text() == "#!/bin/sh\nexit 91\n"


@pytest.mark.parametrize(
    "redirect", ["include", "alternates", "linked_worktree", "private_root"]
)
def test_external_repository_redirects_are_refused_before_git_calls(
    connector, tmp_path, monkeypatch, redirect
):
    root = repository(tmp_path / "redirected_repo")
    if redirect == "include":
        with (root / ".git/config").open("a") as stream:
            stream.write("\n[include]\n\tpath = ../outside-config\n")
    elif redirect == "alternates":
        info = root / ".git/objects/info"
        info.mkdir(exist_ok=True)
        (info / "alternates").write_text(str(tmp_path / "outside-objects"))
    elif redirect == "linked_worktree":
        root = tmp_path / "fake_linked_worktree"
        root.mkdir()
        (root / ".git").write_text("gitdir: ../outside-metadata")
    else:
        root = repository(tmp_path / ".private_repo")

    def forbidden(*args, **kwargs):
        raise AssertionError("Git must not read redirected repository metadata")

    monkeypatch.setattr(connector["app"].platform.connectors.git, "_run", forbidden)
    with pytest.raises(ValueError):
        call(connector, "platform_git_grant", path=str(root))


def test_lost_acknowledgement_is_reconciled_without_replaying(connector, monkeypatch):
    service = connector["app"].platform.connectors
    original = service.git.perform

    def lost_ack(*args):
        original(*args)
        raise RuntimeError("Injected connection loss after the real Git write")

    monkeypatch.setattr(service.git, "perform", lost_ack)
    action = propose(connector)
    unknown = approve(connector, action)
    assert unknown["status"] == "outcome_unknown"
    assert ref(connector) == connector["grant"]["head"]
    assert approve(connector, action)["status"] == "outcome_unknown"
    assert service.git.dispatches == 1
    recovered = call(
        connector,
        "platform_action_reconcile",
        id=action["id"],
        grant=connector["grant"]["id"],
    )
    assert recovered["status"] == "completed"
    assert recovered["result"]["reconciled"] is True
    assert service.git.dispatches == 1


def test_git_transaction_rechecks_head_at_the_actual_write_boundary(
    connector, monkeypatch
):
    service = connector["app"].platform.connectors
    action = propose(connector)
    original = service.git._run

    def concurrent_change(root, args, **kwargs):
        if args[0] == "update-ref":
            git(
                root,
                "commit",
                "--quiet",
                "--allow-empty",
                "-m",
                "Concurrent synthetic change",
            )
        return original(root, args, **kwargs)

    monkeypatch.setattr(service.git, "_run", concurrent_change)
    result = approve(connector, action)
    assert result["status"] == "outcome_unknown"
    assert not ref(connector)
    observation = call(
        connector,
        "platform_action_reconcile",
        id=action["id"],
        grant=connector["grant"]["id"],
    )
    assert observation["status"] == "outcome_unknown"
    assert observation["reconciliation"]["verified"] is False
    assert service.git.dispatches == 1


def test_reconciliation_rejects_changed_approved_payload(connector, monkeypatch):
    service = connector["app"].platform.connectors
    original = service.git.perform

    def lost_ack(*args):
        original(*args)
        raise RuntimeError("Injected lost acknowledgement")

    monkeypatch.setattr(service.git, "perform", lost_ack)
    action = propose(connector)
    assert approve(connector, action)["status"] == "outcome_unknown"
    changed = dict(action["plan"], branch="refs/heads/codex/changed-reconciliation")
    with connector["app"].db() as db:
        db.execute(
            "UPDATE connector_actions SET body=? WHERE id=?",
            (json.dumps(changed), action["id"]),
        )

    def forbidden(*args):
        raise AssertionError("Changed payload must not reach provider reads")

    monkeypatch.setattr(service.git, "inspect_outcome", forbidden)
    with pytest.raises(ValueError, match="digest"):
        call(
            connector,
            "platform_action_reconcile",
            id=action["id"],
            grant=connector["grant"]["id"],
        )


def test_restart_expires_pending_and_requires_new_scope_grant_for_reconciliation(
    connector, monkeypatch
):
    service = connector["app"].platform.connectors
    pending = propose(connector, request="pending", branch="refs/heads/codex/pending")
    action = propose(connector)
    original = service.git.perform

    def lost_ack(*args):
        original(*args)
        raise RuntimeError("Injected interruption")

    monkeypatch.setattr(service.git, "perform", lost_ack)
    assert approve(connector, action)["status"] == "outcome_unknown"
    service.close()
    connector["app"].platform.connectors = ConnectorService(connector["app"])
    assert (
        call(connector, "platform_action_result", id=pending["id"])["status"]
        == "expired"
    )
    with pytest.raises(ValueError, match="expired"):
        call(
            connector,
            "platform_action_reconcile",
            id=action["id"],
            grant=connector["grant"]["id"],
        )
    fresh = call(connector, "platform_git_grant", path=str(connector["root"]))
    assert (
        call(
            connector, "platform_action_reconcile", id=action["id"], grant=fresh["id"]
        )["status"]
        == "completed"
    )
    assert connector["app"].platform.connectors.git.dispatches == 0


def test_an_unattributed_matching_ref_is_not_claimed_as_completion(connector):
    action = propose(connector)
    git(
        connector["root"],
        "update-ref",
        "--create-reflog",
        "-m",
        "Independent synthetic actor",
        action["plan"]["branch"],
        connector["grant"]["head"],
    )
    connector["app"].platform.connectors.actions._update(
        action["id"], "outcome_unknown"
    )
    result = call(
        connector,
        "platform_action_reconcile",
        id=action["id"],
        grant=connector["grant"]["id"],
    )
    assert result["status"] == "outcome_unknown"
    assert (
        result["reconciliation"]["observation"]
        == "desired_ref_present_but_unattributed"
    )


def test_action_store_identifier_is_trusted_configuration(connector):
    with pytest.raises(ValueError, match="trusted action store"):
        ActionGate(connector["app"].db, table="connector_actions; DROP TABLE spaces")


def test_expiry_after_observation_prevents_dispatch(connector, monkeypatch):
    action = propose(connector)
    service = connector["app"].platform.connectors
    now = [service.clock()]
    service.actions.clock = service.git.clock = lambda: now[0]
    original = service.git.observe

    def slow_observation(plan):
        state = original(plan)
        now[0] = action["expires"] + 1
        return state

    monkeypatch.setattr(service.git, "observe", slow_observation)
    assert approve(connector, action)["status"] == "expired"
    assert service.git.dispatches == 0
    assert not ref(connector)


def test_expiry_at_git_dispatch_prevents_provider_write(connector, monkeypatch):
    action = propose(connector)
    service = connector["app"].platform.connectors
    now = [service.clock()]
    service.actions.clock = service.git.clock = lambda: now[0]
    original = service.git._run

    def delayed_dispatch(root, args, **kwargs):
        if args[0] == "update-ref":
            now[0] = action["expires"] + 1
        return original(root, args, **kwargs)

    monkeypatch.setattr(service.git, "_run", delayed_dispatch)
    result = approve(connector, action)
    assert result["status"] == "outcome_unknown"
    assert result["result"]["failure"]["code"] == "approval_expired"
    assert service.git.dispatches == 0
    assert not ref(connector)


def test_approval_lifetime_is_bound_to_the_review_digest(connector):
    action = propose(connector)
    with connector["app"].db() as db:
        db.execute(
            "UPDATE connector_actions SET expires=? WHERE id=?",
            (action["expires"] + 999, action["id"]),
        )
    with pytest.raises(ValueError, match="digest"):
        approve(connector, action)
    assert connector["app"].platform.connectors.git.dispatches == 0
    assert not ref(connector)
