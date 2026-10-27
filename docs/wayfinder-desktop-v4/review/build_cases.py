"""Translate v3 test designs to v4 scope; all implementation cases stay Not run."""

import csv
import re

from review import ROOT, csv_write

old = ROOT.parent / "wayfinder-desktop-v3"
features = {
    1: (1, "chat"), 2: (1, "runtime"), 3: (1, "chat"), 4: (1, "chat"),
    5: (1, "runtime"), 6: (1, "runtime"), 7: (1, "chat"), 8: (2, "documents"),
    9: (2, "memory"), 10: (2, "memory"), 11: (3, "google_read"), 12: (4, "workflows"),
    13: (3, "local_tasks"), 14: (7, "google_write"), 15: (4, "workflows"), 16: (4, "workflows"),
    17: (5, "scheduler"), 18: (5, "scheduler"), 19: (6, "skills"), 20: (2, "memory"),
    21: (3, "google_read"), 22: (2, "documents"), 23: (1, "runtime"), 24: (2, "documents"),
    25: (1, "runtime"), 26: (1, "chat"), 27: (1, "chat"), 28: (1, "chat"),
    29: (1, "chat"), 30: (1, "chat"), 31: (3, "runtime"), 32: (1, "chat"),
    33: (6, "agents"), 34: (2, "memory"), 35: (5, "quick_chat"), 36: (1, "runtime"),
}
optional = {"google_write", "communication", "native_desktop", "coding_effect", "background_mode", "selected_image"}
fields = ["id", "source", "finding", "release", "feature", "variant", "requirement", "excluded_if", "scenario", "expected_result", "owner", "evidence_tier", "status"]
rows = []


def add(case_id, source, finding, release, feature, scenario, expected, tier, excluded=""):
    rows.append(dict(id=case_id, source=source, finding=finding, release=f"R{release}", feature=feature,
                     variant=f"optional:{feature}" if feature in optional else "core",
                     requirement="Required when advertised" if feature in optional else "Required",
                     excluded_if=excluded, scenario=scenario, expected_result=expected,
                     owner="UI + platform; qualification by relevant provider/worker owner",
                     evidence_tier=tier, status="Not run"))


for case in csv.DictReader((old / "audit/SUPPLEMENTAL-CASES.csv").open(encoding="utf-8")):
    number = int(case["finding"][1:])
    release, feature = features[number]
    scenario, expected = case["scenario"], case["expected_result"]
    if case["id"] == "F10-T2":
        scenario = "Edit the reviewed memory payload or change target space before dispatch"
    if number == 13:
        scenario = ("Independently edit provider task and its one-time local copy then refresh both views"
                    if case["id"].endswith("T1") else
                    "Complete/delete a local copy while provider task is still pending then refresh")
        expected = "No sync/writeback or local resurrection; raw/canonical provider status, observed time and versions are explicit"
    if number == 14:
        scenario = ("Lose acknowledgement after the exact advertised test-account operation"
                    if case["id"].endswith("T1") else
                    "Add an unrelated matching item before reconciling the advertised operation")
    if number == 21:
        expected = "Preserve date-only due date; timed reminders stay unsupported here and cause no hidden scheduler/event write"
    if number == 31 and case["id"].endswith("T2"):
        release = 7
        scenario = "Evaluate an R7 core build with all native/send/write optional modules excluded"
        expected = "Required core and optional-denial tests remain required; omitted module tests need an explicit exclusion reason, never a fake pass"
    if number == 32:
        expected = "Explain live research/notes connector is deferred; no fabricated live sources, implicit browsing or alternate unscoped connector"
    tier = "Contract/fault injection plus appropriate live tier from C23"
    if number in {26, 27, 28, 29, 30, 35}:
        tier = "Packaged Windows app; actual keyboard/IME/accessibility walkthrough"
    if number in {11, 21}:
        tier = "Live Google test account plus synthetic boundary fixtures"
    if number == 20:
        tier = "Held-out neural memory evaluation in isolated storage"
    add(case["id"], "v3 supplemental; scope amendments recorded in builder", case["finding"], release,
        feature, scenario, expected, tier)

for case in csv.DictReader((old / "ACCEPTANCE.csv").open(encoding="utf-8")):
    release = int(case["release"][1:])
    feature = {1: "chat", 2: "memory", 3: "google_read", 4: "workflows", 5: "scheduler", 6: "skills", 7: "project_review"}[release]
    excluded = ""
    if case["id"] == "R3-04":
        feature = "local_tasks"
    if case["id"] == "R3-05":
        release, feature = 7, "google_write"
    if case["id"] == "R5-04":
        feature = "quick_chat"
    if case["id"] == "R7-01":
        feature = "coding_effect"
    if case["id"] == "R7-02":
        feature = "communication"
    if case["id"] == "R7-03":
        feature = "google_write"
    if case["id"] == "R7-04":
        excluded = "native_desktop"
    if case["id"] == "R7-05":
        feature = "native_desktop"
    add(case["id"], "v3 acceptance; write cases explicitly moved to R7 optional", "", release,
        feature, case["scenario"], case["expected_result"], case["evidence_tier"], excluded)

for line in (ROOT / "SECOND-ORDER.md").read_text(encoding="utf-8").splitlines():
    if not re.match(r"\| N\d+ \|", line):
        continue
    number, introduced, path, containment, regression = [part.strip() for part in line.strip("|").split("|")]
    n = int(number[1:])
    release, feature = (1, "runtime")
    if n in {7, 9, 10, 11}:
        release, feature = 2, "memory" if n in {7, 9} else "documents"
    if n in {12, 15, 16, 28}:
        release, feature = 7, "google_write"
    if n in {13, 14}:
        release, feature = 3, "local_tasks" if n == 13 else "google_read"
    if n == 17:
        release, feature = 6, "skills"
    if n in {18, 19, 20, 21}:
        release, feature = 5 if n != 21 else 4, "scheduler" if n != 21 else "workflows"
    if n == 22:
        release, feature = 7, "project_review"
    if n == 23:
        release, feature = 5, "quick_chat"
    if n == 29:
        release, feature = 2, "memory"
    add(number + "-T1", "v4 second-order review", number, release, feature,
        regression + "; risk: " + path, containment,
        "Contract/fault injection; real UI/provider tier where applicable")

add("R3-NOWRITE", "v4 scope correction", "F13;F31", 3, "google_read",
    "Attempt provider write from UI and direct service intent in core build",
    "Write surfaces absent and final handler denies the unadvertised/unqualified operation; local task still works",
    "Packaged app plus service boundary", "google_write")
add("R7-READ", "v4 core walkthrough", "N22", 7, "project_review",
    "Inspect bounded status/diff in a disposable granted repository",
    "Actual scoped evidence, no external helpers/hooks, execution or writes; unsafe configuration/path denied",
    "Disposable repository plus packaged UI")
add("R1-NOSAVE", "v4 storage floor", "F34;N02", 1, "runtime",
    "Fail disk writes at host journal, atomic acceptance and final persistence boundaries",
    "No false accepted/saved/final receipt; bounded draft/recovery and no unreserved model dispatch",
    "Disposable storage fault injection")
add("R5-BACKGROUND", "v4 optional mode", "N20", 5, "background_mode",
    "Enable background, close UI, then explicitly Quit with shared host and stale callback",
    "Only valid read occurrence admits after close; Quit fence rejects later callback and does not kill shared host",
    "Installed scheduler plus packaged lifecycle; isolated data")
add("R7-IMAGE", "v4 optional selected input", "", 7, "selected_image",
    "Analyze an explicitly attached synthetic image through its qualified binding",
    "Only selected image disclosed; no screen capture, clipboard access, desktop windows or native action",
    "Synthetic selected artifact and live qualified image binding")
assert len({row["id"] for row in rows}) == len(rows)
csv_write(ROOT / "ACCEPTANCE.csv", fields, rows)

names = {1: "Orchestrator", 2: "Context Retriever", 4: "Capability Scout", 5: "Workflow Coordinator",
         17: "Reminder-related role (formal name unresolved)", 25: "Coding-related role (formal name unresolved)",
         26: "Activity Analyst", 32: "Message-action role (formal name unresolved)",
         33: "Desktop Context Analyst", 34: "File Discovery Worker", 35: "Local File Analyst",
         36: "Desktop Action Planner", 37: "Desktop Action Worker", 38: "Memory Query Worker",
         41: "Memory Conflict Analyst integration", 42: "Memory Maintenance Worker integration",
         44: "Workflow Recovery Worker", 45: "Security advisory role (formal name unresolved)",
         46: "Action Auditor", 47: "Workflow Evaluator infrastructure"}
infra = {2, 4, 5, 26, 37, 38, 41, 42, 44, 46, 47}
inventory = []
for number in range(1, 48):
    inventory.append(dict(id=f"W{number:02}", supplied_name=names.get(number, "Unresolved numbered mapping"),
                          naming_basis="Supplied ownership brief" if number in names else "No formal numbered contract in inspected basis",
                          owner="Platform integration" if number in infra else "Worker configuration owner",
                          binding_status="Unverified; reconcile actual binding/version before availability",
                          product_scope="Deferred fitness" if number == 26 else "Optional disabled image/native" if number in {33, 36, 37} else "See WORKER-SURFACES.md; unresolved IDs unavailable"))
csv_write(ROOT / "WORKER-COVERAGE.csv", list(inventory[0]), inventory)
print(f"Generated {len(rows)} Not-run acceptance cases and {len(inventory)} unqualified coverage rows")
