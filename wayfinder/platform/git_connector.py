"""Existing Git plumbing behind exact repository grants; no arbitrary commands."""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
from threading import RLock
import time

from pydantic import Field
from typing import Literal
from wayfinder.platform.contracts import Contract
from wayfinder.workers.files import (
    checked_path,
    open_checked,
    private,
    reparse,
    version,
)


class GitStep(Contract):
    action: Literal["git.create_branch"] = "git.create_branch"


class GitPlan(Contract):
    contract: Literal["wayfinder.platform/1"] = "wayfinder.platform/1"
    repository: str
    grant_ref: str
    repository_identity: list[str] = Field(min_length=2, max_length=2)
    git_identity: list[str] = Field(min_length=2, max_length=2)
    branch: str = Field(pattern=r"^refs/heads/codex/[A-Za-z0-9][A-Za-z0-9._/-]{0,120}$")
    expected_head: str = Field(pattern=r"^[a-f0-9]{40}$")
    nonce: str = Field(pattern=r"^[a-f0-9]{32}$")
    state: str = Field(pattern=r"^[a-f0-9]{64}$")
    steps: list[GitStep] = Field(min_length=1, max_length=1)


class GitFailure(RuntimeError):
    def __init__(self, code, message):
        self.failure_details = dict(
            tool="git.create_branch", code=code, message=message
        )
        super().__init__(message)


@dataclass
class RepositoryGrant:
    scope: tuple
    root: Path
    identity: tuple
    git_identity: tuple
    expires: float


class GitConnector:
    """Only new local branch refs. No checkout, commit, file editing or network."""

    def __init__(self, *, clock=time.time):
        self.clock, self.lock, self.grants = clock, RLock(), {}
        self.executable = shutil.which("git")
        self.available = bool(self.executable)
        self.dispatches = 0
        self.scope = None  # Invocation scope is bound by the trusted service.
        self.approval_expires = None

    def _layout(self, root):
        root = checked_path(root)
        if private(root):
            raise ValueError(
                "Private application and credential directories are unavailable."
            )
        gitdir = root / ".git"
        if not gitdir.is_dir() or reparse(gitdir.lstat()):
            raise ValueError(
                "Choose an ordinary repository with an in-place .git directory; linked worktrees are unsupported."
            )
        count, pending = 0, [(gitdir, 0)]
        while pending:
            directory, depth = pending.pop()
            if depth > 16:
                raise ValueError(
                    "Repository metadata exceeds the inspection depth budget."
                )
            with os.scandir(directory) as entries:
                for entry in entries:
                    count += 1
                    if count > 10000:
                        raise ValueError(
                            "Repository metadata exceeds the inspection entry budget."
                        )
                    info = entry.stat(follow_symlinks=False)
                    if reparse(info) or not (
                        stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
                    ):
                        raise ValueError(
                            "Repository metadata links, reparse points and special files are unsupported."
                        )
                    if stat.S_ISDIR(info.st_mode):
                        pending.append((Path(entry.path), depth + 1))
        for relative in (
            "commondir",
            "objects/info/alternates",
            "objects/info/http-alternates",
        ):
            if (gitdir / relative).exists():
                raise ValueError(
                    "Repository metadata must not redirect to external storage."
                )
        config = gitdir / "config"
        with open_checked(config, root) as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError("Repository configuration exceeds its read budget.")
        text = raw.decode("utf-8").lower().replace("\\\n", "")
        if re.search(r"\[\s*(include|includeif|extensions)\b", text) or re.search(
            r"^\s*worktree\s*=", text, re.M
        ):
            raise ValueError(
                "External includes, extensions and worktree redirects are unsupported."
            )
        return root, gitdir, hashlib.sha256(raw).hexdigest()

    def _run(self, root, args, *, input=None, accepted=(0,)):
        if not self.executable:
            raise ValueError("The installed Git executable is unavailable.")
        if args[0] not in {
            "rev-parse",
            "show-ref",
            "reflog",
            "check-ref-format",
            "update-ref",
        }:
            raise ValueError(
                "Git operation is not in the trusted connector's fixed command set."
            )
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
        env.update(
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_SYSTEM=os.devnull,
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_TERMINAL_PROMPT="0",
            GIT_OPTIONAL_LOCKS="0",
            GIT_NO_REPLACE_OBJECTS="1",
            GIT_ALLOW_PROTOCOL="",
        )
        command = [
            self.executable,
            "--no-pager",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "user.name=Wayfinder",
            "-c",
            "user.email=wayfinder@localhost",
            "--git-dir=" + str(root / ".git"),
            "--work-tree=" + str(root),
            *args,
        ]
        if args[0] == "update-ref":
            if (
                self.scope is None
                or self.approval_expires is None
                or self.clock() >= self.approval_expires
            ):
                raise GitFailure(
                    "approval_expired",
                    "No live trusted approval remains at the Git dispatch boundary.",
                )
            self.dispatches += 1
        result = subprocess.run(
            command,
            cwd=root,
            # update-ref's stdin protocol requires literal LF. Text-mode pipes
            # translate LF to CRLF on Windows, producing 'unknown command: start'.
            input=input.encode("utf-8") if input is not None else None,
            capture_output=True,
            timeout=10,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode not in accepted:
            raise GitFailure(
                "git_command_refused",
                f"Git {args[0]} exited with code {result.returncode}; no automatic retry. Reconcile any dispatched write.",
            )
        if len(result.stdout) > 12000:
            raise GitFailure(
                "git_response_too_large",
                "Git response exceeded its bounded output budget.",
            )
        return result.stdout.decode("utf-8").strip()

    def grant(self, scope, path):
        with self.lock:
            self.grants = {
                k: v for k, v in self.grants.items() if v.expires > self.clock()
            }
            if len(self.grants) >= 32:
                raise ValueError("Repository grant budget reached.")
            root, gitdir, _ = self._layout(path)
            head = self._run(root, ["rev-parse", "--verify", "HEAD^{commit}"])
            if not re.fullmatch(r"[a-f0-9]{40}", head):
                raise ValueError(
                    "This connector requires an initialized SHA-1 repository."
                )
            gid = secrets.token_urlsafe(24)
            self.grants[gid] = RepositoryGrant(
                tuple(scope),
                root,
                version(root.stat())[:2],
                version(gitdir.stat())[:2],
                self.clock() + 300,
            )
            return dict(
                id=gid,
                repository=str(root),
                expires=self.clock() + 300,
                access="create_new_codex_branch_only",
                head=head,
            )

    def get_grant(self, scope, gid):
        grant = self.grants.get(gid)
        if not grant or grant.scope != tuple(scope) or grant.expires <= self.clock():
            raise ValueError(
                "Repository grant expired, revoked or belongs to another task."
            )
        root, gitdir, config_hash = self._layout(grant.root)
        if (
            version(root.stat())[:2] != grant.identity
            or version(gitdir.stat())[:2] != grant.git_identity
        ):
            raise ValueError("Repository identity changed after grant.")
        return grant, config_hash

    def revoke(self, scope, gid):
        with self.lock:
            self.get_grant(scope, gid)
            del self.grants[gid]

    def snapshot(self, scope, gid, branch):
        with self.lock:
            if not re.fullmatch(
                r"refs/heads/codex/[A-Za-z0-9][A-Za-z0-9._/-]{0,120}", branch
            ):
                raise ValueError("Only a new refs/heads/codex/ branch is supported.")
            grant, config_hash = self.get_grant(scope, gid)
            self._run(grant.root, ["check-ref-format", branch])
            head = self._run(grant.root, ["rev-parse", "--verify", "HEAD^{commit}"])
            if not re.fullmatch(r"[a-f0-9]{40}", head):
                raise ValueError("HEAD is not an initialized SHA-1 commit.")
            target = self._run(
                grant.root,
                ["show-ref", "--verify", "--hash", branch],
                accepted=(0, 1, 128),
            )
            if not target and os.path.lexists(grant.root / ".git" / branch):
                raise ValueError(
                    "Destination ref exists but cannot be resolved safely."
                )
            payload = dict(
                repository=str(grant.root),
                identity=grant.identity,
                git_identity=grant.git_identity,
                config_hash=config_hash,
                head=head,
                target=target,
                branch=branch,
            )
            return dict(
                payload,
                state=hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest(),
            )

    def _bound(self, plan):
        if self.scope is None:
            raise ValueError("Trusted invocation scope is missing.")
        grant, _ = self.get_grant(self.scope, plan.grant_ref)
        if str(grant.root) != plan.repository:
            raise ValueError("Exact repository differs from the approved target.")
        if [str(v) for v in grant.identity] != plan.repository_identity or [
            str(v) for v in grant.git_identity
        ] != plan.git_identity:
            raise ValueError("Approved repository directory identity changed.")
        return grant

    def observe(self, plan):
        try:
            self._bound(plan)
            return self.snapshot(self.scope, plan.grant_ref, plan.branch)["state"]
        except ValueError as error:
            raise GitFailure("resource_or_state_unavailable", str(error)) from error

    @staticmethod
    def message(plan):
        return "wayfinder:" + plan.nonce

    def perform(self, plan, step, expected):
        with self.lock:
            grant = self._bound(plan)
            current = self.snapshot(self.scope, plan.grant_ref, plan.branch)
            if (
                current["state"] != expected
                or current["head"] != plan.expected_head
                or current["target"]
            ):
                raise ValueError(
                    "Repository changed or the destination ref already exists."
                )
            transaction = f"start\nverify HEAD {plan.expected_head}\ncreate {plan.branch} {plan.expected_head}\nprepare\ncommit\n"
            self._run(
                grant.root,
                ["update-ref", "--create-reflog", "-m", self.message(plan), "--stdin"],
                input=transaction,
            )
            return dict(
                state=self.snapshot(self.scope, plan.grant_ref, plan.branch)["state"],
                branch=plan.branch,
                head=plan.expected_head,
                nonce=plan.nonce,
            )

    def inspect_outcome(self, plan, scope, grant_ref):
        with self.lock:
            grant, _ = self.get_grant(scope, grant_ref)
            if str(grant.root) != plan.repository:
                raise ValueError("Reconciliation grant names a different repository.")
            if [str(v) for v in grant.identity] != plan.repository_identity or [
                str(v) for v in grant.git_identity
            ] != plan.git_identity:
                raise ValueError(
                    "Reconciliation requires the original repository identity."
                )
            current = self.snapshot(scope, grant_ref, plan.branch)
            if current["target"] != plan.expected_head:
                return dict(
                    verified=False,
                    observation="absent_or_different_target",
                    target=current["target"],
                )
            log = self._run(
                grant.root, ["reflog", "show", "-1", "--format=%H %gs", plan.branch]
            )
            matched = log == plan.expected_head + " " + self.message(plan)
            return dict(
                verified=matched,
                observation="attributed_ref_and_reflog"
                if matched
                else "desired_ref_present_but_unattributed",
                target=current["target"],
                nonce=plan.nonce if matched else None,
            )

    def verify(self, plan, receipts):
        return (
            len(receipts) == 1
            and self.inspect_outcome(plan, self.scope, plan.grant_ref)["verified"]
        )

    def close(self):
        with self.lock:
            self.grants.clear()
