"""Live isolation proof. Uses real workbench, BGE and both NVIDIA models."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import uuid

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-directory", type=Path, default=ROOT / "docs/memory-spaces-validation"
)
parser.add_argument(
    "--verify-restart",
    action="store_true",
    help="After manually restarting the server, verify the saved run's persistence.",
)
args = parser.parse_args()
OUT = args.output_directory
BASE = "http://127.0.0.1:3352"
token = ""
events, checks = [], []
prefix = datetime.now(timezone.utc).strftime("spaces_%m%d_%H%M%S")


def api(path, body=None):
    headers = {"Content-Type": "application/json", "X-Workbench-Token": token}
    req = Request(
        BASE + path,
        data=None if body is None else json.dumps(body).encode(),
        headers=headers,
    )
    try:
        with urlopen(req, timeout=180) as response:
            return json.load(response)
    except HTTPError as error:
        return dict(http_status=error.code, **json.load(error))


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "memory-spaces-live-evidence.json").write_text(
        json.dumps(dict(run=prefix, checks=checks, events=events), indent=2),
        encoding="utf-8",
    )


def check(name, passed):
    checks.append(dict(name=name, passed=bool(passed)))
    print(name, "PASS" if passed else "FAIL", flush=True)
    save()


def send(space, text, model, mode="retrieve", request_id=None):
    body = dict(
        memory_space_id=space,
        prompt=text,
        model=model,
        mode=mode,
        confirmed=True,
        subject="manual-user",
        request_id=request_id or uuid.uuid4().hex,
        session_id=uuid.uuid4().hex,
    )
    result = api("/api/prompt", body)
    events.append(dict(request=body, response=result))
    print(model.rsplit("/", 1)[-1], space, mode, result.get("ok"), flush=True)
    save()
    return result


token = api("/api/session")["token"]
if args.verify_restart:
    saved = json.loads(
        (OUT / "memory-spaces-live-evidence.json").read_text(encoding="utf-8")
    )
    prefix, events, checks = saved["run"], saved["events"], saved["checks"]
    stored = [event for event in list(events) if event["request"]["mode"] == "store"]
    if len(stored) != 4 or not all(event["response"].get("ok") for event in stored):
        raise RuntimeError(
            "The saved model-validation run did not complete successfully."
        )
    for event in stored:
        space = event["request"]["memory_space_id"]
        mid = event["response"]["stored"]["memory_id"]
        result = send(space, "What is my current test code?", "")
        records = api("/api/memories?memory_space_id=" + space)["records"]
        check(
            space + " survives server restart",
            result.get("ok")
            and result["diagnostics"]["retrieved_memory_ids"] == [mid]
            and len(records) == 1
            and records[0]["memory_id"] == mid,
        )
    empty = next(
        event["request"]["memory_space_id"]
        for event in events
        if event["request"]["model"] == "" and not event["response"].get("retrieved")
    )
    check(
        "empty space survives restart",
        api("/api/memories?memory_space_id=" + empty).get("records") == [],
    )
    save()
    print(
        f'{sum(c["passed"] for c in checks)}/{len(checks)} live checks passed',
        flush=True,
    )
    sys.exit(0 if all(c["passed"] for c in checks) else 1)
pairs = []
for label, model in (
    ("light", "nvidia/nemotron-3.5-lightning-30b-a3b"),
    ("ultra", "nvidia/nemotron-3-ultra-550b-a55b"),
):
    pair = []
    event_id = uuid.uuid4().hex
    for suffix, value in (("a", "copper-orchid-741"), ("b", "silver-maple-862")):
        space = prefix + "_" + label + "_" + suffix
        created = api(
            "/api/spaces",
            dict(
                memory_space_id=space, name="Isolation " + label + " " + suffix.upper()
            ),
        )
        check(
            label + suffix + " create empty space",
            created.get("memory_space_id") == space
            and api("/api/memories?memory_space_id=" + space).get("records") == [],
        )
        result = send(
            space,
            "My current test code is " + value + ". Remember it exactly.",
            model,
            "store",
            event_id,
        )
        mid = (result.get("stored") or {}).get("memory_id")
        check(
            label + suffix + " dual-store write",
            result.get("ok")
            and result["diagnostics"]["storage_confirmed"]
            and result["stored"]["memory_space_id"] == space,
        )
        pair.append((space, value, mid, model))
    check(
        label + " same request ID stays separate",
        pair[0][2] and pair[1][2] and pair[0][2] != pair[1][2],
    )
    for space, value, mid, model in pair:
        result = send(space, "What is my current test code?", model)
        answer = result.get("assistant") or {}
        other = next(p[1] for p in pair if p[0] != space)
        check(
            space + " isolated model answer",
            result.get("ok")
            and value in answer.get("answer", "")
            and other not in json.dumps(result)
            and answer.get("citations") == [mid]
            and result["diagnostics"]["retrieved_memory_ids"] == [mid],
        )
    pairs.extend(pair)
empty = api("/api/spaces", dict(name="Empty isolation space"))["memory_space_id"]
check(
    "new ID starts empty after other writes",
    send(empty, "What is my current test code?", "").get("retrieved") == [],
)
check("unscoped inventory fails closed", api("/api/memories").get("http_status") == 400)
save()
print(
    f'{sum(c["passed"] for c in checks)}/{len(checks)} live checks passed. Restart the workbench, then run with --verify-restart.',
    flush=True,
)
sys.exit(0 if all(c["passed"] for c in checks) else 1)
