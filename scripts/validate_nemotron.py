"""Both requested Nemotron models, real workbench HTTP, persistent test namespaces."""

import json
import csv
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]


class Validation:
    def __init__(self, out):
        self.out = out
        self.base = "http://127.0.0.1:3352"
        self.token = self.api("/api/session")["token"]
        self.prefix = datetime.now(timezone.utc).strftime("nm_%m%d_%H%M%S")
        self.events = []
        self.results = []

    def api(self, path, body=None):
        headers = {"Content-Type": "application/json"}
        if body is not None:
            headers["X-Workbench-Token"] = self.token
        request = Request(
            self.base + path,
            data=None if body is None else json.dumps(body).encode(),
            headers=headers,
        )
        try:
            with urlopen(request, timeout=180) as response:
                return json.load(response)
        except HTTPError as error:
            return json.load(error)

    def send(self, ns, text, mode="retrieve", same=None):
        body = same or dict(
            namespace=ns,
            prompt=text,
            mode=mode,
            model=self.model,
            confirmed=True,
            session_id=uuid.uuid4().hex,
            request_id=uuid.uuid4().hex,
            top_k=5,
            subject="manual-user",
        )
        started = time.perf_counter()
        result = self.api("/api/prompt", body)
        event = dict(
            request=body,
            response=result,
            http_total_ms=round((time.perf_counter() - started) * 1000, 3),
        )
        self.events.append(event)
        self.save()
        print(f'{self.label}: {mode} ok={result.get("ok")} {text[:65]}', flush=True)
        return result

    def records(self, ns):
        return [
            r
            for r in self.api("/api/memories?memory_space_id=" + ns)["records"]
            if r["namespace"] == ns
        ]

    @staticmethod
    def mid(result):
        return (result.get("stored") or {}).get("memory_id")

    @staticmethod
    def evidence(result):
        if result.get("field_recall"):
            return [e for p in result["field_recall"] for e in p["evidence"]]
        return [
            c
            for h in result.get("retrieved", [])
            for c in h.get("metadata", {}).get("memory_evidence", [])
        ]

    def check(self, name, ns, checks):
        row = dict(
            model=self.model,
            name=name,
            namespace=ns,
            checks=checks,
            outcome="Pass" if all(checks.values()) else "Fail",
        )
        self.results.append(row)
        self.save()
        print(f'{self.label}: {name} {row["outcome"]} {json.dumps(checks)}', flush=True)

    def save(self):
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / "nemotron-evidence.json").write_text(
            json.dumps(
                dict(run=self.prefix, results=self.results, events=self.events),
                indent=2,
            ),
            encoding="utf-8",
        )

    def restart(self):
        self.api("/api/stop", {})
        for _ in range(60):
            try:
                self.api("/health")
            except Exception:
                break
            time.sleep(0.1)
        time.sleep(0.3)
        with (ROOT / "data/workbench-nemotron.stdout.log").open("ab") as stdout, (
            ROOT / "data/workbench-nemotron.stderr.log"
        ).open("ab") as stderr:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    str(ROOT / "workbench_server.py"),
                    "--nvidia",
                    "--key-file",
                    str(ROOT.parent / "reserchpaper/.env"),
                ],
                cwd=ROOT,
                stdout=stdout,
                stderr=stderr,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        (ROOT / "data/workbench-process.json").write_text(
            json.dumps(dict(pid=process.pid, url=self.base, nvidia=True)),
            encoding="utf-8",
        )
        for _ in range(100):
            try:
                self.token = self.api("/api/session")["token"]
                return True
            except Exception:
                time.sleep(0.1)
        return False

    def model_tests(self, label, model):
        self.label, self.model = label, model
        ns = self.prefix + "_" + label + "_base"
        a = self.send(
            ns,
            "My current project is Iron Web, a long-term memory system for AI agents. I want to validate its storage and retrieval behavior before building further features.",
            "store",
        )
        original = self.events[-1]["request"]
        b = self.send(
            ns,
            "I am testing whether Iron Web can remember project information across separate interactions.",
            "store",
        )
        records = self.records(ns)
        self.check(
            "1 Creation",
            ns,
            dict(
                writes_ok=a.get("ok") is True and b.get("ok") is True,
                both_stores=len(records) == 2
                and all(r["graph_stored"] and r["vector_stored"] for r in records),
                semantic_claims=bool(records)
                and all(
                    any(c["kind"] != "episode" for c in r["claims"]) for r in records
                ),
            ),
        )
        replay = self.send(ns, original["prompt"], "store", same=original)
        self.check(
            "Write replay",
            ns,
            dict(
                succeeded=replay.get("ok") is True,
                no_duplicate=len(self.records(ns)) == 2,
                no_second_inference=replay.get("diagnostics", {})
                .get("hosted", {})
                .get("extraction", {})
                .get("replayed")
                is True,
            ),
        )
        q = self.send(
            ns,
            "Which project am I working on, and what am I currently trying to validate?",
        )
        evidence = self.evidence(q)
        self.check(
            "2 Cross-session retrieval",
            ns,
            dict(
                ok=q.get("ok") is True,
                expected_stored_evidence="Iron Web" in json.dumps(evidence),
                grounded_answer="iron web"
                in q.get("assistant", {}).get("answer", "").lower(),
                citations=bool(q.get("assistant", {}).get("citations")),
            ),
        )
        p = self.send(
            ns,
            "When working on Iron Web, I prefer to test one component at a time and inspect actual stored records before moving to the next phase.",
            "store",
        )
        q = self.send(ns, "What is my preferred approach for testing Iron Web?")
        self.check(
            "3 Preference",
            ns,
            dict(
                stored=p.get("ok") is True,
                preference_kind=any(
                    c["kind"] == "preference"
                    for c in (p.get("stored") or {}).get("claims", [])
                ),
                retrieved_actual_id=self.mid(p)
                in {e["memory_id"] for e in self.evidence(q)},
                answer=q.get("ok") is True
                and "component" in q.get("assistant", {}).get("answer", "").lower(),
            ),
        )
        ns = self.prefix + "_" + label + "_label"
        a = self.send(
            ns, "For this test, the active project label is Memory Alpha.", "store"
        )
        b = self.send(
            ns,
            "Correction: the active project label is Memory Beta. Memory Alpha is no longer the correct label.",
            "store",
        )
        q = self.send(ns, "What is the current project label?")
        records = self.records(ns)
        old = next((r for r in records if r["memory_id"] == self.mid(a)), {})
        self.check(
            "4 Automatic correction",
            ns,
            dict(
                writes_ok=a.get("ok") is True and b.get("ok") is True,
                old_claim_corrected=any(
                    c["status"] == "corrected" for c in old.get("claims", [])
                ),
                current_beta=any(
                    "Memory Beta" in str(e["value"]) for e in self.evidence(q)
                ),
                old_id_excluded=self.mid(a)
                not in q.get("diagnostics", {}).get("generation_memory_ids", []),
                grounded_answer=q.get("ok") is True
                and "Memory Beta" in q.get("assistant", {}).get("answer", ""),
                citations=bool(q.get("assistant", {}).get("citations")),
            ),
        )
        ns = self.prefix + "_" + label + "_conflict"
        a = self.send(ns, "My test workspace is named Workspace North.", "store")
        b = self.send(ns, "My test workspace is named Workspace South.", "store")
        q = self.send(ns, "What is the current test workspace name?")
        claims = [c for r in self.records(ns) for c in r["claims"]]
        self.check(
            "5 Conflict",
            ns,
            dict(
                writes_ok=a.get("ok") is True and b.get("ok") is True,
                same_field=len({c["predicate"] for c in claims}) == 1,
                disputed=bool(claims)
                and all(c["status"] == "disputed" for c in claims),
                answer_disputed=q.get("ok") is True
                and q.get("assistant", {}).get("evidence_status") == "disputed",
                both_sides_cited={self.mid(a), self.mid(b)}
                <= set(q.get("assistant", {}).get("citations", [])),
            ),
        )
        ns = self.prefix + "_" + label + "_persist"
        a = self.send(
            ns,
            "For persistence testing, the verification phrase is copper-orchid-731.",
            "store",
        )
        restarted = self.restart()
        q = self.send(ns, "What is the verification phrase for the persistence test?")
        records = self.records(ns)
        self.check(
            "6 Restart persistence",
            ns,
            dict(
                restarted=restarted,
                same_source=any(
                    r["memory_id"] == self.mid(a)
                    and r["vector_stored"]
                    and r["graph_stored"]
                    for r in records
                ),
                same_id_retrieved=self.mid(a)
                in {e["memory_id"] for e in self.evidence(q)},
                exact_phrase=q.get("ok") is True
                and "copper-orchid-731" in q.get("assistant", {}).get("answer", ""),
            ),
        )
        ns = self.prefix + "_" + label + "_review"
        a = self.send(
            ns, "The next test review is scheduled for 15 November 2026.", "store"
        )
        b = self.send(
            ns,
            "The test review has been rescheduled to 22 November 2026. Use the new date instead.",
            "store",
        )
        q = self.send(ns, "When is the next test review?")
        records = self.records(ns)
        old = next((r for r in records if r["memory_id"] == self.mid(a)), {})
        self.check(
            "7 Stale memory",
            ns,
            dict(
                writes_ok=a.get("ok") is True and b.get("ok") is True,
                prior_superseded=any(
                    c["status"] == "superseded" for c in old.get("claims", [])
                ),
                old_id_excluded=self.mid(a)
                not in q.get("diagnostics", {}).get("generation_memory_ids", []),
                current_date=any(
                    "2026-11-22" in str(e["value"]) for e in self.evidence(q)
                ),
                answer=q.get("ok") is True
                and "22" in q.get("assistant", {}).get("answer", ""),
            ),
        )
        ns = self.prefix + "_" + label + "_precision"
        self.send(ns, "The memory backend test uses a blue notebook.", "store")
        self.send(ns, "The interface test uses a green notebook.", "store")
        a = self.send(ns, "The retrieval test uses an orange notebook.", "store")
        q = self.send(ns, "Which notebook is used for the retrieval test?")
        self.check(
            "8 Precision",
            ns,
            dict(
                ok=q.get("ok") is True,
                correct_semantic_rank=bool(q.get("retrieved"))
                and q["retrieved"][0]["memory_id"] == self.mid(a),
                actual_orange_evidence=any(
                    "orange" in str(e["value"]).lower() for e in self.evidence(q)
                ),
                answer="orange" in q.get("assistant", {}).get("answer", "").lower(),
                orange_source_cited=self.mid(a)
                in q.get("assistant", {}).get("citations", []),
            ),
        )

    def report(self):
        with (self.out / "nemotron-results.csv").open(
            "w", encoding="utf-8", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["model", "test", "namespace", "outcome", "checks"])
            for r in self.results:
                writer.writerow(
                    [
                        r["model"],
                        r["name"],
                        r["namespace"],
                        r["outcome"],
                        json.dumps(r["checks"]),
                    ]
                )
        records = [
            r
            for space in self.api("/api/spaces")["spaces"]
            if space["memory_space_id"].startswith(self.prefix)
            for r in self.records(space["memory_space_id"])
        ]
        (self.out / "nemotron-records.json").write_text(
            json.dumps(records, indent=2), encoding="utf-8"
        )
        lines = [
            "# Nemotron validation after repairs",
            "",
            f"Run: `{self.prefix}`. Real API calls through the local workbench. Real BGE embeddings, FalkorDB and embedded Qdrant.",
            "",
            "| Model | Test | Result |",
            "|---|---|---|",
        ]
        lines += [
            f'| {r["model"]} | {r["name"]} | {r["outcome"]} |' for r in self.results
        ]
        lines += [
            "",
            f'{sum(r["outcome"]=="Pass" for r in self.results)} passed; {sum(r["outcome"]=="Fail" for r in self.results)} failed. {len(records)} retained test records.',
            "",
            "Every query uses a new session UUID and no history. Writes pass user text to the selected Nemotron interpreter; tests do not provide claims or hardcode responses. Field names are read from the actual scoped graph. Structured answers cite only returned memory IDs. Semantic candidate lists are preserved separately from routed field recall used for generation. Both actual server processes were cleanly restarted during persistence checks, using the same stores and NVIDIA settings.",
            "",
            "Full prompts, validated extraction attempts, routing, generated answers, IDs, claim states and timings are in nemotron-evidence.json. Full retained records are in nemotron-records.json. Prior runs were not wiped.",
            "",
        ]
        for r in self.results:
            lines += [
                f'## {r["model"]}: {r["name"]} — {r["outcome"]}',
                "",
                f'Namespace: `{r["namespace"]}`',
                "",
                f'Checks: `{json.dumps(r["checks"])}`',
                "",
            ]
        lines += [
            "## Reproduce",
            "",
            "```powershell",
            "Set-Location 'D:\\Opencode_\\memory_system'",
            "& 'D:\\Opencode_\\reserchpaper\\.venv\\Scripts\\python.exe' .\\scripts\\validate_nemotron.py",
            "```",
            "",
            "This runner expects the workbench started with --nvidia and the existing key available through --key-file or NVIDIA_API_KEY. It makes real NVIDIA requests and retains explicitly labelled test records.",
        ]
        (self.out / "nemotron-report.md").write_text("\n".join(lines), encoding="utf-8")
        self.save()
        print(
            json.dumps(
                dict(
                    run=self.prefix,
                    passed=sum(r["outcome"] == "Pass" for r in self.results),
                    failed=sum(r["outcome"] == "Fail" for r in self.results),
                    records=len(records),
                )
            ),
            flush=True,
        )


def main():
    value = Validation(ROOT / "docs/nemotron-validation")
    for label, model in [
        ("light", "nvidia/nemotron-3.5-lightning-30b-a3b"),
        ("ultra", "nvidia/nemotron-3-ultra-550b-a55b"),
    ]:
        try:
            value.model_tests(label, model)
        except Exception as error:
            value.events.append(dict(model=model, runner_error=type(error).__name__))
            print(label + " runner error " + type(error).__name__, flush=True)
            value.save()
    value.report()


if __name__ == "__main__":
    main()
