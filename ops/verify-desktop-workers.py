"""Explicit live smoke using synthetic artifacts only; never reads personal data."""

import argparse
import hashlib
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wayfinder.workers.hermes import HermesBridge
from wayfinder.workers.hub import WorkerHub


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Invoke the configured model with fixture inputs",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = dict(
        runtime="Hermes", isolation=HermesBridge().run({"role": "probe"}), checks=[]
    )
    if args.live:
        with tempfile.TemporaryDirectory(
            prefix="wayfinder-live-fixtures-"
        ) as temporary:
            root = Path(temporary)

            @contextmanager
            def db():
                connection = sqlite3.connect(root / "jobs.db", timeout=10)
                try:
                    with connection:
                        yield connection
                finally:
                    connection.close()

            hub = WorkerHub(db)
            scope = ("fixture-owner", "fixture-space", "fixture-task")

            def run(name, role, question, **kwargs):
                job = hub.start(scope, role=role, question=question, **kwargs)
                deadline = time.monotonic() + 115
                while (
                    job["status"] in {"queued", "running", "stopping"}
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.2)
                    job = hub.get(scope, job["id"])
                return dict(
                    name=name, role=role, status=job["status"], result=job.get("result")
                )

            try:
                for suffix in (".md", ".docx"):
                    path = root / ("fixture" + suffix)
                    if suffix == ".md":
                        path.write_text(
                            "Project codename: Cedar. Retention: 42 days.",
                            encoding="utf-8",
                        )
                    else:
                        with zipfile.ZipFile(path, "w") as archive:
                            archive.writestr(
                                "word/document.xml",
                                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Project codename: Cedar. Retention: 42 days.</w:t></w:r></w:p></w:body></w:document>',
                            )
                    grant = hub.files.grant(scope, path)
                    ref = hub.files.discover(scope, grant["id"])["files"][0]["id"]
                    result = run(
                        "file_" + suffix[1:],
                        "W35",
                        "What is the codename and retention? Cite the source.",
                        reference=ref,
                    )
                    answer = (result.get("result") or {}).get("text", "")
                    result["grounded"] = "cedar" in answer.lower() and "42" in answer
                    results["checks"].append(result)
                    print(json.dumps(result), flush=True)
                from PIL import Image, ImageDraw, ImageFont

                image = Image.new("RGB", (700, 300), "green")
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("arial.ttf", 72)
                draw.text((60, 100), "CEDAR 42", fill="white", font=font)
                path = root / "fixture.png"
                image.save(path)
                shared = hub.share_image(
                    scope, path, hashlib.sha256(path.read_bytes()).hexdigest()
                )
                result = run(
                    "shared_image",
                    "W33",
                    "Read the large text and identify the background color.",
                    image=shared["id"],
                )
                answer = (result.get("result") or {}).get("text", "").lower()
                result["grounded"] = all(
                    word in answer for word in ("cedar", "42", "green")
                )
                results["checks"].append(result)
                print(json.dumps(result), flush=True)
                result = run(
                    "planner_missing_target",
                    "W36",
                    "Type Cedar in an editor, but no window has been selected.",
                )
                result["grounded"] = bool(
                    (result.get("result") or {}).get("needs_context")
                )
                results["checks"].append(result)
                print(json.dumps(result), flush=True)
            finally:
                hub.close()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    if any(c["status"] != "completed" or not c["grounded"] for c in results["checks"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
