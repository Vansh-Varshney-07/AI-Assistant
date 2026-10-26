"""Native widget/event-loop integration with a real authenticated memory API.

These tests call the application's own controllers, not OS input automation.
They do not stand in for a human visual/accessibility acceptance review.
"""

import time
import tkinter as tk

import pytest

from wayfinder.api import Client, serve
from wayfinder.desktop import Desktop
from tests.test_wayfinder_app import factory
from wayfinder.runtime import open_service


def settle(root, app, timeout=15):
    until = time.monotonic() + timeout
    while app.busy and time.monotonic() < until:
        root.update()
        time.sleep(0.01)
    root.update()
    assert not app.busy, app.status.get()


def test_shared_views_switch_settings_approval_and_native_lifecycle(tmp_path):
    service = open_service(tmp_path / "ui", factory)
    server = serve(service)
    client = Client(server.server_port, service.token)
    cedar = client.call("create_space", name="Cedar")
    maple = client.call("create_space", name="Maple")
    root = tk.Tk()
    stopped = []

    def shutdown():
        server.shutdown()
        server.server_close()
        service.close()
        stopped.append(True)

    app = Desktop(root, client, shutdown)
    try:
        settle(root, app)
        assert app.conversation
        assert len(app.tabs.tabs()) == 7
        for tab in app.tabs.tabs():
            app.tabs.select(tab)
            root.update()
        app.space_picker.current(0)
        app.select_space()
        settle(root, app)
        assert app.space == cedar["id"]
        assert app.identity.get() == app.quick_identity.get()
        cid = app.conversation
        root.geometry("1000x720")
        root.update()
        app.show_quick()
        root.update()
        assert app.quick.state() == "normal"
        app.quick.withdraw()
        app.show_quick()
        root.update()
        assert app.conversation == cid
        result = client.call(
            "transcript",
            space=app.space,
            conversation=cid,
            id="widget-message",
            text="Synthetic UI check",
        )
        app.show_transcript(result)
        assert app.chat_widgets[0].get("1.0", "end") == app.chat_widgets[1].get(
            "1.0", "end"
        )
        app.propose()
        settle(root, app)
        assert app.selected_proposal
        assert "pending" in app.approval_output.get("1.0", "end")
        app.decide(True)
        settle(root, app)
        assert "completed" in app.approval_output.get("1.0", "end")
        app.recall("now")
        settle(root, app)
        assert '"value": 30' in app.memory_output.get("1.0", "end")
        app.space_picker.current(1)
        app.select_space()
        settle(root, app)
        assert app.space == maple["id"]
        assert "30" not in app.memory_output.get("1.0", "end")
        assert "Synthetic UI check" not in app.chat_widgets[1].get("1.0", "end")
        app.font_size.set("14")
        app.save_settings()
        settle(root, app)
        assert client.call("settings")["font_size"] == 14
        app.font_size.set("999")
        app.save_settings()
        settle(root, app)
        assert client.call("settings")["font_size"] == 14
        if __import__("os").name == "nt":
            assert app.native.ready.wait(5)
            assert app.native.available, "Native tray registration failed"
            assert app.native.hotkey, "Global hotkey registration failed"
            app.background.set(True)
            app.font_size.set("14")
            app.save_settings()
            settle(root, app)
            app.close_main()
            root.update()
            assert root.state() == "withdrawn"
            app.show_main()
            root.update()
            assert root.state() == "normal"
        app.quit()
        assert stopped
        with pytest.raises(ValueError):
            client.call("status")
    finally:
        if not app.closed:
            app.busy = False
            app.quit()


def test_inflight_result_cannot_retarget_new_space(tmp_path):
    service = open_service(tmp_path / "ui-race", factory)
    server = serve(service)
    client = Client(server.server_port, service.token)
    client.call("create_space", name="Cedar")
    client.call("create_space", name="Maple")
    root = tk.Tk()

    def shutdown():
        server.shutdown()
        server.server_close()
        service.close()

    app = Desktop(root, client, shutdown)
    try:
        settle(root, app)
        original = app.space
        app.submit(
            lambda: {"from": original},
            lambda result: app.put(app.memory_output, str(result)),
        )
        app.space_picker.current(0)
        app.select_space()
        settle(root, app)
        assert app.space != original
        assert original not in app.memory_output.get("1.0", "end")
        assert "original space" in app.status.get()
        # New chat is available after the original operation is settled.
        app.new_chat()
        settle(root, app)
        assert app.conversation
    finally:
        app.busy = False
        app.quit()
