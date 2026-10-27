"""Bounded transport to the existing OpenShell-managed Hermes installation."""

import base64
import json
from pathlib import Path
import subprocess
import threading
import time


class HermesUnavailable(RuntimeError):
    pass


class HermesBridge:
    def __init__(self, *, command=None, timeout=110):
        self.command = command or [
            "wsl.exe",
            "-d",
            "Ubuntu-24.04",
            "-u",
            "assistant",
            "--",
            "/home/assistant/.local/bin/openshell",
            "sandbox",
            "exec",
            "-n",
            "ai-assistant",
            "--no-tty",
            "--timeout",
            "100",
            "--",
            "/opt/hermes/.venv/bin/python",
            "-",
        ]
        self.timeout = timeout

    def run(self, payload, cancelled=None):
        cancelled = cancelled or threading.Event()
        script = (
            Path(__file__).with_name("hermes_runner.py").read_text(encoding="utf-8")
        )
        # The request is data, never shell code or command-line interpolation.
        encoded = base64.b64encode(
            json.dumps(payload, allow_nan=False).encode()
        ).decode("ascii")
        source = "REQUEST_B64 = " + repr(encoded) + "\n" + script
        if cancelled.is_set():
            raise HermesUnavailable("Worker stopped.")
        try:
            process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if __import__("os").name == "nt" else 0
                ),
            )
        except OSError as error:
            raise HermesUnavailable(
                "The installed Hermes sandbox is unavailable. Start Ubuntu/OpenShell."
            ) from error
        deadline = time.monotonic() + self.timeout
        outgoing = source.encode("utf-8")
        try:
            while True:
                if cancelled.is_set() or time.monotonic() > deadline:
                    process.kill()
                    process.communicate()
                    raise HermesUnavailable(
                        "Worker stopped or timed out; no result is confirmed."
                    )
                try:
                    output, _ = process.communicate(input=outgoing, timeout=0.2)
                    break
                except subprocess.TimeoutExpired:
                    outgoing = None
            if process.returncode:
                raise HermesUnavailable(
                    "Hermes could not complete this bounded worker run."
                )
            marker = b"WAYFINDER_WORKER_RESULT="
            lines = [
                line[len(marker) :]
                for line in output.splitlines()
                if line.startswith(marker)
            ]
            if len(lines) != 1 or len(lines[0]) > 400000:
                raise HermesUnavailable("Hermes returned an invalid worker response.")
            result = json.loads(lines[0])
            if not result.get("ok") or result.get("effective_tools") != []:
                raise HermesUnavailable(
                    result.get("error", "Worker tool isolation failed.")
                    + " "
                    + json.dumps(result.get("diagnostic", {}))
                )
            return result
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
