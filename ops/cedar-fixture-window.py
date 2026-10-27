"""Dedicated fictional test window; no desktop observation or external actions."""

import argparse
import ctypes
import os
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    if os.name == "nt":
        # Set this application's DPI mode, not a system-wide preference.
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    case = args.case.resolve()
    if not (case / "scenario.json").is_file():
        raise ValueError("A generated Cedar scenario directory is required.")
    root = tk.Tk()
    root.title(args.title)
    root.geometry("840x650")
    root.configure(background="#f3f6f8")
    root.after(400, root.deiconify)
    card = tk.Frame(root, background="#e5f4e8", padx=30, pady=22)
    card.pack(fill="x", padx=18, pady=18)
    tk.Label(
        card, text="PROJECT CEDAR", font=("Segoe UI", 25, "bold"), background="#e5f4e8"
    ).pack(anchor="w")
    tk.Label(
        card,
        text="SCREENSHOT SOURCE • Retention: 42 days",
        font=("Segoe UI", 19),
        background="#e5f4e8",
    ).pack(anchor="w", pady=10)
    tk.Label(
        card,
        text="Fictional acceptance-test data • compare with the local release note",
        font=("Segoe UI", 11),
        background="#e5f4e8",
    ).pack(anchor="w")
    panel = ttk.Frame(root, padding=18)
    panel.pack(fill="both", expand=True)
    ttk.Label(
        panel, text="Dedicated test editor — approved draft only", font=("Segoe UI", 14)
    ).pack(anchor="w")
    editor = tk.Text(
        panel, height=11, font=("Consolas", 12), wrap="word", insertofftime=0
    )
    editor.pack(fill="both", expand=True, pady=10)
    status = tk.StringVar(
        value="No draft saved. This window does not run W37 or approve actions."
    )

    def save():
        value = editor.get("1.0", "end-1c")
        if not value.strip():
            status.set("Enter the approved draft before saving.")
            return
        destination = case / "output" / "cedar-handoff.txt"
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(value)
        except FileExistsError:
            status.set("A draft already exists. Overwriting is unavailable.")
            return
        status.set("Saved new draft: cedar-handoff.txt")

    ttk.Button(panel, text="Save new draft", command=save).pack(anchor="w")
    ttk.Label(panel, textvariable=status, wraplength=780).pack(anchor="w", pady=8)

    def poll_close():
        if (case / "close-window").exists():
            root.destroy()
        else:
            root.after(250, poll_close)

    poll_close()

    def publish_identity():
        (case / "fixture-target.json").write_text(
            json.dumps(
                {
                    "process": os.getpid(),
                    "window": int(root.wm_frame(), 0),
                    "title": root.title(),
                }
            ),
            encoding="utf-8",
        )

    root.after(500, publish_identity)
    root.mainloop()


if __name__ == "__main__":
    main()
