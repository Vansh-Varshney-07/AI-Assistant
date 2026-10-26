"""Real Cua CLI transport, restricted to one explicitly approved fixture window.

This is a test-only connection, not a general Windows desktop capability.
It reuses the same Cua driver used by Hermes; there is no agent/model loop.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import io


class CuaOperationError(RuntimeError):
    """Keep a scoped driver's refusal visible to the action gate and caller."""

    def __init__(self, tool, code, message):
        self.failure_details = dict(
            tool=tool, code=str(code)[:120], message=str(message)[:1200]
        )
        super().__init__(f"{tool}: {code}: {message}")


class CuaFixtureDriver:
    def __init__(self, executable, endpoint, case, *, process, window, title):
        self.executable = Path(executable).resolve(strict=True)
        self.endpoint, self.case = endpoint, Path(case).resolve(strict=True)
        self.process, self.window, self.title = process, window, title
        self.session = "wayfinder-cedar-test"
        self.last = None
        self.available = True
        self.calls = []

    def capability_manifest(self):
        """Draft only; a trusted launcher must approve it before starting Cua.

        Match the same exact target as _target, rather than every Python window
        through an executable lookup. Never enables display-wide input/capture.
        """
        if type(self.process) is not int or type(self.window) is not int:
            raise ValueError("Fixture identity must contain integer IDs.")
        if self.process <= 0 or self.window <= 0:
            raise ValueError("Fixture identity must contain positive IDs.")
        return dict(
            version=3,
            expires_after="1h",
            idle_timeout="10m",
            allow=dict(
                tools=["get_window_state", "click", "type_text", "bring_to_front"]
            ),
            resources=dict(
                desktop=dict(
                    display=False,
                    windows=[dict(pid=self.process, window_id=self.window)],
                ),
                files=dict(read=[], write=[dict(dir=str(self.case), recursive=True)]),
            ),
        )

    def call(self, name, **arguments):
        if name not in {
            "get_window_state",
            "click",
            "type_text",
            "press_key",
            "bring_to_front",
        }:
            raise ValueError("Tool unavailable in the fixture connection.")
        arguments.update(pid=self.process, window_id=self.window, session=self.session)
        result = subprocess.run(
            [
                str(self.executable),
                "--socket",
                self.endpoint,
                "call",
                name,
                json.dumps(arguments, allow_nan=False),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=25,
            env=dict(os.environ, CUA_DRIVER_RS_TELEMETRY_ENABLED="false"),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        invalid_response = False
        try:
            body = json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError):
            body = {}
            invalid_response = True
        if not isinstance(body, dict):
            body = {}
            invalid_response = True
        if (
            result.returncode
            or invalid_response
            or body.get("isError")
            or body.get("status") in {"refused", "error"}
        ):
            (self.case / "driver-last-error.json").write_text(
                json.dumps(
                    {
                        "tool": name,
                        "returncode": result.returncode,
                        "response": result.stdout[:10000],
                        "diagnostic": result.stderr[:2000],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            refusal = body.get("refusal")
            refusal = refusal if isinstance(refusal, dict) else {}
            fallback_code = (
                "driver_invalid_response"
                if invalid_response
                else "driver_operation_unconfirmed"
            )
            raise CuaOperationError(
                name,
                refusal.get("code", body.get("code", fallback_code)),
                refusal.get(
                    "message", "Cua refused or could not confirm the fixture operation."
                ),
            )
        return body

    def snapshot(self):
        path = self.case / "driver-observation.png"
        body = self.call(
            "get_window_state",
            include_accessibility_tree=False,
            include_screenshot=True,
            screenshot_out_file=str(path),
        )
        if "minimized window" in body.get("screenshot_error", ""):
            # Capture cannot read an iconic window. Restore only this fixed,
            # human-approved fixture, then take a fresh observation once.
            self.call("bring_to_front")
            body = self.call(
                "get_window_state",
                include_accessibility_tree=False,
                include_screenshot=True,
                screenshot_out_file=str(path),
            )
        if (
            body.get("pid") != self.process
            or body.get("window_id") != self.window
            or body.get("window_title") != self.title
            or body.get("screenshot_error")
            or not body.get("capture_id")
            or not path.is_file()
        ):
            raise RuntimeError(
                "Target identity or fixture capture could not be verified."
            )
        geometry = body.get("window_bounds")
        from PIL import Image

        with Image.open(path) as image:
            # Title-bar activation tint is not document state. Identity/title and
            # geometry are validated separately; preserve all client-area pixels.
            pixels = image.crop((8, 40, image.width - 8, image.height - 8))
            buffer = io.BytesIO()
            pixels.save(buffer, format="PNG")
        digest = hashlib.sha256(
            buffer.getvalue() + json.dumps(geometry, sort_keys=True).encode()
        ).hexdigest()
        self.last = dict(
            state=digest,
            capture=body,
            image_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        return digest

    def _target(self, plan):
        if (
            plan.window != self.window
            or plan.process != self.process
            or plan.app != self.title
        ):
            raise ValueError("Only the exact reviewed fixture window is permitted.")

    def observe(self, plan):
        self._target(plan)
        return self.snapshot()

    def perform(self, plan, step, expected):
        try:
            return self._perform(plan, step, expected)
        except Exception as error:
            artifact = self.case / "driver-last-error.json"
            if not artifact.exists():
                artifact.write_text(
                    json.dumps(
                        {
                            "stage": "perform",
                            "error_type": type(error).__name__,
                            "message": str(error)[:2000],
                        }
                    ),
                    encoding="utf-8",
                )
            raise

    def _perform(self, plan, step, expected):
        self._target(plan)
        if step.delivery_mode == "foreground":
            activation = self.call("bring_to_front")
            if not activation.get("landed_on_target"):
                raise RuntimeError("The approved fixture could not acquire foreground.")
        observed = self.snapshot()
        if observed != expected:
            (self.case / "driver-last-error.json").write_text(
                json.dumps(
                    {
                        "stage": "pre_dispatch_state",
                        "expected": expected,
                        "observed": observed,
                    }
                ),
                encoding="utf-8",
            )
            raise ValueError("Fixture pixels changed before input dispatch.")
        if step.action == "click":
            width = self.last["capture"]["screenshot_width"]
            height = self.last["capture"]["screenshot_height"]
            if not (0 <= step.x < width and 40 <= step.y < height):
                raise ValueError("Click is outside the fixture client area.")
            result = self.call(
                "click",
                scope="window",
                x=step.x,
                y=step.y,
                capture_id=self.last["capture"]["capture_id"],
                delivery_mode=step.delivery_mode or "background",
            )
        elif step.action == "type_text":
            result = self.call(
                "type_text",
                scope="window",
                text=step.text,
                delivery_mode=step.delivery_mode or "background",
            )
        else:
            raise ValueError(
                "This fixture run permits only reviewed clicks and literal text."
            )
        # Do not automatically escalate or retry input after uncertain delivery.
        self.calls.append(dict(action=step.action, result=result))
        time.sleep(0.15)
        return dict(action=step.action, state=self.snapshot(), driver_result=result)

    def verify(self, plan, receipts):
        self._target(plan)
        target = self.case / "output" / "cedar-handoff.txt"
        expected = "".join(
            step.text for step in plan.steps if step.action == "type_text"
        )
        return (
            target.is_file()
            and target.read_text(encoding="utf-8") == expected
            and len(receipts) == len(plan.steps)
        )
