"""Finite design models, not tests of an implemented desktop app or live provider.

Compare a deliberately permissive action model against proposed strict guards.
BFS returns shortest counterexamples; iterative DFS independently checks the same
reachable graph. No action is executed. All output stays in this audit folder.
"""

from collections import deque
from dataclasses import asdict, dataclass, field, replace
from itertools import combinations, permutations, product
import ast
import csv
import hashlib
import json
from pathlib import Path
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Action:
    phase: str = "proposed"
    account_b: bool = False
    expired: bool = False
    revoked: bool = False
    changed: bool = False
    cancelled: bool = False
    dispatches: int = 0
    effects: int = 0
    bad_dispatch: bool = False
    independent_verified: bool = False
    complete: bool = False
    unknown_seen: bool = False
    replayed_unknown: bool = False


def successors(s, hardened):
    # The reviewed proposal targets account A. Switching active UI account does
    # not rewrite it. Flags are monotone except the active account selection.
    yield "switch_active_account", replace(s, account_b=not s.account_b)
    if not s.expired:
        yield "approval_expires", replace(s, expired=True)
    if not s.revoked:
        yield "revoke", replace(s, revoked=True)
    if not s.cancelled:
        yield "cancel", replace(s, cancelled=True)
    if s.phase in {"proposed", "approved"} and not s.changed:
        yield "edit_proposed_payload", replace(s, changed=True)
    if s.phase == "proposed" and not (hardened and (s.expired or s.revoked or s.changed or s.cancelled)):
        yield "approve_original_proposal", replace(s, phase="approved")
    if s.phase == "proposed":
        yield "reject", replace(s, phase="rejected")
    if s.phase == "approved" and s.dispatches < 2:
        invalid = s.account_b or s.expired or s.revoked or s.changed or s.cancelled
        if not hardened or not invalid:
            yield "dispatch", replace(s, phase="inflight", dispatches=s.dispatches + 1,
                                      bad_dispatch=s.bad_dispatch or invalid,
                                      replayed_unknown=s.replayed_unknown or s.unknown_seen)
    # Effects can arrive after local connection loss; observing no acknowledgement
    # is not proof that the provider did nothing.
    if s.phase in {"inflight", "unknown", "acknowledged"} and s.effects < s.dispatches:
        yield "provider_applies", replace(s, effects=s.effects + 1)
    if s.phase == "inflight":
        yield "lose_acknowledgement", replace(s, phase="unknown", unknown_seen=True)
        if s.effects == s.dispatches:
            yield "receive_acknowledgement", replace(s, phase="acknowledged", complete=not hardened)
    if s.phase == "unknown" and not hardened and s.dispatches < 2:
        yield "ordinary_retry_same_action", replace(s, phase="approved")
    if s.phase in {"unknown", "acknowledged"} and s.effects == 1 and not s.bad_dispatch:
        if not hardened or not s.account_b:
            yield "independent_read_verifies_original_effect", replace(s, phase="verified", independent_verified=True, complete=True)
    if s.phase in {"proposed", "approved"}:
        yield "restart", replace(s, phase="expired")
    elif s.phase in {"inflight", "acknowledged"}:
        yield "restart", replace(s, phase="unknown", unknown_seen=True)


def violations(s):
    return [name for name, failed in {
        "dispatch_requires_current_exact_authorization": s.bad_dispatch,
        "same_action_id_has_at_most_one_effect": s.effects > 1,
        "uncertain_write_is_not_redispatched": s.replayed_unknown,
        "complete_requires_independent_verification": s.complete and not s.independent_verified,
    }.items() if failed]


def explore(hardened):
    initial = Action()
    q, parent, graph = deque([initial]), {initial: None}, {}
    witnesses, violating_states = {}, 0
    while q:
        current = q.popleft()
        failures = violations(current)
        violating_states += bool(failures)
        for name in failures:
            if name not in witnesses:
                trace, at = [], current
                while parent[at] is not None:
                    previous, event = parent[at]
                    trace.append(event)
                    at = previous
                witnesses[name] = list(reversed(trace))
        edges = list(successors(current, hardened))
        graph[current] = edges
        for event, nxt in edges:
            if nxt not in parent:
                parent[nxt] = (current, event)
                q.append(nxt)
    visited, stack, dfs_edges = set(), [initial], 0
    while stack:
        s = stack.pop()
        if s in visited:
            continue
        visited.add(s)
        dfs_edges += len(graph[s])
        stack.extend(nxt for _, nxt in reversed(graph[s]))
    assert visited == set(parent), "BFS and DFS disagree"
    return dict(states=len(parent), edges=sum(map(len, graph.values())),
                bfs_dfs_same_reachable_states=True, dfs_edges=dfs_edges,
                violating_states=violating_states, shortest_counterexamples=witnesses)


@dataclass(frozen=True)
class Chat:
    started: bool = False
    space_b: bool = False
    cancelled: bool = False
    last_sequence: int = 0
    finals: int = 0
    scope_leaked: bool = False
    resurrected: bool = False


def chat_edges(s, strict):
    yield "switch_visible_space", replace(s, space_b=not s.space_b)
    if not s.started:
        yield "submit_in_space_A", replace(s, started=True)
        return
    if not s.cancelled and not s.finals:
        yield "server_confirms_cancel", replace(s, cancelled=True, last_sequence=2 if strict else s.last_sequence)
    # Duplicate/late transport frames are deliberately allowed as fault inputs.
    if not strict or not s.cancelled:
        if not strict or s.last_sequence < 1:
            yield "delta_1_for_space_A", replace(s, last_sequence=max(1, s.last_sequence),
                                                scope_leaked=s.scope_leaked or (s.space_b and not strict))
        if s.finals < 2 and (not strict or s.last_sequence < 2):
            yield "complete_2_for_space_A", replace(s, last_sequence=2, finals=s.finals + 1,
                                                   scope_leaked=s.scope_leaked or (s.space_b and not strict),
                                                   resurrected=s.resurrected or s.cancelled)


def explore_chat(strict):
    initial = Chat()
    queue, parents, graph, witnesses = deque([initial]), {initial: None}, {}, {}
    while queue:
        s = queue.popleft()
        for name, bad in {"scope_safe_delivery": s.scope_leaked,
                          "terminal_cancel_not_resurrected": s.resurrected,
                          "duplicate_final_not_published": s.finals > 1}.items():
            if bad and name not in witnesses:
                trace, at = [], s
                while parents[at]:
                    previous, event = parents[at]
                    trace.append(event)
                    at = previous
                witnesses[name] = list(reversed(trace))
        graph[s] = list(chat_edges(s, strict))
        for event, nxt in graph[s]:
            if nxt not in parents:
                parents[nxt] = (s, event)
                queue.append(nxt)
    stack, seen = [initial], set()
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        stack.extend(nxt for _, nxt in graph[s])
    assert seen == set(parents)
    return dict(states=len(seen), edges=sum(map(len, graph.values())),
                bfs_dfs_same_reachable_states=True, shortest_counterexamples=witnesses)


def design_matrix(folder):
    axes = {
        "entry": ["chat", "quick_chat", "schedule", "workflow", "shortcut"],
        "lifecycle": ["online", "offline", "restarting", "asleep"],
        "authority": ["valid", "expired", "revoked", "account_changed"],
        "operation": ["read", "propose", "write"],
        "evidence": ["fresh", "changed", "deleted", "missing"],
        "payload": ["ordinary", "oversize", "unicode", "untrusted_markup"],
    }
    names = list(axes)
    candidates = list(product(*axes.values()))
    def pairs(row):
        return frozenset((i, row[i], j, row[j]) for i, j in combinations(range(len(row)), 2))
    indexed = [(row, pairs(row)) for row in candidates]
    uncovered = set().union(*(p for _, p in indexed))
    universe = len(uncovered)
    selected = []
    while uncovered:
        row, covered = max(indexed, key=lambda item: len(item[1] & uncovered))
        assert covered & uncovered
        selected.append(row)
        uncovered -= covered
    for filename, rows in (("designed-scenarios.csv", candidates), ("pairwise-scenarios.csv", selected)):
        with (folder / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["id", *names, "status"])
            for i, row in enumerate(rows, 1):
                writer.writerow([f"S{i:04}", *row, "Not run"])
    return dict(axes=axes, cartesian_scenarios=len(candidates), pairwise_selected=len(selected),
                unique_pairs=universe, uncovered_pairs=len(uncovered),
                status="test designs only; no app or provider execution; unsupported combinations must be denied")


def date_boundaries():
    ny = ZoneInfo("America/New_York")
    gap = datetime(2026, 3, 8, 2, 30)
    roundtrip = gap.replace(tzinfo=ny).astimezone(timezone.utc).astimezone(ny).replace(tzinfo=None)
    fold = datetime(2026, 11, 1, 1, 30)
    due = datetime(2026, 10, 26, tzinfo=timezone.utc)
    observed = dict(
        spring_local_time_nonexistent=gap != roundtrip,
        autumn_local_time_ambiguous=fold.replace(tzinfo=ny, fold=0).utcoffset() != fold.replace(tzinfo=ny, fold=1).utcoffset(),
        date_only_task_can_shift_day_if_treated_as_timestamp=due.astimezone(ZoneInfo("America/Los_Angeles")).date() != due.date(),
        interpretation="timezone arithmetic only; no schedule was created or tested",
    )
    assert all(v is True for k, v in observed.items() if k != "interpretation")
    return observed


def race_orders():
    groups = [
        ["approve_original_proposal", "revoke", "dispatch", "provider_applies", "lose_acknowledgement"],
        ["approve_original_proposal", "approval_expires", "dispatch", "switch_active_account"],
        ["approve_original_proposal", "edit_proposed_payload", "dispatch", "restart"],
    ]
    chat_group = ["submit_in_space_A", "switch_visible_space", "delta_1_for_space_A", "server_confirms_cancel", "complete_2_for_space_A"]
    results = {}
    for guarded in (False, True):
        count, failed = 0, 0
        for group in groups:
            for order in permutations(group):
                s = Action()
                for event in order:
                    # Requests invalid in the current state are denied/no state change.
                    s = dict(successors(s, guarded)).get(event, s)
                count += 1
                failed += bool(violations(s))
        for order in permutations(chat_group):
            s = Chat()
            for event in order:
                s = dict(chat_edges(s, guarded)).get(event, s)
            count += 1
            failed += bool(s.scope_leaked or s.resurrected or s.finals > 1)
        results["guarded" if guarded else "deliberately_permissive"] = dict(orders=count, violating_orders=failed)
    assert results["guarded"]["violating_orders"] == 0
    return dict(results=results, interpretation="abstract event orderings; not concurrent threads or provider races")


def existing_wire_boundaries(root):
    # Execute only the actual pure wire() function, without importing/starting any
    # application, database, model, service or installed SDK.
    source = root.parents[1] / "wayfinder" / "api.py"
    module = ast.parse(source.read_text(encoding="utf-8"))
    function = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "wire")
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
    values = [0, 1, 2**53 - 1, 2**53, 2**53 + 1, 2**63 - 1, -(2**63), True, False]
    for value in values:
        actual = namespace["wire"]({"outer": [value]})["outer"][0]
        expected = str(value) if type(value) is int and abs(value) > 2**53 - 1 else value
        assert actual == expected and type(actual) is type(expected)
    return dict(passed=len(values), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                interpretation="existing Python wire function only; future TypeScript event contract is still unspecified")


def task_projection_example(root):
    project = root.parents[1]
    adapter_path = project / "wayfinder/platform/google_read.py"
    adapter_ast = ast.parse(adapter_path.read_text(encoding="utf-8"))
    refusal = next(n for n in adapter_ast.body if isinstance(n, ast.ClassDef) and n.name == "ReadRefusal")
    adapter = next(n for n in adapter_ast.body if isinstance(n, ast.ClassDef) and n.name == "GoogleRead")
    read = next(n for n in adapter.body if isinstance(n, ast.FunctionDef) and n.name == "read")
    base = ast.parse((project / "wayfinder/atlas/harness/base.py").read_text(encoding="utf-8"))
    task = next(n for n in base.body if isinstance(n, ast.ClassDef) and n.name == "TaskItem")
    namespace = dict(json=json, time=time, dataclass=dataclass, field=field, asdict=asdict, Any=object, VERSION="fixture")
    exec(compile(ast.Module(body=[task, refusal, read], type_ignores=[]), str(adapter_path), "exec"), namespace)
    raw = dict(items=[dict(id="synthetic-task", title="Synthetic task", status="needsAction", etag="synthetic-version", updated="2026-10-26T00:00:00Z")])

    class Response:
        status_code = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def iter_content(self, **kwargs):
            yield json.dumps(raw).encode()

    class Session:
        def get(self, *args, **kwargs):
            return Response()
        def close(self):
            pass

    class Fixture:
        session_factory = object()
        clock = staticmethod(time.time)

        def session(self, *args):
            return Session()

        def live(self, *args):
            return None

    output = namespace["read"](Fixture(), dict(service="tasks", connection="synthetic", url="https://tasks.googleapis.com/tasks/v1/lists/synthetic/tasks", params={}, limit=3, resource="synthetic", expires=time.time() + 60))
    item = output["records"][0]
    return dict(input_status="needsAction", output_status=item["status"],
                normalized_pending=item["status"] == "pending",
                etag_retained=item["metadata"].get("etag") == "synthetic-version",
                updated_retained=item["metadata"].get("updated") == "2026-10-26T00:00:00Z",
                source_sha256=hashlib.sha256(adapter_path.read_bytes()).hexdigest(),
                interpretation="actual extracted projection method with synthetic response and fake session; no auth, app or provider was started")


def main():
    start = time.monotonic()
    root = Path(__file__).resolve().parents[1]
    report = dict(
        scope="finite abstract action lifecycle; no implementation or provider validation",
        bounds=dict(accounts=2, reviewed_actions=1, max_dispatches=2, max_effects=2),
        deliberate_bad_model=explore(False), proposed_guarded_model=explore(True),
        chat_deliberate_bad_model=explore_chat(False), chat_proposed_guarded_model=explore_chat(True),
        date_boundaries=date_boundaries(),
        abstract_race_orders=race_orders(), existing_wire_boundaries=existing_wire_boundaries(root),
        existing_task_projection=task_projection_example(root),
        designed_matrix=design_matrix(Path(__file__).parent),
        input_sha256={name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                      for name in ("PLAN.md", "FLOWS.md", "WORKER-SURFACES.md", "ACCEPTANCE.csv", "preview.html")},
        elapsed_seconds=round(time.monotonic() - start, 3),
    )
    assert report["deliberate_bad_model"]["shortest_counterexamples"], "Mutation model must expose violations"
    assert not report["proposed_guarded_model"]["violating_states"], "Guarded abstraction failed"
    assert not report["chat_proposed_guarded_model"]["shortest_counterexamples"]
    assert len(report["chat_deliberate_bad_model"]["shortest_counterexamples"]) == 3
    destination = Path(__file__).with_name("model-results.json")
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
