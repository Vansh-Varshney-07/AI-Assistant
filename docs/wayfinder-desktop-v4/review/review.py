"""Cumulative artifact checks and finite models; never app/provider qualification.

Only writes inside this design directory. Imports the earlier pure models without
running their main function or changing their reports. Every checkpoint repeats
the original safety models, checks old source hashes and rechecks earlier fixes.
"""

import argparse
from collections import Counter, deque
import csv
from dataclasses import dataclass, replace
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / "wayfinder-desktop-v3"
REVIEW = ROOT / "review"
MAPPING = {
    1: (1, "C01"), 2: (1, "C02"), 3: (1, "C03"), 4: (1, "C04"),
    5: (1, "C03"), 6: (1, "C05"), 7: (1, "C07"), 8: (2, "C08"),
    9: (2, "C09"), 10: (2, "C06"), 11: (3, "C11"), 12: (4, "C15"),
    13: (3, "C12"), 14: (3, "C13"), 15: (4, "C14"), 16: (4, "C15"),
    17: (4, "C16"), 18: (4, "C17"), 19: (4, "C18"), 20: (2, "C10"),
    21: (3, "C12"), 22: (2, "C08"), 23: (1, "C04"), 24: (2, "C08"),
    25: (1, "C02"), 26: (5, "C22"), 27: (5, "C22"), 28: (5, "C22"),
    29: (5, "C22"), 30: (5, "C22"), 31: (5, "C23"), 32: (4, "C20"),
    33: (4, "C20"), 34: (2, "C21"), 35: (5, "C19"), 36: (1, "C05"),
}
AMENDMENTS = {
    1: "Application-canonical bounded history; tool-closed isolated Hermes binding; frozen provider policy",
    2: "Authenticated stable-root runtime ownership; safe lock recovery; owned/shared lifecycle and component health",
    3: "Host request journal before send; atomic acceptance; durable reservation; explicit new read attempt only",
    4: "Scoped string-ID sequenced events; snapshots/bounded buffers; terminal CAS and truthful upstream cancellation",
    5: "Observation-only retries; command identity cannot be refreshed automatically; unknown effects never ordinary retry",
    6: "API/schema negotiation, exclusive supported migration and isolated compatible restore start with R1",
    7: "Concrete content/IPC/source-opening deny policy, size limits and negative acceptance",
    8: "Freeze provider binding and require both local read and permitted outbound disclosure",
    9: "Durable forget barrier, context epoch, pre-barrier chats view-only, purge verification and latest-ledger restore gate",
    10: "Trusted immutable proposal, atomic competing decision and final scope/version/account checks",
    11: "Separate connection/qualification/authority health; immutable account identity and generations; bounded read retry",
    12: "Templates store intentions; manual/standing authority issues fresh short-lived step references within limits",
    13: "Local/provider task independence; raw/canonical status and versions; explicit one-time copy; two-way sync deferred",
    14: "Provider writes moved to optional R7 modules; per-operation receipts/attribution/reconciliation and conservative stable-account duplicate locks",
    15: "Linear maximum-six-step read recipes; pinned versions, typed edges, required inputs and five-minute freshness",
    16: "Root budgets include all children/retries; bounded queues, foreground priority and retained uncertain accounting",
    17: "Daily fixed IANA-zone only; skip gaps/missed, first fold, no overlap/catch-up; unique intended-UTC admission",
    18: "Existing scheduler must enter trusted adapter and pass durable app Quit fence; otherwise feature unavailable",
    19: "Reviewed immutable skill/binding versions and effective rights; pinned execution plus live revocation; rollback future-only",
    20: "Retain hard memory invariants; proposed preregistered 40-case held-out neural suite with at least 38 correct and zero boundary failures",
    21: "Date-only task semantics remain dates; timed reminders not promised by a task field",
    22: "Historical retained excerpt differs from temporary artifact and fresh current-source access",
    23: "Opaque IDs/decimal-string counters with existing wire regression and future decoder qualification",
    24: "Qualified UTF-8 text/Markdown first; byte/extraction limits, target/hash checks, partial indicators and tracked cleanup",
    25: "Component-specific prerequisites and degraded states; no silent empty-root fallback or privileged dependency repair",
    26: "Prototype conflicting outline removed; visible and forced-colour focus rules; rendered verification still required",
    27: "One generated manifest governs routes, samples, inspector and attachments; direct unsupported intents denied",
    28: "Prototype native navigation dialog with real open/close/Escape and live focus fallback",
    29: "Prototype actual wide visibility plus narrow dialog and synchronized aria-expanded/labels",
    30: "Prototype composition latch/event/key229 guards; normal Enter and Shift+Enter remain distinct",
    31: "Explicit feature variants, required-when-advertised cases, exclusion reasons and mandatory omitted-capability denial",
    32: "Live web research and external notes explicitly deferred; no misleading model-only substitute",
    33: "All 47 IDs inventoried; unresolved bindings remain unavailable until developer reconciliation; no invented prompts",
    34: "Record-class retention, pending privacy barriers, quotas and truthful disk-full state; expired command namespaces prevent pruned replay",
    35: "Quick view shares broker/draft lease; clamped bounds, hotkey conflict, tray restore and private notification rules",
    36: "Pinned host/build/runtime/license matrix and no-go gates before implementation; no automatic runtime upgrade",
}
RISK_REFS = {
    1: "N05;N11", 2: "N01;N20", 3: "N02;N03;N08", 4: "N04;N05",
    5: "N02;N03;N15", 6: "N06;N09", 7: "N24;N26", 8: "N11",
    9: "N07;N09;N12", 10: "N04;N14;N17;N29", 11: "N14;N28", 12: "N18;N19",
    13: "N13", 14: "N12;N15;N16;N28", 15: "N17;N18", 16: "N04;N21",
    17: "N19", 18: "N18;N20", 19: "N17;N26", 20: "N07;N11",
    21: "N13;N19", 22: "N10", 23: "N05", 24: "N10;N11", 25: "N01;N06",
    26: "N24;N27", 27: "N25;N26", 28: "N24;N27", 29: "N24;N27",
    30: "N27", 31: "N25;N26", 32: "N25;N26", 33: "N17;N26",
    34: "N02;N08;N09;N12", 35: "N23;N24;N27", 36: "N06;N22",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def baseline():
    path = REVIEW / "baseline.json"
    files = {str(p.relative_to(OLD)).replace("\\", "/"): sha(p)
             for p in OLD.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    if not path.exists():
        path.write_text(json.dumps(files, indent=2) + "\n", encoding="utf-8")
    expected = json.loads(path.read_text(encoding="utf-8"))
    assert files == expected, "Earlier plan/audit changed; investigate, do not reset baseline"
    return len(files)


def legacy_models():
    spec = importlib.util.spec_from_file_location("v3_design_models", OLD / "audit/check_models.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    bad, good = module.explore(False), module.explore(True)
    chat_bad, chat_good = module.explore_chat(False), module.explore_chat(True)
    assert len(bad["shortest_counterexamples"]) == 4
    assert not good["violating_states"]
    assert len(chat_bad["shortest_counterexamples"]) == 3
    assert not chat_good["shortest_counterexamples"]
    race = module.race_orders()
    assert race["results"]["guarded"]["violating_orders"] == 0
    return dict(action_guarded=good, chat_guarded=chat_good,
                negative_control_action=bad, negative_control_chat=chat_bad,
                orderings=race, wire=module.existing_wire_boundaries(OLD),
                dates=module.date_boundaries())


@dataclass(frozen=True)
class Epoch:
    authority: int = 0
    context: int = 0
    sent: bool = False
    bound_authority: int = 0
    bound_context: int = 0
    result: bool = False
    current_visible: bool = False
    leak: bool = False


def epoch_next(s, guarded):
    if not s.sent and s.authority == 0:
        yield "submit_frozen_context", replace(s, sent=True, bound_authority=s.authority,
                                              bound_context=s.context)
    if s.authority == 0:
        yield "disconnect_or_replace_account", replace(s, authority=1, current_visible=False)
    if s.context == 0:
        yield "forget_or_correct_context", replace(s, context=1, current_visible=False)
    if s.sent and not s.result:
        yield "worker_finishes", replace(s, result=True)
    if s.result and not s.current_visible:
        stale = s.authority != s.bound_authority or s.context != s.bound_context
        if not guarded or not stale:
            yield "publish_or_rehydrate_cached_result", replace(s, current_visible=True,
                                                                leak=s.leak or stale)
    yield "reconnect_observes_only", s


def epoch_model(guarded):
    initial = Epoch()
    parents, queue, graph = {initial: None}, deque([initial]), {}
    witness = None
    while queue:
        s = queue.popleft()
        if s.leak and witness is None:
            witness, at = [], s
            while parents[at] is not None:
                previous, event = parents[at]
                witness.append(event)
                at = previous
            witness.reverse()
        graph[s] = list(epoch_next(s, guarded))
        for event, nxt in graph[s]:
            if nxt not in parents:
                parents[nxt] = (s, event)
                queue.append(nxt)
    seen, stack = set(), [initial]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        stack.extend(nxt for _, nxt in graph[s])
    assert seen == set(parents)
    return dict(states=len(seen), edges=sum(map(len, graph.values())),
                bfs_dfs_agree=True, stale_delivery_counterexample=witness,
                assumptions="one input, one context revision, one account epoch; no real storage/provider")


@dataclass(frozen=True)
class RiskLock:
    generation: int = 0
    erased: bool = False
    repeat_admitted: bool = False


def lock_model(guarded):
    initial = RiskLock()
    queue, parents, graph, witness = deque([initial]), {initial: None}, {}, None
    while queue:
        state = queue.popleft()
        if state.repeat_admitted and witness is None:
            witness, at = [], state
            while parents[at] is not None:
                previous, event = parents[at]
                witness.append(event)
                at = previous
            witness.reverse()
        edges = [("status_read_observes_only", state)]
        if state.generation == 0:
            edges.append(("reconnect_same_stable_account", replace(state, generation=1)))
        if not state.erased:
            edges.append(("erase_semantic_payload", replace(state, erased=True)))
        if not guarded and not state.repeat_admitted and (state.generation or state.erased):
            edges.append(("resubmit_unknown_same_family_with_new_request_id", replace(state, repeat_admitted=True)))
        graph[state] = edges
        for event, nxt in edges:
            if nxt not in parents:
                parents[nxt] = (state, event)
                queue.append(nxt)
    seen, stack = set(), [initial]
    while stack:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        stack.extend(nxt for _, nxt in graph[state])
    assert seen == set(parents)
    return dict(states=len(seen), edges=sum(map(len, graph.values())), bfs_dfs_agree=True,
                repeat_counterexample=witness,
                assumptions="one already-uncertain effect, one stable provider account/resource/family; no provider semantics proof")


def manifest_checks(batch, contracts):
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    features = manifest["features"] + manifest["optional_features"]
    by_id = {f["id"]: f for f in features}
    assert len(by_id) == len(features)
    visited, active = set(), set()

    def visit(name):
        assert name not in active, "Feature dependency cycle"
        if name in visited:
            return
        active.add(name)
        f = by_id[name]
        for dependency in f["requires"]:
            assert dependency in by_id
            assert by_id[dependency]["release"] <= f["release"]
            visit(dependency)
        active.remove(name)
        visited.add(name)

    for f in features:
        visit(f["id"])
        if f.get("batch", 3) <= batch:
            assert f"## {f['contract']} " in contracts, f
    previous = set()
    for release in range(1, 8):
        enabled = {f["id"] for f in manifest["features"] if f["release"] <= release}
        assert previous <= enabled, "Prior release feature disappeared"
        for name in enabled:
            assert set(by_id[name]["requires"]) <= enabled
        previous = enabled
    assert manifest["r1"]["tools"] == "closed"
    assert not manifest["r1"]["automatic_memory"]
    assert not manifest["r1"]["background_execution"]
    assert manifest["r1"]["automatic_command_retries"] == 0
    return dict(features=len(features), acyclic=True, cumulative_releases=7)


def artifact_links():
    missing = []
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            if not (path.parent / target.split("#")[0]).exists():
                missing.append([str(path.relative_to(ROOT)), target])
    return missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, choices=range(1, 6), required=True)
    args = parser.parse_args()
    batch = args.batch
    contracts = (ROOT / "CONTRACTS.md").read_text(encoding="utf-8")
    findings = list(csv.DictReader((OLD / "audit/FINDINGS.csv").open(encoding="utf-8")))
    rows = []
    for f in findings:
        fix_batch, contract = MAPPING[int(f["id"][1:])]
        addressed = fix_batch <= batch
        if addressed:
            assert f"## {contract} " in contracts, f["id"]
        rows.append(dict(finding=f["id"], priority=f["priority"], title=f["title"],
                         batch=fix_batch, contract=contract,
                         plan_change=AMENDMENTS[int(f["id"][1:])],
                         second_order_risks=RISK_REFS[int(f["id"][1:])],
                         design_status="Addressed in proposed contract" if addressed else "Pending later batch",
                         implementation_status="Unverified", acceptance_refs=f"{f['id']}-T1;{f['id']}-T2"))
    csv_write(ROOT / "REMEDIATIONS.csv", list(rows[0]), rows)
    ledger = ["# Finding-by-finding redesign", "", "Every amendment is a proposed requirement. Implementation remains unverified. The original v3 finding and its evidence remain preserved; use the contract and acceptance references below rather than treating this ledger as a production pass.", ""]
    for row in rows:
        ledger.extend([f"## {row['finding']} — {row['title']}", "",
                       f"Batch {row['batch']} · {row['design_status']} · [Contract {row['contract']}](CONTRACTS.md)", "",
                       row["plan_change"] + ".", "",
                       f"Recheck: {row['acceptance_refs']}; second-order risks {row['second_order_risks']} in [risk register](SECOND-ORDER.md). All app cases remain Not run.", ""])
    (ROOT / "REMEDIATIONS.md").write_text("\n".join(ledger), encoding="utf-8")
    old = legacy_models()
    negative, guarded = epoch_model(False), epoch_model(True)
    assert negative["stale_delivery_counterexample"]
    assert guarded["stale_delivery_counterexample"] is None
    lock_bad, lock_good = lock_model(False), lock_model(True)
    assert lock_bad["repeat_counterexample"]
    assert lock_good["repeat_counterexample"] is None
    result = dict(batch=batch, scope="artifact consistency and finite design models only",
                  original_files_unchanged=baseline(),
                  findings_total=len(rows), findings_design_addressed=sum(r["batch"] <= batch for r in rows),
                  contracts_present=len(re.findall(r"^## C\d+ ", contracts, re.M)),
                  release_manifest=manifest_checks(batch, contracts),
                  original_safety_models=old,
                  epoch_negative_control=negative, epoch_guarded=guarded,
                  uncertainty_lock_negative_control=lock_bad, uncertainty_lock_guarded=lock_good,
                  unresolved_links=artifact_links(),
                  implementation_status="Not run; no desktop app or live integration tested")
    if batch == 5:
        assert not result["unresolved_links"], result["unresolved_links"]
        cases = list(csv.DictReader((ROOT / "ACCEPTANCE.csv").open(encoding="utf-8")))
        ids = {case["id"] for case in cases}
        assert len(ids) == len(cases)
        for row in rows:
            assert set(row["acceptance_refs"].split(";")) <= ids
        assert all(case["status"] == "Not run" for case in cases)
        assert all(case["owner"] and case["evidence_tier"] and case["requirement"] for case in cases)
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        by_feature = {f["id"]: f for f in manifest["features"] + manifest["optional_features"]}
        optional_ids = {f["id"] for f in manifest["optional_features"]}
        for case in cases:
            assert case["feature"] in by_feature, case["id"]
            assert int(case["release"][1:]) >= by_feature[case["feature"]]["release"], case["id"]
            if case["feature"] in optional_ids:
                assert case["requirement"] == "Required when advertised", case["id"]
            if case["excluded_if"]:
                assert case["excluded_if"] in optional_ids, case["id"]
        inventory = list(csv.DictReader((ROOT / "WORKER-COVERAGE.csv").open(encoding="utf-8")))
        assert {row["id"] for row in inventory} == {f"W{i:02}" for i in range(1, 48)}
        assert len(inventory) == 47
        result["worker_inventory"] = "47 IDs covered; bindings still unverified"
        result["acceptance"] = dict(cases=len(cases), status=dict(Counter(c["status"] for c in cases)))
        preview = json.loads((REVIEW / "preview-results.json").read_text(encoding="utf-8"))
        assert preview["failed"] == 0, preview
        assert preview["graph_executed"], "Final check requires actual full finite preview traversal"
        for name, digest in preview["input_sha256"].items():
            assert sha(ROOT / name) == digest, "Preview changed after its full check: " + name
        result["design_sha256"] = {name: sha(ROOT / name) for name in
                                   ("PLAN.md", "CONTRACTS.md", "FLOWS.md", "manifest.json", "preview.html", "ACCEPTANCE.csv", "SECOND-ORDER.md")}
        result["preview"] = {k: preview[k] for k in ("reachable_states", "transitions", "passed", "failed")}
    destination = REVIEW / f"batch-{batch}.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "original_safety_models"}))


if __name__ == "__main__":
    main()
