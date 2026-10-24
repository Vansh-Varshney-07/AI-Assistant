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
            for name, content in {
                "Content-Type": kind,
                "Content-Length": str(len(encoded)),
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
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
                    return self.send({"status": "online"})
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
    args = parser.parse_args()
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
                f"Memory Testing Workbench: http://127.0.0.1:{server.server_port}",
                flush=True,
            )
            print(
                "Nemotron enabled for explicit model selections; embeddings/storage stay local. Ctrl+C to stop."
                if hosted_clients
                else "Evidence only. Ctrl+C to stop.",
                flush=True,
            )
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
    except Exception as error:
        parser.exit(
            1,
            f"Workbench startup failed ({type(error).__name__}). Check local FalkorDB, config and exclusive Qdrant ownership.\n",
        )


if __name__ == "__main__":
    main()
