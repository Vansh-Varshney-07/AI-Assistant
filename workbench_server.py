"""Loopback-only manual interface for the existing MemoryEngine. Run with Ctrl+C to stop."""

import argparse
import ipaddress
import json
import os
from pathlib import Path
import secrets
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parent


def wire_value(value):
    """Preserve INT64 values exactly across JavaScript's 53-bit number boundary."""
    if type(value) is int and abs(value) > 2**53 - 1:
        return str(value)
    if isinstance(value, dict):
        return {k: wire_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire_value(v) for v in value]
    return value


STITCH_SCREENS = {
    "home": ("wayfinder_home_command_center_2", "code.html", "Home Command Center 2"),
    "home-1": ("wayfinder_home_command_center_1", "code.html", "Home Command Center 1"),
    "planner": ("wayfinder_planner_today_matrix", "code.html", "Planner Today Matrix"),
    "precision-planner": ("wayfinder_precision_planner_time_matrix", "code.html", "Precision Planner Time Matrix"),
    "notion": ("wayfinder_notion_workspace", "code.html", "Notion Workspace"),
    "workflows": ("wayfinder_workflows_automation_editor", "code.html", "Workflows Automation Editor"),
    "workflows-engine": ("wayfinder_workflows_automation_engine", "code.html", "Workflows Automation Engine"),
    "activity": ("wayfinder_activity_execution_monitor", "code.html", "Activity Execution Monitor"),
    "connections": ("wayfinder_connections_data_bridges_2", "code.html", "Connections Data Bridges 2"),
    "connections-1": ("wayfinder_connections_data_bridges_1", "code.html", "Connections Data Bridges 1"),
    "permissions": ("wayfinder_permissions_security", "code.html", "Permissions & Security"),
}


def get_stitch_screens_catalog():
    return [
        {
            "id": key,
            "title": info[2],
            "folder": info[0],
            "url": f"/screens/{key}",
        }
        for key, info in STITCH_SCREENS.items()
    ]


def resolve_stitch_screen(key):
    if key in STITCH_SCREENS:
        folder, filename, _ = STITCH_SCREENS[key]
        return ROOT / "stitch_wayfinder_ai_desktop_interface" / folder / filename
    # Check if direct path inside stitch folder
    candidate = ROOT / "stitch_wayfinder_ai_desktop_interface" / key
    if candidate.exists() and candidate.is_file():
        return candidate
    if (candidate / "code.html").exists():
        return candidate / "code.html"
    return None


def get_wayfinder_workers():
    import re
    workers_dir = ROOT / "wayfinder" / "workers"
    results = []
    if workers_dir.exists():
        for def_file in sorted(workers_dir.glob("*/definition.yaml")):
            data = {}
            try:
                import yaml
                data = yaml.safe_load(def_file.read_text(encoding="utf-8")) or {}
            except Exception:
                text = def_file.read_text(encoding="utf-8")
                wid = re.search(r"^id:\s*(.+)$", text, re.M)
                wname = re.search(r"^name:\s*(.+)$", text, re.M)
                wstatus = re.search(r"^status:\s*(.+)$", text, re.M)
                wresp = re.search(r"responsibility:\s*>\s*\n((?:\s{2,}.*\n?)+)", text)
                data = {
                    "id": wid.group(1).strip() if wid else def_file.parent.name[:3],
                    "name": wname.group(1).strip() if wname else def_file.parent.name,
                    "status": wstatus.group(1).strip() if wstatus else "fixture-tested",
                    "responsibility": " ".join([l.strip() for l in wresp.group(1).splitlines()]) if wresp else "",
                    "capabilities": [],
                    "denied_capabilities": [],
                }
            if data.get("id"):
                results.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "status": data.get("status", "fixture-tested"),
                    "responsibility": (data.get("responsibility") or "").strip(),
                    "capabilities": data.get("capabilities", []),
                    "denied_capabilities": data.get("denied_capabilities", []),
                })
    return results


class MockWorkbench:
    """Preview-mode workbench adapter allowing UI testing without FalkorDB."""
    def __init__(self):
        import time
        self._spaces = [
            {"memory_space_id": "sp_primary_core", "name": "Primary Core Space"},
            {"memory_space_id": "sp_research_01", "name": "Research Experiment 01"},
        ]
        self._records = {
            "sp_primary_core": [
                {
                    "memory_id": "mem_01hqz882",
                    "content": "Wayfinder assistant uses a three-tier context runtime with hot RAM, evidence cards, and dual-store durable storage.",
                    "memory_space_id": "sp_primary_core",
                    "statuses": ["active"],
                    "types": ["fact"],
                    "created_timestamp": time.time() - 3600,
                    "updated_timestamp": None,
                    "vector_stored": True,
                    "graph_stored": True,
                },
                {
                    "memory_id": "mem_01hqz991",
                    "content": "All external worker mutations require explicit human sign-off as enforced by SecOps rule POL-01.",
                    "memory_space_id": "sp_primary_core",
                    "statuses": ["active"],
                    "types": ["policy"],
                    "created_timestamp": time.time() - 1800,
                    "updated_timestamp": None,
                    "vector_stored": True,
                    "graph_stored": True,
                }
            ],
            "sp_research_01": []
        }
        self.spaces = self

    def status(self):
        return {
            "status": "online (preview mode)",
            "falkordb": "127.0.0.1:6381",
            "qdrant": "embedded-local",
            "extraction_policy": "none",
            "models": ["nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-70b-instruct"]
        }

    def list_spaces(self):
        return self._spaces

    def create(self, body):
        name = body.get("name", "New Space")
        space_id = "sp_" + secrets.token_hex(4)
        new_sp = {"memory_space_id": space_id, "name": name}
        self._spaces.append(new_sp)
        self._records[space_id] = []
        return new_sp

    def inventory(self, memory_space_id):
        return {
            "records": self._records.get(memory_space_id, []),
            "unowned_observation_ids": []
        }

    def run(self, body):
        import time
        prompt = body.get("prompt", "")
        mode = body.get("mode", "retrieve")
        space_id = body.get("memory_space_id", "sp_primary_core")
        stored = None
        if mode in ("store", "claim"):
            mid = "mem_" + secrets.token_hex(4)
            stored = {
                "memory_id": mid,
                "content": prompt,
                "memory_space_id": space_id,
                "statuses": ["active"],
                "types": ["user_prompt"],
                "created_timestamp": time.time(),
                "updated_timestamp": None,
                "vector_stored": True,
                "graph_stored": True,
            }
            if space_id not in self._records:
                self._records[space_id] = []
            self._records[space_id].append(stored)

        retrieved = []
        for r in self._records.get(space_id, []):
            retrieved.append({
                "memory_id": r["memory_id"],
                "content": r["content"],
                "score": 0.91,
                "metadata": {"source": "falkordb_graph"}
            })

        return {
            "ok": True,
            "stored": stored,
            "retrieved": retrieved[: body.get("top_k", 5)],
            "recall": None,
            "assistant": {
                "answer": f"Wayfinder response: Grounded in evidence from '{space_id}'. Processed prompt '{prompt}'.",
                "evidence_status": "grounded",
                "citations": [r["memory_id"] for r in retrieved[:2]]
            },
            "diagnostics": {
                "pipeline_invoked": True,
                "errors": []
            }
        }


def handler_for(workbench, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, value, status=200, kind="application/json; charset=utf-8"):
            encoded = (
                value
                if isinstance(value, bytes)
                else json.dumps(wire_value(value), allow_nan=False).encode("utf-8")
            )
            self.send_response(status)
            csp = (
                "default-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com https://lh3.googleusercontent.com data:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: https://lh3.googleusercontent.com; "
                "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
            )
            for name, content in {
                "Content-Type": kind,
                "Content-Length": str(len(encoded)),
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": csp,
                "Referrer-Policy": "no-referrer",
            }.items():
                self.send_header(name, content)
            self.end_headers()
            self.wfile.write(encoded)

        def local_request(self):
            allowed = {
                f"127.0.0.1:{self.server.server_port}",
                f"localhost:{self.server.server_port}",
            }
            if self.headers.get("Host") not in allowed:
                raise PermissionError("Unrecognized local host.")
            origin = self.headers.get("Origin")
            if origin and origin != "http://" + self.headers["Host"]:
                raise PermissionError("Cross-origin requests are unavailable.")
            if self.headers.get("Sec-Fetch-Site") == "cross-site":
                raise PermissionError("Cross-site requests are unavailable.")

        def do_GET(self):
            try:
                self.local_request()
                path = urlsplit(self.path).path
                files = {
                    "/": ("index.html", "text/html; charset=utf-8"),
                    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                    "/style.css": ("style.css", "text/css; charset=utf-8"),
                }
                if path in files:
                    name, kind = files[path]
                    return self.send(
                        (ROOT / "workbench" / name).read_bytes(), kind=kind
                    )
                if path == "/health":
                    return self.send({"status": "online", "interface": "Wayfinder AI Desktop"})
                if path == "/api/session":
                    return self.send({"token": token})
                if path == "/api/status":
                    return self.send(workbench.status())
                if path == "/api/spaces":
                    return self.send({"spaces": workbench.list_spaces()})
                if path == "/api/memories":
                    query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
                    if (
                        set(query) != {"memory_space_id"}
                        or len(query["memory_space_id"]) != 1
                    ):
                        raise ValueError(
                            "Supply exactly one memory_space_id to inspect records."
                        )
                    return self.send(workbench.inventory(query["memory_space_id"][0]))
                if path == "/api/wayfinder/workers":
                    return self.send({"workers": get_wayfinder_workers()})
                if path == "/screens" or path == "/screens/list":
                    return self.send({"screens": get_stitch_screens_catalog()})
                if path.startswith("/screens/"):
                    screen_key = path[len("/screens/"):].strip("/")
                    screen_file = resolve_stitch_screen(screen_key)
                    if screen_file and screen_file.exists():
                        mime = "text/html; charset=utf-8" if screen_file.suffix == ".html" else "image/png"
                        return self.send(screen_file.read_bytes(), kind=mime)
                    return self.send({"error": f"Screen '{screen_key}' not found."}, 404)
                self.send({"error": "Unknown endpoint"}, 404)
            except PermissionError as error:
                self.send({"error": str(error)}, 403)
            except ValueError as error:
                self.send({"error": str(error)}, 400)
            except Exception:
                self.send(
                    {
                        "error": "Storage inspection failed; inspect local service availability."
                    },
                    503,
                )

        def do_POST(self):
            try:
                self.local_request()
                if not secrets.compare_digest(
                    self.headers.get("X-Workbench-Token", ""), token
                ):
                    raise PermissionError(
                        "Workbench session token required; reload the local page."
                    )
                path = urlsplit(self.path).path
                if path not in {"/api/prompt", "/api/stop", "/api/spaces"}:
                    return self.send({"error": "Unknown endpoint"}, 404)
                if (
                    self.headers.get("Content-Type", "").split(";")[0]
                    != "application/json"
                ):
                    return self.send({"error": "JSON required"}, 415)
                size = int(self.headers.get("Content-Length", "0"))
                if not 1 <= size <= 131072:
                    return self.send(
                        {"error": "Request must contain 1–131072 bytes"}, 413
                    )

                def invalid(value):
                    raise ValueError("Nonfinite JSON values are unavailable.")

                body = json.loads(self.rfile.read(size), parse_constant=invalid)
                if path == "/api/spaces":
                    return self.send(workbench.spaces.create(body), 201)
                if path == "/api/stop":
                    if body != {}:
                        raise ValueError("Stop takes an empty object.")
                    self.send({"status": "stopping"})
                    Thread(target=self.server.shutdown, daemon=True).start()
                    return
                result = workbench.run(body)
                self.send(result, 200 if result["ok"] else 409)
            except PermissionError as error:
                self.send({"error": str(error)}, 403)
            except (ValueError, TypeError) as error:
                self.send({"error": str(error)}, 400)
            except Exception:
                self.send({"error": "Request failed; no completion is asserted."}, 503)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    parser.add_argument("--port", type=int, default=3352)
    parser.add_argument(
        "--nvidia",
        action="store_true",
        help="Explicitly enable the two Nemotron models using NVIDIA_API_KEY.",
    )
    parser.add_argument(
        "--key-file",
        type=Path,
        help="Optional existing .env file; only NVIDIA_API_KEY is read.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Launch Wayfinder AI desktop interface in preview mode without requiring live FalkorDB.",
    )
    args = parser.parse_args()

    if args.preview:
        server = ThreadingHTTPServer(
            ("127.0.0.1", args.port),
            handler_for(MockWorkbench(), secrets.token_hex(32)),
        )
        server.daemon_threads = False
        print(
            f"Wayfinder AI Desktop Interface [Preview Mode]: http://127.0.0.1:{server.server_port}",
            flush=True,
        )
        print(
            "Serving all 10 Stitch screens + 16 Wayfinder workers + simulated memory engine. Ctrl+C to stop.",
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return

    # Embeddings remain local and offline even when hosted text inference is enabled.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    import yaml
    from memory.engine import MemoryEngine
    from memory.workbench import Workbench

    config = yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}
    if config.get("extraction_policy", "none") != "none":
        parser.error("This local-only workbench requires extraction_policy: none.")
    host = os.environ.get(
        "FALKORDB_HOST", config.get("falkordb", {}).get("host", "127.0.0.1")
    )
    try:
        loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = False
    if not loopback:
        parser.error("This local-only workbench requires loopback FalkorDB.")
    hosted_clients = {}
    if args.nvidia:
        from openai import OpenAI
        from memory.shared.hosted import NEMOTRON_MODELS

        key = os.environ.get("NVIDIA_API_KEY")
        if not key and args.key_file:
            from dotenv import dotenv_values

            key = dotenv_values(args.key_file).get("NVIDIA_API_KEY")
        if not key:
            parser.error(
                "NVIDIA_API_KEY is required for --nvidia. The key is never printed."
            )
        hosted_clients = {
            model: OpenAI(
                api_key=key,
                base_url="https://integrate.api.nvidia.com/v1",
                timeout=60,
                max_retries=1,
            )
            for model in NEMOTRON_MODELS
        }
    try:
        with MemoryEngine(config=str(args.config.resolve())) as engine:
            server = ThreadingHTTPServer(
                ("127.0.0.1", args.port),
                handler_for(
                    Workbench(engine, hosted_clients=hosted_clients),
                    secrets.token_hex(32),
                ),
            )
            server.daemon_threads = False
            print(
                f"Wayfinder AI Desktop Interface: http://127.0.0.1:{server.server_port}",
                flush=True,
            )
            print(
                "Nemotron enabled for explicit model selections; embeddings/storage stay local. Ctrl+C to stop."
                if hosted_clients
                else "MemoryEngine active. Ctrl+C to stop.",
                flush=True,
            )
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
    except Exception as error:
        print(f"Warning: Engine connection failed ({type(error).__name__}).", flush=True)
        print("Tip: Run with '--preview' to test the Wayfinder UI without live FalkorDB.\n", flush=True)
        parser.exit(
            1,
            f"Workbench startup failed ({type(error).__name__}). Check local FalkorDB, config and exclusive Qdrant ownership.\n",
        )


if __name__ == "__main__":
    main()
