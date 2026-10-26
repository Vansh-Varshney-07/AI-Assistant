"""Regenerate audit summaries from retained files without running Iron Web."""
import ast
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import statistics
import subprocess
import sys
from zipfile import ZipFile
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path.cwd()
OUT = ROOT / "docs/research/iron-web-paper/audit-artifacts"
OUT.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

files = []
for name in ["memory", "tests", "scripts", "requirements"]:
    files.extend(p for p in (ROOT/name).rglob("*") if p.is_file() and p.suffix in {".py", ".txt"} and "__pycache__" not in p.parts)
files += [ROOT/n for n in ["README.md", "config.yaml", "compose.yaml", "pytest.ini", "Test-Wayfinder.ps1"]]
for path in (ROOT/"docs").rglob("*"):
    if not path.is_file() or "research" in path.parts:
        continue
    if path.suffix in {".csv", ".json", ".md", ".xml"}:
        files.append(path)
for base in ["data/repair_backup_20261023", "data/space_backup_20261023"]:
    files.extend(p for p in (ROOT/base).rglob("*") if p.is_file())
for name in [".local/hermes-smoke-results.json", ".local/project-checks.json", ".local/database-recovery-verification.json"]:
    files.append(ROOT/name)
files.extend((ROOT/".local/database-recovery").glob("*/recovery-report.json"))
records = [{"path":p.relative_to(ROOT).as_posix(), "bytes":p.stat().st_size, "sha256":sha(p)}
           for p in sorted(set(files)) if p.exists()]
with (OUT/"artifact_hashes.csv").open("w",encoding="utf-8-sig",newline="") as handle:
    w=csv.DictWriter(handle,fieldnames=["path","bytes","sha256"]);w.writeheader();w.writerows(records)

source_index=[]
for name in ["memory","tests","scripts"]:
    for path in sorted((ROOT/name).rglob("*.py")):
        tree=ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                source_index.append({"path":path.relative_to(ROOT).as_posix(),"symbol":node.name,"line":node.lineno,"end_line":node.end_lineno})
(OUT/"source_index.json").write_text(json.dumps(source_index,indent=2),encoding="utf-8")

summaries=[]
for folder in ["live-validation","nemotron-validation-before-schema","nemotron-validation-schema-rejected","nemotron-validation"]:
    prefix="live-test" if folder=="live-validation" else "nemotron"
    base=ROOT/"docs"/folder
    evidence=json.loads((base/f"{prefix}-evidence.json").read_text(encoding="utf-8"))
    with (base/f"{prefix}-results.csv").open(encoding="utf-8-sig",newline="") as handle:
        csvrows=list(csv.DictReader(handle))
    rows=evidence["results"]
    def comparable(row):
        checks=row.get("checks",{})
        if isinstance(checks,str):checks=json.loads(checks)
        return (row.get("model",""), row.get("test",row.get("name","")),
                row.get("path",""),row.get("namespace",""),row.get("outcome",""),
                json.dumps(checks,sort_keys=True))
    summary={"folder":folder,"run_id":evidence["run"],"csv_rows":len(csvrows),
             "csv_outcomes":dict(Counter(r["outcome"] for r in csvrows)),
             "json_rows":len(rows),"json_outcomes":dict(Counter(r["outcome"] for r in rows)),
             "event_count":len(evidence["events"]),"csv_json_counts_match":len(rows)==len(csvrows),
             "csv_json_case_records_match":Counter(map(comparable,rows))==Counter(map(comparable,csvrows)),
             "csv_sha256":sha(base/f"{prefix}-results.csv"),"json_sha256":sha(base/f"{prefix}-evidence.json"),
             "failed_checks":[{"model":r.get("model"),"test":r.get("name",r.get("test")),
                              "false_checks":[k for k,v in r.get("checks",{}).items() if v is False]}
                             for r in rows if r["outcome"]=="Fail"]}
    if folder!="live-validation":
        summary["grading_disagreements"]=[r.get("name") for r in rows
            if r["outcome"]!=("Pass" if all(r["checks"].values()) else "Fail")]
        series=defaultdict(lambda:defaultdict(list))
        replay_counts=Counter()
        for event in evidence["events"]:
            request=event.get("request",{});response=event.get("response",{})
            diagnostic=response.get("diagnostics",{});hosted=diagnostic.get("hosted",{})
            model=request.get("model",hosted.get("model","unknown"))
            for stage in ["extraction","generation"]:
                trace=hosted.get(stage)
                if not isinstance(trace,dict):continue
                if stage=="extraction" and trace.get("replayed"):
                    replay_counts[model]+=1;continue
                val=trace.get("inference_ms")
                if isinstance(val,(int,float)):series[model][stage+"_inference_ms"].append(val)
            if request.get("mode","retrieve") in {"retrieve","recall"} and isinstance(diagnostic.get("total_ms"),(int,float)):
                series[model]["query_adapter_total_ms"].append(diagnostic["total_ms"])
        summary["observed_timings"]={model:{key:{"n":len(vals),"median":statistics.median(vals)} for key,vals in groups.items()} for model,groups in series.items()}
        summary["excluded_replayed_extraction_traces"]=dict(replay_counts)
        summary["timing_warning"]="Historical event observations, not a controlled benchmark; inference traces include bounded retries; extraction replay traces excluded."
    summaries.append(summary)
(OUT/"retained_run_summary.json").write_text(json.dumps(summaries,indent=2),encoding="utf-8")

paper=ROOT/"docs/research/iron-web-paper/manuscript/Iron_Web_Research_Paper_9_Page_Editing_Draft.docx"
with ZipFile(paper) as z:
    xml=ET.fromstring(z.read("word/document.xml"));ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main","pic":"http://schemas.openxmlformats.org/drawingml/2006/picture"}
    paras=["".join(p.itertext()) for p in xml.findall("./w:body/w:p",ns)]
    doc_check={"sha256":sha(paper),"embedded_pictures":len(xml.findall(".//pic:pic",ns)),
               "tables":len(xml.findall(".//w:tbl",ns)),"repeated_results_headings":sum(p=="4. Results & Discussion" for p in paras)}
git=str(Path.home()/".cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe")
revision=subprocess.check_output([git,"rev-parse","HEAD"],text=True,cwd=ROOT).strip()
manifest={"audit_date":"2026-10-24","assembled_at_utc":datetime.now(timezone.utc).isoformat(),
          "base_commit":revision,"source_identity":"base commit plus artifact_hashes.csv; worktree has pre-existing changes",
          "original_paper":doc_check,"hashed_files":len(records),"indexed_symbols":len(source_index),
          "new_experiments_executed":False,"new_tests_executed":False,"application_code_modified":False,
          "databases_opened_by_audit":False,"original_paper_overwritten":False,
          "access_limits":[".local/tests-relocation-20261024 traversal denied",
                           "hardware CIM inventory denied; GPU spec remains user-reported",
                           "No earlier chat output or files outside the audited project were treated as accessible evidence"],
          "evidence_missing_in_accessible_project":["regression.xml","startup-memory-tests.xml","phase02-tests.xml","real-embedding-smoke.json","memory-spaces-live-evidence.json"],
          "external_sources_checked":["https://github.com/snap-research/locomo/blob/main/LICENSE.txt",
              "https://github.com/xiaowu0162/LongMemEval/blob/main/LICENSE",
              "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned",
              "https://github.com/xiaowu0162/LongMemEval-V2/blob/main/LICENSE",
              "https://huggingface.co/datasets/xiaowu0162/longmemeval-v2/blob/main/README.md",
              "https://arxiv.org/abs/2504.19413v1","https://arxiv.org/abs/2501.13956","https://arxiv.org/abs/2604.21284v1"]}
(OUT/"audit_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps({"hashed_files":len(records),"runs":len(summaries),"paper":doc_check,
                  "final_timings":summaries[-1].get("observed_timings")},indent=2))
