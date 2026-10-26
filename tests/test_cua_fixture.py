"""No native input here: verify the real CLI adapter's scope checks before dispatch."""

import json
from types import SimpleNamespace

import pytest

from wayfinder.workers.actions import DesktopPlan
from wayfinder.workers.cua_fixture import CuaFixtureDriver, CuaOperationError


def fixture_driver(tmp_path):
    executable = tmp_path / "fixture-driver.exe"
    executable.write_bytes(b"not executed")
    return CuaFixtureDriver(
        executable,
        "fixture-private-endpoint",
        tmp_path,
        process=41,
        window=17,
        title="Cedar fixture",
    )


def plan(**changes):
    return DesktopPlan.model_validate(
        dict(
            summary="Fixture",
            app="Cedar fixture",
            process=41,
            window=17,
            state="initial",
            observation="selected_window",
            completion="Fixture saved",
            steps=[dict(action="type_text", text="Cedar")],
            **changes,
        )
    )


def test_wrong_target_and_unlisted_tools_never_launch_process(tmp_path, monkeypatch):
    driver = fixture_driver(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("No process should launch")

    monkeypatch.setattr("wayfinder.workers.cua_fixture.subprocess.run", forbidden)
    wrong = plan().model_copy(update=dict(window=99))
    with pytest.raises(ValueError, match="exact reviewed"):
        driver.observe(wrong)
    with pytest.raises(ValueError, match="unavailable"):
        driver.call("terminal")


def test_cli_arguments_pin_process_window_and_session(tmp_path, monkeypatch):
    driver = fixture_driver(tmp_path)
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout='{"status":"ok"}')

    monkeypatch.setattr("wayfinder.workers.cua_fixture.subprocess.run", run)
    driver.call("type_text", pid=999, window_id=999, session="other", text="$(literal)")
    args = json.loads(calls[0][-1])
    assert args == dict(
        pid=41, window_id=17, session="wayfinder-cedar-test", text="$(literal)"
    )
    assert calls[0][1:4] == ["--socket", "fixture-private-endpoint", "call"]


def test_snapshot_checks_identity_and_client_pixels(tmp_path, monkeypatch):
    from PIL import Image, ImageDraw

    driver = fixture_driver(tmp_path)
    image = Image.new("RGB", (200, 200), "green")
    path = tmp_path / "driver-observation.png"
    image.save(path)
    response = dict(
        pid=41,
        window_id=17,
        window_title="Cedar fixture",
        capture_id="fixture-capture",
        screenshot_width=200,
        screenshot_height=200,
        window_bounds=dict(x=1, y=2, width=200, height=200),
    )
    monkeypatch.setattr(driver, "call", lambda *args, **kwargs: dict(response))
    before = driver.snapshot()
    ImageDraw.Draw(image).rectangle((0, 0, 199, 35), fill="red")
    image.save(path)
    assert driver.snapshot() == before
    ImageDraw.Draw(image).rectangle((50, 80, 100, 110), fill="white")
    image.save(path)
    assert driver.snapshot() != before
    response["pid"] = 42
    with pytest.raises(RuntimeError, match="identity"):
        driver.snapshot()


def test_stale_pixels_block_input_and_file_verification_is_exact(tmp_path, monkeypatch):
    driver = fixture_driver(tmp_path)
    monkeypatch.setattr(driver, "snapshot", lambda: "changed")
    with pytest.raises(ValueError, match="pixels changed"):
        driver.perform(plan(), plan().steps[0], "initial")
    assert driver.calls == []
    (tmp_path / "output").mkdir()
    output = tmp_path / "output/cedar-handoff.txt"
    output.write_text("different")
    assert not driver.verify(plan(), [{}])
    output.write_text("Cedar")
    assert driver.verify(plan(), [{}])


def test_failed_foreground_activation_stops_before_capture_or_input(
    tmp_path, monkeypatch
):
    driver = fixture_driver(tmp_path)
    calls = []

    def call(name, **kwargs):
        calls.append(name)
        return dict(landed_on_target=False)

    def forbidden():
        raise AssertionError("Must stop after failed activation")

    monkeypatch.setattr(driver, "call", call)
    monkeypatch.setattr(driver, "snapshot", forbidden)
    step = plan().steps[0].model_copy(update=dict(delivery_mode="foreground"))
    with pytest.raises(RuntimeError, match="acquire foreground"):
        driver.perform(plan(), step, "initial")
    assert calls == ["bring_to_front"]
    assert driver.calls == []


def test_manifest_grants_only_reviewed_window_without_display_or_app_access(tmp_path):
    driver = fixture_driver(tmp_path)
    manifest = driver.capability_manifest()
    assert manifest["resources"]["desktop"] == dict(
        display=False, windows=[dict(pid=41, window_id=17)]
    )
    assert "apps" not in manifest["resources"]
    assert "launch_app" not in manifest["allow"]["tools"]
    assert manifest["resources"]["files"]["read"] == []
    driver.process = 0
    with pytest.raises(ValueError, match="positive"):
        driver.capability_manifest()


def test_driver_refusal_keeps_structured_reason_without_retry(tmp_path, monkeypatch):
    driver = fixture_driver(tmp_path)
    calls = []
    refusal = dict(
        code="bounded_resource_outside_manifest", message="Window not granted"
    )

    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(
            returncode=1,
            stdout=json.dumps(dict(status="refused", refusal=refusal)),
            stderr="",
        )

    monkeypatch.setattr("wayfinder.workers.cua_fixture.subprocess.run", run)
    with pytest.raises(CuaOperationError) as caught:
        driver.call("type_text", text="Cedar")
    assert caught.value.failure_details == dict(tool="type_text", **refusal)
    assert len(calls) == 1


@pytest.mark.parametrize("response", ["invalid json", "[]"])
def test_malformed_driver_response_is_not_accepted(tmp_path, monkeypatch, response):
    driver = fixture_driver(tmp_path)
    monkeypatch.setattr(
        "wayfinder.workers.cua_fixture.subprocess.run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=response, stderr=""),
    )
    with pytest.raises(CuaOperationError) as caught:
        driver.call("type_text", text="Cedar")
    assert caught.value.failure_details["code"] == "driver_invalid_response"
