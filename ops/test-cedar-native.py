"""Human-approved Cedar-only native execution test using the real Cua driver."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wayfinder.api import Client, serve
from wayfinder.service import AppService
from wayfinder.workers.cua_fixture import CuaFixtureDriver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--approved-test", action="store_true", required=True)
    parser.add_argument("--reuse-validated-plan", action="store_true")
    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Explicitly bind foreground delivery to this already approved fixture test",
    )
    args = parser.parse_args()
    case = args.case.resolve()
    prior = case / "native-execution.json"
    if prior.exists():
        (case / f"native-attempt-{time.time_ns()}.json").write_bytes(prior.read_bytes())
    if (case / "output/cedar-handoff.txt").exists():
        raise ValueError(
            "A test draft already exists; overwriting and blind replay are unavailable."
        )
    target = json.loads((case / "fixture-target.json").read_text())
    driver = CuaFixtureDriver(
        args.driver, r"\\.\pipe\wayfinder-cedar-20261025-215958", case, **target
    )
    baseline = driver.snapshot()
    draft = "Project Cedar handoff: screenshot retention = 42 days; release note retention = 30 days. Discrepancy unresolved; confirmation required."
    expected_steps = [
        dict(action="click", x=200, y=420),
        dict(action="type_text", text=draft),
        dict(action="click", x=70, y=628),
    ]
    if args.foreground:
        expected_steps = [
            dict(step, delivery_mode="foreground") for step in expected_steps
        ]
    observation = dict(
        app=target["title"],
        process=target["process"],
        window=target["window"],
        state=baseline,
        observation="selected_window",
        exact_steps=expected_steps,
        evidence="The observed screenshot says 42 days; the permitted release note says 30 days. Both are synthetic.",
        destination=str(case / "output/cedar-handoff.txt"),
        controls="Click (200,420) focuses the blank editor. Click (70,628) is the observed Save new draft button. Save never overwrites.",
    )

    class NoMemory:
        def close(self):
            pass

    service = AppService(case / "native-test-runtime", NoMemory())
    service.workers.actions.driver = driver
    server = serve(service)
    client = Client(server.server_port, service.token)
    sid = client.call("create_space", name="Approved Cedar native execution")["id"]
    scope = dict(space=sid, task="approved-cedar-native")
    report = dict(
        driver="Real signed Cua 0.37.0 CLI used by Hermes computer-use",
        target=target,
        limits="One fixed fixture process/window; no full-desktop capture; no overwrite",
        checks=[],
    )

    def record(name, passed, evidence):
        row = dict(
            test=name, status="passed" if passed else "failed", evidence=evidence
        )
        report["checks"].append(row)
        (case / "native-execution.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(json.dumps(row), flush=True)
        return passed

    try:
        if args.reuse_validated_plan:
            job = None
            with service.db() as connection:
                rows = connection.execute(
                    "SELECT id,result FROM worker_jobs WHERE role='W36' AND status='completed' ORDER BY created DESC"
                ).fetchall()
            for row in rows:
                saved = json.loads(row["result"])
                candidate = saved.get("plan") or {}
                candidate_steps = [
                    {
                        k: v
                        for k, v in s.items()
                        if v is not None and k != "delivery_mode"
                    }
                    for s in candidate.get("steps", [])
                ]
                expected_core = [
                    {k: v for k, v in s.items() if k != "delivery_mode"}
                    for s in expected_steps
                ]
                if candidate_steps == expected_core and all(
                    candidate.get(k) == observation[k]
                    for k in ["app", "process", "window", "state", "observation"]
                ):
                    if args.foreground:
                        saved["plan"]["steps"] = expected_steps
                        saved["controller_delivery_policy"] = (
                            "Foreground explicitly selected after a confirmed background_occluded refusal; target and payload unchanged."
                        )
                    job = dict(
                        id=row["id"],
                        role="W36",
                        status="completed",
                        result=saved,
                        reused_persisted_worker_output=True,
                    )
                    break
            if job is None:
                raise ValueError(
                    "No previously validated Hermes plan matches this current fixture state."
                )
        else:
            job = client.call(
                "worker_start",
                **scope,
                role="W36",
                context=json.dumps(observation),
                question=(
                    "Create the exact executable DesktopPlan for the observed Cedar fixture. Use only exact_steps in the supplied context, "
                    "preserving every parameter and the full literal text. Use the observed app/process/window/state. "
                    "The completion condition is the new destination file containing the exact draft. Do not execute anything."
                ),
            )
        deadline = time.monotonic() + 125
        while (
            job["status"] in {"queued", "running", "stopping"}
            and time.monotonic() < deadline
        ):
            time.sleep(0.2)
            job = client.call("worker_result", **scope, id=job["id"])
        result = job.get("result") or {}
        plan = result.get("plan")
        if not record(
            "W36 exact native plan",
            job["status"] == "completed"
            and isinstance(plan, dict)
            and result.get("executed") is False,
            job,
        ):
            return 1
        actual_steps = [
            {k: v for k, v in step.items() if v is not None} for step in plan["steps"]
        ]
        if actual_steps != expected_steps or any(
            plan[k] != observation[k]
            for k in ["app", "process", "window", "state", "observation"]
        ):
            record(
                "Plan parameters match the exact reviewed fixture operations",
                False,
                dict(reason="Model plan changed the allowed target or payload"),
            )
            return 1
        record(
            "Plan parameters match exact reviewed operations",
            True,
            dict(steps=actual_steps),
        )
        rejected = client.call("worker_action_propose", **scope, plan=plan)
        denied = client.call(
            "worker_action_decide", **scope, id=rejected["id"], approve=False
        )
        record(
            "Reject approval produces no input",
            denied["status"] == "rejected" and not driver.calls,
            denied,
        )
        stale = dict(plan, state="0" * 64)
        proposed = client.call("worker_action_propose", **scope, plan=stale)
        stopped = client.call(
            "worker_action_decide", **scope, id=proposed["id"], approve=True
        )
        record(
            "Stale observation produces no input",
            stopped["status"] == "failed" and not driver.calls,
            stopped,
        )
        other = dict(plan, process=target["process"] + 1)
        proposed = client.call("worker_action_propose", **scope, plan=other)
        stopped = client.call(
            "worker_action_decide", **scope, id=proposed["id"], approve=True
        )
        record(
            "Different process produces no input",
            stopped["status"] == "failed" and not driver.calls,
            stopped,
        )
        approved = client.call("worker_action_propose", **scope, plan=plan)
        # Human explicitly approved this one fixture window and one new synthetic draft.
        executed = client.call(
            "worker_action_decide", **scope, id=approved["id"], approve=True
        )
        output = case / "output/cedar-handoff.txt"
        verified = output.is_file() and output.read_text(encoding="utf-8") == draft
        record(
            "W37 real editor input and independently verified file",
            executed["status"] == "completed" and verified,
            dict(
                action=executed,
                output_exists=output.exists(),
                exact_content=verified,
                driver_calls=len(driver.calls),
            ),
        )
        repeated = client.call(
            "worker_action_decide", **scope, id=approved["id"], approve=True
        )
        record(
            "Replayed approval does not duplicate input",
            repeated["status"] == executed["status"] and len(driver.calls) <= 3,
            dict(status=repeated["status"], driver_calls=len(driver.calls)),
        )
        if verified:
            report["output_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        (case / "native-execution.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        return 1 if any(row["status"] == "failed" for row in report["checks"]) else 0
    finally:
        server.shutdown()
        server.server_close()
        service.close()


if __name__ == "__main__":
    raise SystemExit(main())
