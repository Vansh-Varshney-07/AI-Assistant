"""Loopback-only, capability-authenticated desktop transport."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from wayfinder.service import AccessDenied, StaleContext


def wire(value):
    if (
        isinstance(value, int)
        and not isinstance(value, bool)
        and abs(value) > 2**53 - 1
    ):
        return str(value)
    if isinstance(value, dict):
        return {k: wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(v) for v in value]
    return value


def serve(service):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # No credentials, prompts or source data in request logs.

        def reply(self, code, value):
            raw = json.dumps(wire(value), ensure_ascii=False, allow_nan=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            self.reply(405, dict(error="Use the authenticated desktop API."))

        def do_POST(self):
            try:
                if (
                    self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}"
                    or self.headers.get("Origin")
                    or self.headers.get("Sec-Fetch-Site")
                ):
                    raise AccessDenied("Browser requests are not permitted.")
                token = self.headers.get("Authorization", "")
                if not token.startswith("Bearer "):
                    raise AccessDenied("Authentication required.")
                identity = service.authenticate(token[7:])
                # Deny roles before reading a body or touching memory.
                service.authorize(identity)
                if self.headers.get("Content-Type") != "application/json":
                    raise ValueError("JSON content type required.")
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 131072:
                    raise ValueError("Request too large or empty.")
                body = json.loads(self.rfile.read(length))
                operation = self.path.removeprefix("/v2/")
                if self.path != "/v2/" + operation:
                    raise ValueError("Unknown endpoint.")
                self.reply(
                    200, dict(ok=True, data=service.call(identity, operation, body))
                )
            except AccessDenied as error:
                self.reply(403, dict(ok=False, error=str(error)))
            except StaleContext as error:
                self.reply(409, dict(ok=False, error=str(error)))
            except (ValueError, TypeError) as error:
                # Pydantic errors can echo inputs. Do not return their full text.
                message = (
                    str(error)
                    if type(error) is ValueError
                    else "Invalid request schema."
                )
                self.reply(400, dict(ok=False, error=message))
            except Exception:
                self.reply(
                    503,
                    dict(
                        ok=False,
                        error="Storage unavailable or operation unconfirmed. Inspect status and retry; completion is not asserted.",
                    ),
                )

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server


class Client:
    def __init__(self, port, token):
        self.base = f"http://127.0.0.1:{port}/v2/"
        self.token = token

    def call(self, operation, **body):
        request = Request(
            self.base + operation,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token,
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                result = json.load(response)
        except HTTPError as error:
            result = json.load(error)
        except (URLError, TimeoutError, OSError) as error:
            raise ValueError(
                "Memory service disconnected or timed out. Check its status; no completion is asserted."
            ) from error
        if not result.get("ok"):
            raise ValueError(result.get("error", "Memory service disconnected."))
        return result["data"]
