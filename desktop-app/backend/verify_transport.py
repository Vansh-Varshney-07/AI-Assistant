"""Headless production transport + actual neural engine smoke, isolated storage.

This is not a GUI/native-action test or a held-out retrieval quality evaluation.
Run only against the uniquely disposable database supplied by Test-Backend.ps1.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import secrets
import subprocess
import sys
from threading import Thread
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    project = root.parent
    secret = secrets.token_hex(32)
    diagnostic = Path(args.report).with_suffix('.startup.log').open('w', encoding='utf-8')
    environment = dict(os.environ, WAYFINDER_HOST_SECRET=secret, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", WAYFINDER_DIAG_THREADS="1")
    process = subprocess.Popen(
        [sys.executable, "-B", "-u", str(Path(__file__).with_name("host.py")), "--project", str(project), "--runtime", args.runtime],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=diagnostic,
        text=True, encoding="utf-8", cwd=project, env=environment,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    incoming = queue.Queue()

    def read():
        for line in process.stdout:
            if line.startswith("WAYFINDER_DESKTOP="):
                incoming.put(json.loads(line[len("WAYFINDER_DESKTOP="):]))
        incoming.put({"exited": True})

    Thread(target=read, daemon=True).start()
    sequence = 0
    checks = []

    def call(operation, body=None, timeout=120):
        nonlocal sequence
        sequence += 1
        rid = str(sequence)
        process.stdin.write(json.dumps(dict(id=rid, secret=secret, operation=operation, body=body or {})) + "\n")
        process.stdin.flush()
        result = incoming.get(timeout=timeout)
        assert result.get("id") == rid, result
        if not result.get("ok"):
            raise RuntimeError(result.get("error", "Transport failed"))
        return result["data"]

    def check(name, passed):
        checks.append(dict(name=name, passed=bool(passed)))
        assert passed, name

    started = time.monotonic()
    try:
        state = call("boot")
        check("real_engine_ready", state["state"] == "ready")
        check("no_secret_in_metadata", secret not in json.dumps(state))
        check("unqualified_routes_disabled", not state["capabilities"]["general_chat"] and not state["capabilities"]["native_desktop"] and not state["capabilities"]["google_live"])
        sid = call("create_space", {"name": "Synthetic headless desktop qualification"})["id"]
        scope = dict(space=sid, task="general")
        pending = call("platform_memory_propose", dict(scope, request_id="neural-once", body=dict(text="Synthetic project retention is 30 days.", subject="me", predicate="retention_days", value=30, action="assert", task_id="general")))
        check("pending_not_applied", pending["status"] == "pending" and call("recall", {"space": sid, "predicate": "retention_days"})["packet"]["answer_status"] == "missing")
        receipt = call("platform_memory_decide", dict(scope, id=pending["id"], digest=pending["digest"], approve=True))
        check("neural_dual_store_receipt", receipt["status"] == "completed" and receipt["result"]["verified"] is True)
        evidence = call("recall", {"space": sid, "predicate": "retention_days"})["packet"]["evidence"]
        check("real_neural_recall", len(evidence) == 1 and evidence[0]["value"] == 30)
        second = call("create_space", {"name": "Synthetic independent space"})["id"]
        check("space_isolation", call("recall", {"space": second, "predicate": "retention_days"})["packet"]["evidence"] == [])
        snapshot = call("snapshot", {"space": sid})
        check("snapshot_existing_receipt", snapshot["actions"][0]["id"] == pending["id"])
        live_result = None
        if args.live:
            inspected = call("platform_inspect", scope)
            check("installed_runtime_isolated", inspected["compatible"] and inspected["isolation"]["effective_tools"] == [] and inspected["isolation"]["memory"] is False)
            selected = Path(args.runtime).parent / "synthetic-document.md"
            selected.write_text("Synthetic document: the project retention is 42 days. No other source has precedence.", encoding="utf-8")
            grant = call("worker_grant", dict(scope, path=str(selected)))
            ref = call("worker_search", dict(scope, grant=grant["id"]))["files"][0]["id"]
            job = call("platform_read_start", dict(scope, request=dict(request_id="live-client-once", question="Compare the synthetic retention values and explain the discrepancy. Cite both sources; do not decide which source takes precedence.", reference=ref, context=dict(subject="me", predicate="retention_days"))))
            deadline = time.monotonic() + 115
            while time.monotonic() < deadline:
                job = call("platform_read_result", dict(scope, id=job["id"]))
                if job["status"] != "worker_running":
                    break
                time.sleep(0.3)
            check("live_client_workflow_completed", job["status"] == "completed")
            check("genuine_model_compares_sources", all(value in job["result"]["synthesis"] for value in ("30", "42")))
            check("selected_file_independently_checked", job["result"]["evidence"]["file"]["sha256"] == hashlib.sha256(selected.read_bytes()).hexdigest())
            check("one_live_dispatch_no_effect", job["result"]["metrics"]["worker_invocations"] == 1 and job["result"]["executed"] is False)
            live_result = dict(runtime_version=inspected["runtime"]["version"], status=job["status"], metrics=job["result"]["metrics"], verification=job["result"]["verification"])
            catalog=call('platform_profiles',scope)
            check('profile_and_preset_inventory',len(catalog['profiles'])==8 and len(catalog['presets'])==6 and all(not p['available'] for p in catalog['presets']))
            task=call('platform_profile_start',dict(scope,request=dict(request_id='live-study-guide-once',profile_id='A05',profile_version='1',reference=ref,goal='Create a concise study guide from the supplied synthetic document. State the retention value, explain its meaning and include one practice question. Cite the source; do not invent missing context.')))
            task_deadline=time.monotonic()+115
            while time.monotonic()<task_deadline:
                task=call('platform_profile_result',dict(scope,id=task['id']))
                if task['status'] not in {'running','reserved'}:break
                time.sleep(.3)
            check('live_knowledge_task_completed',task['status']=='completed' and '42' in task['result']['text'])
            check('live_task_source_verified',task['result']['sources'][0]['sha256']==hashlib.sha256(selected.read_bytes()).hexdigest())
            check('single_existing_worker_no_helpers_or_effects',task['metrics']['worker_invocations']==1 and task['metrics']['delegations']==0 and task['effects_executed'] is False)
            replay=call('platform_profile_start',dict(scope,request=dict(request_id='live-study-guide-once',profile_id='A05',profile_version='1',reference=ref,goal='Create a concise study guide from the supplied synthetic document. State the retention value, explain its meaning and include one practice question. Cite the source; do not invent missing context.')))
            check('live_task_duplicate_did_not_redispatch',replay['id']==task['id'] and replay['job']==task['job'])
            live_result['knowledge_task']=dict(status=task['status'],profile=task['profile_id'],metrics=task['metrics'],source_verified=True)
        report = dict(scope="actual private Python stdio adapter + authenticated API + actual cached ONNX embeddings + disposable Iron Web", checks=checks, passed=len(checks), elapsed_seconds=round(time.monotonic() - started, 3), actual_neural_embeddings=True, live_hermes=live_result, gui_tested=False, native_tested=False, google_account_tested=False, held_out_memory_quality_tested=False)
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report))
    finally:
        if process.poll() is None:
            process.stdin.close()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        diagnostic.close()


if __name__ == "__main__":
    main()
