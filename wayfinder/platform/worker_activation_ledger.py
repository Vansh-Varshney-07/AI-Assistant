"""Worker activation ledger — static truth for all 47 roles."""
from typing import Any
import json

# Ledger: each entry has id, binding, mode, available, reason, live_qualified
LEDGER: list[dict[str, Any]] = [
    # --- Source-context workers (bound via worker_bindings.py) ---
    {"id":"W01","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W03","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W06","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W07","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W09","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W10","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W12","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W13","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W14","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W15","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W16","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W18","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W19","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    {"id":"W24","binding":"hermes_context","mode":"source_context","available":True,"reason":"YAML definition; context-provided runs via start_context()","live_qualified":False},
    # --- Tool-requiring workers (excluded from tools-closed path) ---
    {"id":"W08","binding":"none","mode":"tool_requiring","available":False,"reason":"Requires live tool grants; excluded from tools-closed source-context path","live_qualified":False},
    {"id":"W11","binding":"none","mode":"tool_requiring","available":False,"reason":"Requires live tool grants; excluded from tools-closed source-context path","live_qualified":False},
    # --- Deterministic platform services ---
    {"id":"W02","binding":"context_gateway","mode":"trusted_service","available":True,"reason":"ContextGateway: FalkorDB read; no Hermes delegation","live_qualified":True},
    {"id":"W04","binding":"atlas_search","mode":"trusted_service","available":True,"reason":"Atlas search: read-only catalog","live_qualified":True},
    {"id":"W05","binding":"workflow_coordinator","mode":"trusted_service","available":True,"reason":"Workflow coordinator via workflows.py","live_qualified":True},
    {"id":"W25","binding":"git_service","mode":"trusted_service","available":True,"reason":"Git read/diff; scoped path; no push","live_qualified":True},
    {"id":"W26","binding":"activity_csv","mode":"trusted_service","available":True,"reason":"Activity log CSV reader","live_qualified":True},
    {"id":"W34","binding":"file_broker","mode":"trusted_service","available":True,"reason":"FileBroker: deterministic file identity","live_qualified":True},
    {"id":"W38","binding":"context_gateway","mode":"trusted_service","available":True,"reason":"ContextGateway write: memory proposals only","live_qualified":True},
    {"id":"W41","binding":"conflicts_service","mode":"trusted_service","available":True,"reason":"Conflict detection service","live_qualified":True},
    {"id":"W42","binding":"maintenance_service","mode":"trusted_service","available":True,"reason":"Maintenance service","live_qualified":True},
    {"id":"W44","binding":"recovery_service","mode":"trusted_service","available":True,"reason":"Recovery/draft cache service","live_qualified":True},
    {"id":"W46","binding":"action_audit","mode":"trusted_service","available":True,"reason":"Action audit log","live_qualified":True},
    {"id":"W47","binding":"evaluation_service","mode":"trusted_service","available":True,"reason":"Evaluation/quality check service","live_qualified":True},
    # --- Desktop workers ---
    {"id":"W33","binding":"explicit_image","mode":"desktop_role","available":True,"reason":"Explicit image analysis variant","live_qualified":False},
    {"id":"W35","binding":"hermes_file_analysis","mode":"desktop_role","available":True,"reason":"Hermes file analysis; qualified via CapabilityCatalog","live_qualified":True},
    {"id":"W36","binding":"plan_proposal","mode":"desktop_role","available":True,"reason":"Desktop plan proposal","live_qualified":False},
    # --- Gated/disconnected ---
    {"id":"W37","binding":"none","mode":"gated","available":False,"reason":"No qualified native driver; W37 stays disconnected","live_qualified":False},
    # --- Missing explicit mappings (documented as unavailable) ---
    {"id":"W17","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W20","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W21","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W22","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W23","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W27","binding":"none","mode":"unmapped","available":False,"reason":"Fitness/habit tracking; deferred (X01.04)","live_qualified":False},
    {"id":"W28","binding":"none","mode":"unmapped","available":False,"reason":"Fitness/habit tracking; deferred (X01.04)","live_qualified":False},
    {"id":"W29","binding":"none","mode":"unmapped","available":False,"reason":"Communications worker; no explicit contract","live_qualified":False},
    {"id":"W30","binding":"none","mode":"unmapped","available":False,"reason":"Communications worker; no explicit contract","live_qualified":False},
    {"id":"W31","binding":"none","mode":"unmapped","available":False,"reason":"Communications worker; no explicit contract","live_qualified":False},
    {"id":"W32","binding":"none","mode":"unmapped","available":False,"reason":"Communications worker; no explicit contract","live_qualified":False},
    {"id":"W39","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W40","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
    {"id":"W45","binding":"none","mode":"unmapped","available":False,"reason":"No explicit mapping; requires further specification","live_qualified":False},
]

def get_ledger() -> list[dict[str, Any]]:
    return LEDGER

def get_role(worker_id: str) -> dict[str, Any] | None:
    for entry in LEDGER:
        if entry["id"] == worker_id:
            return entry
    return None

def available_source_context_roles() -> list[str]:
    return [e["id"] for e in LEDGER if e["mode"] == "source_context" and e["available"]]

def available_trusted_services() -> list[str]:
    return [e["id"] for e in LEDGER if e["mode"] == "trusted_service" and e["available"]]
