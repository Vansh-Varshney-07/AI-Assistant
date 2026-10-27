"""Launch the Windows-first Wayfinder desktop shell without hosted inference."""

import argparse
from pathlib import Path
import queue
from threading import Thread
import tkinter as tk
from tkinter import ttk

from wayfinder.api import Client, serve
from wayfinder.desktop import Desktop
from wayfinder.runtime import open_service


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(__file__).resolve().parent / ".local/wayfinder",
    )
    args = parser.parse_args()
    root = tk.Tk()
    root.title("Wayfinder — Starting")
    root.geometry("640x220")
    pane = ttk.Frame(root, padding=20)
    pane.pack(fill="both", expand=True)
    status = tk.StringVar(value="Connecting to local memory storage…")
    ttk.Label(pane, textvariable=status, wraplength=590).pack(pady=12)
    events = queue.Queue()
    state = {"loading": False}

    def connect():
        if state["loading"]:
            return
        state["loading"] = True
        status.set("Connecting to local memory storage…")

        def work():
            service = None
            try:
                service = open_service(args.runtime)
                server = serve(service)
                events.put((service, server, None))
            except Exception:
                if service:
                    service.close()
                events.put(
                    (
                        None,
                        None,
                        "Memory storage is offline or another app owns this runtime. Start Docker/FalkorDB, or quit the other owner, then Retry. No memory was reported saved.",
                    )
                )

        Thread(target=work, daemon=True).start()

    def quit_startup():
        if state["loading"]:
            status.set("Waiting for the connection attempt before quitting.")
            state["quit"] = True
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", quit_startup)
    ttk.Button(pane, text="Retry connection", command=connect).pack(side="left")
    ttk.Button(pane, text="Quit", command=quit_startup).pack(side="right")

    def poll():
        try:
            service, server, error = events.get_nowait()
        except queue.Empty:
            root.after(100, poll)
            return
        state["loading"] = False
        if state.get("quit"):
            if server:
                server.shutdown()
                server.server_close()
                service.close()
            root.destroy()
            return
        if error:
            status.set(error)
            root.after(100, poll)
            return
        pane.destroy()

        def shutdown():
            server.shutdown()
            server.server_close()
            service.close()

        Desktop(root, Client(server.server_port, service.token), shutdown)

    connect()
    root.after(100, poll)
    root.mainloop()


if __name__ == "__main__":
    main()
