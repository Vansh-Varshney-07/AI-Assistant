"""Minimal native main app and quick window sharing one authenticated service."""

import json
import queue
from threading import Thread
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import tkinter.font as tkfont

from wayfinder.native import WindowsControls
from wayfinder.service import uid


def pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


class Desktop:
    def __init__(self, root, client, shutdown):
        self.root, self.client, self.shutdown = root, client, shutdown
        self.events = queue.Queue()
        self.spaces, self.space, self.conversation = [], None, None
        self.epoch, self.busy, self.proof = 0, False, None
        self.selected_proposal = None
        self.selected_source = None
        self.closed = False
        self.settings = dict(font_size=12, background=False)
        root.title("Wayfinder — Personal AI")
        root.geometry("1120x800")
        root.minsize(820, 620)
        root.protocol("WM_DELETE_WINDOW", self.close_main)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("TNotebook.Tab", padding=(12, 7))
        toolbar = ttk.Frame(root, padding=10)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="WAYFINDER", font=("Segoe UI", 15, "bold")).pack(
            side="left", padx=(0, 18)
        )
        self.space_var = tk.StringVar()
        self.space_picker = ttk.Combobox(
            toolbar, textvariable=self.space_var, state="readonly", width=27
        )
        self.space_picker.pack(side="left")
        self.space_picker.bind("<<ComboboxSelected>>", lambda e: self.select_space())
        for label, command in (
            ("New space", self.new_space),
            ("New chat", self.new_chat),
            ("Quick chat", self.show_quick),
            ("Quit", self.quit),
        ):
            ttk.Button(toolbar, text=label, command=command).pack(side="left", padx=4)
        self.identity = tk.StringVar(value="Connecting")
        ttk.Label(root, textvariable=self.identity, padding=(12, 0)).pack(fill="x")
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        self.pages = {}
        for title in (
            "Chat",
            "Plugins",
            "Workflows",
            "Memory",
            "Skills",
            "Runs / Approvals",
            "Settings",
        ):
            page = ttk.Frame(self.tabs, padding=12)
            self.tabs.add(page, text=title)
            self.pages[title] = page
        for title, phase in (("Workflows", 6), ("Skills", 7)):
            page = self.pages[title]
            ttk.Label(
                page,
                text=f"{title} — available in phase {phase}",
                font=("Segoe UI", 16),
            ).pack(anchor="w", pady=12)
            ttk.Label(
                page,
                text="General workflows and skills are not connected yet.\nUse Desktop workers for Hermes file and shared-image analysis.",
            ).pack(anchor="w", pady=10)
            ttk.Button(page, text="Configure (not connected)", state="disabled").pack(
                anchor="w"
            )
        self.chat_widgets = []
        self.build_chat(self.pages["Chat"])
        self.build_memory()
        self.build_approvals()
        self.build_settings()
        self.build_workers()
        self.status = tk.StringVar(value="Starting local memory service")
        ttk.Label(root, textvariable=self.status, padding=8, wraplength=1050).pack(
            fill="x"
        )
        self.quick = tk.Toplevel(root)
        self.quick.title("Wayfinder — Quick chat")
        self.quick.geometry("470x500")
        self.quick.minsize(360, 340)
        self.quick.attributes("-topmost", True)
        self.quick.protocol("WM_DELETE_WINDOW", self.quick.withdraw)
        self.quick_identity = tk.StringVar()
        ttk.Label(
            self.quick, textvariable=self.quick_identity, wraplength=440, padding=8
        ).pack(fill="x")
        self.build_chat(self.quick, quick=True)
        self.quick.withdraw()
        self.native = WindowsControls(
            lambda action: self.events.put(("native", action))
        )
        self.root.after(50, self.drain)
        self.root.after(2500, self.poll)
        self.submit(
            lambda: (client.call("settings"), client.call("spaces")), self.initialized
        )

    def output(self, parent, height=12):
        frame = ttk.Frame(parent)
        box = tk.Text(
            frame, wrap="word", height=height, font=("Consolas", 11), state="disabled"
        )
        scroll = ttk.Scrollbar(frame, command=box.yview)
        box.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        box.pack(side="left", fill="both", expand=True)
        frame.pack(fill="both", expand=True, pady=5)
        return box

    @staticmethod
    def put(box, value):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", value)
        box.configure(state="disabled")

    def build_chat(self, parent, quick=False):
        ttk.Label(
            parent,
            text="Local transcript • Use Desktop workers for Hermes file and image analysis",
            wraplength=700,
        ).pack(anchor="w", pady=4)
        box = self.output(parent, 8)
        entry = ttk.Entry(parent)
        entry.pack(fill="x", pady=5)
        buttons = ttk.Frame(parent)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Save message", command=lambda: self.send(entry)).pack(
            side="left"
        )
        ttk.Button(buttons, text="Memory / tasks", command=self.open_memory).pack(
            side="left", padx=4
        )
        ttk.Button(
            buttons, text="Clear transcript", command=self.clear_transcript
        ).pack(side="left")
        entry.bind("<Return>", lambda e: self.send(entry))
        self.chat_widgets.append(box)
        if quick:
            ttk.Button(parent, text="Open main app", command=self.show_main).pack(
                anchor="e", padx=6, pady=5
            )

    def build_memory(self):
        page = self.pages["Memory"]
        ttk.Label(
            page,
            text="Explicit memory • inspect a proposal in Runs / Approvals before saving",
        ).pack(anchor="w")
        form = ttk.Frame(page)
        form.pack(fill="x", pady=6)
        self.fields = {}
        for index, (key, default) in enumerate(
            (
                ("subject", "me"),
                ("task_id", "general"),
                ("predicate", "retention_days"),
                ("value", "30"),
            )
        ):
            ttk.Label(form, text=key).grid(row=0, column=index, sticky="w")
            variable = tk.StringVar(value=default)
            ttk.Entry(form, textvariable=variable).grid(
                row=1, column=index, sticky="ew", padx=(0, 8)
            )
            form.columnconfigure(index, weight=1)
            self.fields[key] = variable
        second = ttk.Frame(page)
        second.pack(fill="x")
        self.action = tk.StringVar(value="assert")
        ttk.Combobox(
            second,
            textvariable=self.action,
            values=("assert", "correct", "supersede", "retract"),
            state="readonly",
            width=12,
        ).pack(side="left")
        ttk.Label(second, text="Target claim IDs (comma separated)").pack(
            side="left", padx=6
        )
        self.targets = ttk.Entry(second)
        self.targets.pack(side="left", fill="x", expand=True)
        ttk.Label(page, text="Reason for change").pack(anchor="w")
        self.reason = ttk.Entry(page)
        self.reason.pack(fill="x")
        ttk.Label(page, text="Source text (approved long-term memory)").pack(anchor="w")
        self.source_text = tk.Text(page, height=3, wrap="word")
        self.source_text.pack(fill="x")
        self.source_text.insert("1.0", "Cedar retention is 30 days.")
        actions = ttk.Frame(page)
        actions.pack(fill="x", pady=5)
        for label, command in (
            ("Propose memory", self.propose),
            ("Recall current", lambda: self.recall("now")),
            ("Recall history", lambda: self.recall("historical")),
            ("Refresh sources", self.inventory),
            ("Propose forget source", self.forget),
        ):
            ttk.Button(actions, text=label, command=command).pack(
                side="left", padx=(0, 4)
            )
        self.sources = ttk.Treeview(
            page, columns=("source", "status"), show="headings", height=3
        )
        self.sources.heading(
            "source", text="Source ID (select to inspect exact evidence / provenance)"
        )
        self.sources.heading("status", text="Claim states")
        self.sources.column("source", width=600)
        self.sources.pack(fill="x")
        self.sources.bind("<<TreeviewSelect>>", lambda e: self.inspect_source())
        self.memory_output = self.output(page, 8)

    def build_approvals(self):
        page = self.pages["Runs / Approvals"]
        ttk.Label(
            page,
            text="Approval binds the exact source, scope, operation and memory revision. No external task execution yet.",
        ).pack(anchor="w")
        actions = ttk.Frame(page)
        actions.pack(fill="x", pady=6)
        for label, command in (
            ("Refresh", self.approvals),
            ("Approve selected", lambda: self.decide(True)),
            ("Reject selected", lambda: self.decide(False)),
        ):
            ttk.Button(actions, text=label, command=command).pack(side="left", padx=4)
        self.proposal_list = ttk.Treeview(
            page, columns=("id", "status", "operation"), show="headings", height=5
        )
        for key in ("id", "status", "operation"):
            self.proposal_list.heading(key, text=key)
        self.proposal_list.pack(fill="x")
        self.proposal_list.bind("<<TreeviewSelect>>", lambda e: self.inspect_proposal())
        self.approval_output = self.output(page)
        self.proposals = {}

    def build_settings(self):
        page = self.pages["Settings"]
        ttk.Label(page, text="Local application settings", font=("Segoe UI", 16)).pack(
            anchor="w", pady=10
        )
        ttk.Label(page, text="Font size (10–24)").pack(anchor="w")
        self.font_size = tk.StringVar(value="12")
        ttk.Spinbox(page, from_=10, to=24, textvariable=self.font_size, width=8).pack(
            anchor="w"
        )
        self.background = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            page,
            text="Keep running in the tray when the main window closes",
            variable=self.background,
        ).pack(anchor="w", pady=10)
        ttk.Button(page, text="Save settings", command=self.save_settings).pack(
            anchor="w"
        )
        ttk.Button(page, text="Refresh health", command=self.poll_now).pack(
            anchor="w", pady=10
        )
        self.health = self.output(page, 10)
        ttk.Label(
            page,
            text="Ctrl+Alt+Space opens quick chat while this app runs. Quit stops this app's service.\nNo Windows startup job, schedules, screen capture or 24-hour availability claim.\nCredentials are held by the service and are not shown here.\nTranscripts are stored locally and never automatically become long-term memory.",
            wraplength=900,
        ).pack(anchor="w", pady=8)

    def submit(self, work, callback, *, bound=True):
        if self.busy:
            self.status.set(
                "A request is running. Wait for its result before starting another."
            )
            return
        self.busy = True
        self.status.set("Working locally…")
        epoch = self.epoch if bound else None

        def execute():
            try:
                self.events.put(("result", epoch, callback, work(), None))
            except Exception as error:
                self.events.put(("result", epoch, callback, None, str(error)))

        Thread(target=execute, daemon=True).start()

    def drain(self):
        if self.closed:
            return
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            if event[0] == "native":
                {"quick": self.show_quick, "main": self.show_main, "quit": self.quit}[
                    event[1]
                ]()
                continue
            _, epoch, callback, result, error = event
            self.busy = False
            if epoch is not None and epoch != self.epoch:
                self.status.set(
                    "The request remained bound to its original space. Refresh that space to inspect it."
                )
                continue
            if error:
                self.proof = None
                self.put(self.memory_output, "Evidence cleared: " + error)
                self.status.set("Request failed or unconfirmed: " + error)
            else:
                self.status.set(
                    "Ready • memory stays local • desktop analysis uses Hermes when requested"
                )
                try:
                    callback(result)
                except Exception:
                    self.status.set(
                        "View refresh failed. Refresh the active space; no completion is asserted."
                    )
        self.root.after(50, self.drain)

    def initialized(self, result):
        self.settings, spaces = result
        self.font_size.set(str(self.settings["font_size"]))
        self.background.set(self.settings["background"])
        self.apply_font()
        self.set_spaces(spaces)

    def set_spaces(self, spaces):
        self.spaces = spaces
        self.space_picker.configure(
            values=[s["name"] + " · " + s["id"][-8:] for s in spaces]
        )
        if spaces:
            index = next(
                (i for i, s in enumerate(spaces) if s["id"] == self.space),
                len(spaces) - 1,
            )
            self.space_picker.current(index)
            self.select_space()
        else:
            self.identity.set("No space yet. Create a space to start.")

    def select_space(self):
        index = self.space_picker.current()
        if index < 0:
            return
        self.space = self.spaces[index]["id"]
        self.epoch += 1
        self.conversation = None
        self.proof = None
        self.selected_proposal = self.selected_source = None
        self.proposals = {}
        self.proposal_list.delete(*self.proposal_list.get_children())
        self.sources.delete(*self.sources.get_children())
        for box in self.chat_widgets + [self.memory_output, self.approval_output]:
            self.put(box, "")
        self.worker_grant = self.worker_image = self.worker_run = None
        self.worker_files.delete(*self.worker_files.get_children())
        self.put(self.worker_output, "Select a file, folder or image for this space.")
        self.worker_selection.set("Nothing shared in this space")
        self.worker_job_rows = []
        self.worker_job_picker.configure(values=[])
        self.worker_job_picker.set("")
        self.update_identity()
        if not self.busy:
            self.new_chat()

    def update_identity(self):
        label = f"Space: {self.space or 'none'} | Conversation: {self.conversation or 'none'}"
        self.identity.set(label)
        self.quick_identity.set(label)

    def build_workers(self):
        page = self.pages["Plugins"]
        self.tabs.tab(page, text="Desktop workers")
        self.worker_grant = self.worker_image = self.worker_run = None
        self.worker_rows = {}
        ttk.Label(page, text="Files and shared images", font=("Segoe UI", 16)).pack(
            anchor="w"
        )
        ttk.Label(
            page,
            wraplength=950,
            text=(
                "Choose what to share, then ask a question. Analysis sends the selected content to your "
                "configured Hermes model. Files are read-only; nothing is saved to long-term memory."
            ),
        ).pack(anchor="w", pady=4)
        row = ttk.Frame(page)
        row.pack(fill="x")
        for label, command in (
            ("Choose folder", lambda: self.choose_worker_source(True)),
            ("Choose file", lambda: self.choose_worker_source(False)),
            ("Share screenshot/image", self.choose_worker_image),
            ("Revoke sharing", self.revoke_worker_sharing),
        ):
            ttk.Button(row, text=label, command=command).pack(side="left", padx=3)
        self.worker_selection = tk.StringVar(value="Nothing shared")
        ttk.Label(page, textvariable=self.worker_selection, wraplength=950).pack(
            anchor="w", pady=4
        )
        search = ttk.Frame(page)
        search.pack(fill="x")
        ttk.Label(search, text="Filename pattern").pack(side="left")
        self.worker_pattern = ttk.Entry(search, width=25)
        self.worker_pattern.insert(0, "*")
        self.worker_pattern.pack(side="left", padx=6)
        ttk.Button(search, text="Find files", command=self.search_worker_files).pack(
            side="left"
        )
        self.worker_files = ttk.Treeview(
            page, columns=("name", "size"), show="headings", height=5
        )
        self.worker_files.heading("name", text="Authorized file")
        self.worker_files.heading("size", text="Bytes")
        self.worker_files.column("name", width=650)
        self.worker_files.column("size", width=100)
        self.worker_files.pack(fill="x", pady=4)
        ttk.Label(page, text="Question or desktop request").pack(anchor="w")
        self.worker_question = ttk.Entry(page)
        self.worker_question.pack(fill="x", pady=3)
        self.worker_question.insert(
            0, "Summarize the selected source and cite the evidence."
        )
        row = ttk.Frame(page)
        row.pack(fill="x")
        for label, command in (
            ("Analyze selected file", lambda: self.start_worker("W35")),
            ("Analyze shared image", lambda: self.start_worker("W33")),
            ("Plan desktop request", lambda: self.start_worker("W36")),
            ("Refresh result", self.refresh_worker),
            ("Stop run", self.stop_worker),
            ("Clear result", self.clear_worker_result),
        ):
            ttk.Button(row, text=label, command=command).pack(side="left", padx=2)
        ttk.Label(
            page,
            text="Desktop execution is locked until a verified Windows driver is connected.",
            wraplength=950,
        ).pack(anchor="w", pady=5)
        history = ttk.Frame(page)
        history.pack(fill="x")
        ttk.Button(history, text="Recent runs", command=self.load_worker_jobs).pack(
            side="left"
        )
        self.worker_job_rows = []
        self.worker_job_picker = ttk.Combobox(history, state="readonly", width=60)
        self.worker_job_picker.pack(side="left", padx=5)
        self.worker_job_picker.bind(
            "<<ComboboxSelected>>", lambda _: self.select_worker_job()
        )
        self.worker_output = self.output(page, 9)

    def load_worker_jobs(self):
        if not self.space:
            return
        args = self.worker_args()

        def ready(rows):
            self.worker_job_rows = rows
            self.worker_job_picker.configure(
                values=[
                    f"{row['role']} · {row['status']} · {row['id'][-10:]}"
                    for row in rows
                ]
            )
            if rows:
                self.worker_job_picker.current(0)
                self.select_worker_job()

        self.submit(lambda: self.client.call("worker_jobs", **args), ready)

    def select_worker_job(self):
        selected = self.worker_job_picker.current()
        if 0 <= selected < len(self.worker_job_rows):
            job = self.worker_job_rows[selected]
            self.worker_run = job["id"]
            self.show_worker_result(job)

    def worker_args(self):
        if not self.space:
            raise ValueError("Create or select a space first.")
        return dict(space=self.space, task="desktop-ui")

    def choose_worker_source(self, folder):
        if self.busy or not self.space:
            return
        path = (
            filedialog.askdirectory(
                parent=self.root, title="Authorize read-only folder access"
            )
            if folder
            else filedialog.askopenfilename(
                parent=self.root, title="Select one file to analyze"
            )
        )
        if not path:
            return
        args = self.worker_args()
        previous = self.worker_grant

        def work():
            if previous:
                self.client.call("worker_revoke", **args, grant=previous)
            grant = self.client.call("worker_grant", **args, path=path)
            results = self.client.call(
                "worker_search", **args, grant=grant["id"], pattern="*"
            )
            return grant, results

        def ready(result):
            grant, results = result
            self.worker_grant = grant["id"]
            self.worker_selection.set(
                f"Read-only: {grant['name']} • expires in 15 minutes"
            )
            self.show_worker_files(results)

        self.submit(work, ready)

    def search_worker_files(self):
        if self.worker_grant:
            args, gid, pattern = (
                self.worker_args(),
                self.worker_grant,
                self.worker_pattern.get(),
            )
            self.submit(
                lambda: self.client.call(
                    "worker_search", **args, grant=gid, pattern=pattern
                ),
                self.show_worker_files,
            )

    def show_worker_files(self, result):
        self.worker_rows = {f["id"]: f for f in result["files"]}
        self.worker_files.delete(*self.worker_files.get_children())
        for item in result["files"]:
            self.worker_files.insert(
                "", "end", iid=item["id"], values=(item["name"], item["bytes"])
            )
        if result["files"]:
            self.worker_files.selection_set(result["files"][0]["id"])
        self.put(
            self.worker_output,
            f"Found {len(result['files'])} file(s). "
            + (
                "Search was bounded; narrow the pattern for more results."
                if result["possibly_truncated"]
                else "Select one to analyze."
            ),
        )

    def choose_worker_image(self):
        if self.busy or not self.space:
            return
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Share one screenshot or image",
            filetypes=[("PNG or JPEG", "*.png *.jpg *.jpeg")],
        )
        if not path:
            return
        # Preview the selected image before any provider request.
        try:
            import hashlib
            import io
            from PIL import Image, ImageTk
            from pathlib import Path

            if Path(path).stat().st_size > 2 * 1024 * 1024:
                raise ValueError("Choose an image no larger than 2 MiB.")
            raw = Path(path).read_bytes()
            image_hash = hashlib.sha256(raw).hexdigest()
            with Image.open(io.BytesIO(raw)) as selected:
                if selected.width * selected.height > 16_000_000:
                    raise ValueError("Choose an image no larger than 16 megapixels.")
                preview = selected.convert("RGB")
                preview.thumbnail((640, 400))
            dialog = tk.Toplevel(self.root)
            dialog.title("Selected image preview")
            photo = ImageTk.PhotoImage(preview)
            label = ttk.Label(dialog, image=photo)
            label.image = photo
            label.pack(padx=10, pady=10)
            ttk.Label(
                dialog,
                text="Only this selected image will be analyzed when you request it.",
            ).pack(padx=10)
            accepted = []

            def accept():
                accepted.append(True)
                dialog.destroy()

            ttk.Button(dialog, text="Share this image", command=accept).pack(pady=10)
            dialog.transient(self.root)
            dialog.grab_set()
            self.root.wait_window(dialog)
            if not accepted:
                return
        except Exception as error:
            self.status.set(str(error))
            return
        args = self.worker_args()

        def work():
            self.client.call("worker_clear_images", **args)
            return self.client.call(
                "worker_image", **args, path=path, sha256=image_hash
            )

        def ready(result):
            self.worker_image = result["id"]
            self.worker_selection.set(
                f"Shared image: {result['name']} • {result['width']} × {result['height']}"
            )
            self.put(
                self.worker_output,
                "Image shared locally. Select Analyze shared image to send it to Hermes.",
            )

        self.submit(work, ready)

    def revoke_worker_sharing(self):
        if not self.space:
            return
        args, gid = self.worker_args(), self.worker_grant

        def work():
            if gid:
                self.client.call("worker_revoke", **args, grant=gid)
            return self.client.call("worker_clear_images", **args)

        def ready(_):
            self.worker_grant = self.worker_image = None
            self.worker_files.delete(*self.worker_files.get_children())
            self.worker_selection.set("Sharing revoked")
            self.put(
                self.worker_output,
                "Future reads and delivery of pending analysis are revoked. Content already sent to the provider cannot be recalled.",
            )

        self.submit(work, ready)

    def start_worker(self, role):
        if not self.space:
            return
        args = self.worker_args()
        selected = self.worker_files.selection()
        reference = selected[0] if selected and role == "W35" else None
        if role == "W35" and not reference or role == "W33" and not self.worker_image:
            self.status.set("Select a file or share an image first.")
            return
        question = self.worker_question.get()
        image = self.worker_image if role == "W33" else None
        self.submit(
            lambda: self.client.call(
                "worker_start",
                **args,
                role=role,
                question=question,
                reference=reference,
                image=image,
            ),
            self.worker_started,
        )

    def worker_started(self, result):
        self.worker_run = result["id"]
        self.show_worker_result(result)
        if result["status"] in {"queued", "running", "stopping"}:
            self.root.after(1500, self.refresh_worker)

    def show_worker_result(self, result):
        data = result.get("result") or {}
        outline = data.get("outline")
        detail = data.get("text") or pretty(data)
        if outline:
            detail = (
                outline["summary"]
                + "\n\n"
                + "\n".join(
                    f"{i}. {step}"
                    for i, step in enumerate(outline["proposed_steps"], 1)
                )
                + "\n\nBefore execution: "
                + outline["needs_context"]
            )
        if (data.get("evidence") or {}).get("truncated") or (
            data.get("extraction") or {}
        ).get("truncated"):
            detail += "\n\nOnly part of the document was analyzed; the source exceeded the extraction limit."
        self.put(
            self.worker_output, f"{result['role']} · {result['status']}\n\n{detail}"
        )

    def refresh_worker(self):
        if self.closed or not self.space or not self.worker_run:
            return
        if self.busy:
            self.root.after(1500, self.refresh_worker)
            return
        args, jid = self.worker_args(), self.worker_run
        self.submit(
            lambda: self.client.call("worker_result", **args, id=jid),
            self.worker_started,
        )

    def stop_worker(self):
        if self.worker_run:
            args, jid = self.worker_args(), self.worker_run
            self.submit(
                lambda: self.client.call("worker_cancel", **args, id=jid),
                self.worker_started,
            )

    def clear_worker_result(self):
        if self.worker_run:
            args, jid = self.worker_args(), self.worker_run

            def ready(_):
                self.worker_run = None
                self.put(self.worker_output, "Stored result cleared.")

            self.submit(
                lambda: self.client.call("worker_forget", **args, id=jid), ready
            )

    def new_space(self):
        if self.busy:
            return
        name = simpledialog.askstring(
            "New memory space",
            "Name (each space has an independent ID):",
            parent=self.root,
        )
        if name:
            self.submit(
                lambda: (
                    self.client.call("create_space", name=name),
                    self.client.call("spaces"),
                )[1],
                self.set_spaces,
                bound=False,
            )

    def new_chat(self):
        if self.space:
            sid = self.space
            self.submit(
                lambda: self.client.call("conversation", space=sid),
                self.show_transcript,
            )

    def show_transcript(self, result):
        self.conversation = result["conversation"]
        self.update_identity()
        rendered = "\n\n".join("You: " + m["text"] for m in result["messages"])
        if not rendered:
            rendered = "This conversation is empty. Save local messages or use Memory for explicit facts."
        for box in self.chat_widgets:
            self.put(box, rendered)

    def send(self, entry):
        if self.busy or not self.conversation:
            self.status.set(
                "Create/select a space and wait for the conversation to open."
            )
            return
        value = entry.get().strip()
        if not value:
            return
        sid, cid, mid = self.space, self.conversation, uid()
        self.submit(
            lambda: self.client.call(
                "transcript", space=sid, conversation=cid, id=mid, text=value
            ),
            self.show_transcript,
        )
        entry.delete(0, "end")

    def clear_transcript(self):
        if self.conversation and messagebox.askyesno(
            "Clear transcript",
            "Delete messages in this conversation? Approved memories remain independent.",
        ):
            sid, cid = self.space, self.conversation
            self.submit(
                lambda: self.client.call(
                    "clear_transcript", space=sid, conversation=cid
                ),
                self.show_transcript,
            )

    def open_memory(self):
        self.show_main()
        self.tabs.select(self.pages["Memory"])

    def propose(self):
        if not self.space:
            return
        try:
            raw = self.fields["value"].get()
            try:
                value = json.loads(raw)
            except ValueError:
                value = raw
            body = {k: v.get() for k, v in self.fields.items() if k != "value"}
            body.update(
                value=value,
                text=self.source_text.get("1.0", "end").strip(),
                action=self.action.get(),
                targets=[x.strip() for x in self.targets.get().split(",") if x.strip()]
                or None,
                reason=self.reason.get(),
            )
            sid, request = self.space, uid()
            self.submit(
                lambda: self.client.call(
                    "propose", space=sid, request=request, body=body
                ),
                self.proposed,
            )
        except Exception:
            self.status.set("Invalid memory input. Check the form.")

    def proposed(self, proposal):
        self.tabs.select(self.pages["Runs / Approvals"])
        self.proposals[proposal["id"]] = proposal
        self.render_proposals(list(self.proposals.values()))
        self.proposal_list.selection_set(proposal["id"])
        self.inspect_proposal()
        self.status.set(
            "Pending approval. Inspect the exact input below, then Approve or Reject."
        )

    def approvals(self):
        if self.space:
            sid = self.space
            self.submit(
                lambda: self.client.call("proposals", space=sid), self.render_proposals
            )

    def render_proposals(self, rows):
        self.proposals = {r["id"]: r for r in rows}
        self.proposal_list.delete(*self.proposal_list.get_children())
        for row in rows:
            self.proposal_list.insert(
                "",
                "end",
                iid=row["id"],
                values=(
                    row["id"],
                    row["status"],
                    row["body"].get("operation", row["body"].get("action", "redacted")),
                ),
            )

    def inspect_proposal(self):
        selected = self.proposal_list.selection()
        self.selected_proposal = selected[0] if selected else None
        if self.selected_proposal:
            self.put(
                self.approval_output, pretty(self.proposals[self.selected_proposal])
            )

    def decide(self, approve):
        if not self.selected_proposal:
            return
        sid, pid = self.space, self.selected_proposal
        self.submit(
            lambda: self.client.call(
                "decide", space=sid, proposal=pid, approve=approve
            ),
            self.decided,
        )

    def decided(self, result):
        self.proof = None
        self.put(
            self.memory_output,
            "Memory changed or proposal decided. Retrieve fresh evidence.",
        )
        self.proposals[result["id"]] = result
        self.render_proposals(list(self.proposals.values()))
        self.proposal_list.selection_set(result["id"])
        self.inspect_proposal()
        self.status.set(
            "Proposal " + result["status"] + ". " + pretty(result.get("result"))
        )

    def recall(self, mode):
        if self.space:
            sid = self.space
            args = {
                k: self.fields[k].get() for k in ("subject", "predicate", "task_id")
            }
            self.submit(
                lambda: self.client.call(
                    "recall", space=sid, temporal_mode=mode, **args
                ),
                self.recalled,
            )

    def recalled(self, result):
        self.proof = result["proof"]
        self.put(self.memory_output, pretty(result))

    def inventory(self):
        if self.space:
            sid = self.space
            self.submit(
                lambda: self.client.call("inventory", space=sid), self.show_inventory
            )

    def show_inventory(self, result):
        self.sources.delete(*self.sources.get_children())
        self.selected_source = None
        for row in result["records"]:
            self.sources.insert(
                "",
                "end",
                iid=row["memory_id"],
                values=(row["memory_id"], ", ".join(row["statuses"])),
            )
        self.put(
            self.memory_output,
            f"{len(result['records'])} source(s). Select one for current/history/provenance inspection.",
        )

    def inspect_source(self):
        selected = self.sources.selection()
        if selected and not self.busy:
            sid, mid = self.space, selected[0]
            self.selected_source = mid
            self.submit(
                lambda: self.client.call("source", space=sid, memory_id=mid),
                lambda r: self.put(self.memory_output, pretty(r)),
            )

    def forget(self):
        if self.selected_source:
            sid, mid, request = self.space, self.selected_source, uid()
            self.submit(
                lambda: self.client.call(
                    "propose",
                    space=sid,
                    request=request,
                    body=dict(operation="forget", memory_id=mid),
                ),
                self.proposed,
            )

    def apply_font(self):
        tkfont.nametofont("TkDefaultFont").configure(
            family="Segoe UI", size=self.settings["font_size"]
        )
        for box in self.chat_widgets:
            box.configure(font=("Segoe UI", self.settings["font_size"]))

    def save_settings(self):
        try:
            value = dict(
                font_size=int(self.font_size.get()), background=self.background.get()
            )
        except ValueError:
            self.status.set("Font size must be an integer from 10 to 24.")
            return
        if value["background"] and not self.native.available:
            self.status.set("Tray unavailable. Background close cannot be enabled.")
            return

        def saved(result):
            self.settings = result
            self.apply_font()

        self.submit(
            lambda: self.client.call("settings", value=value), saved, bound=False
        )

    def poll_now(self):
        if not self.busy:
            proof, sid = self.proof, self.space

            def health():
                result = self.client.call("status")
                if proof:
                    self.client.call("validate_context", space=sid, proof=proof)
                return result

            self.submit(
                health,
                lambda r: self.put(
                    self.health,
                    pretty(
                        dict(r, tray=self.native.available, hotkey=self.native.hotkey)
                    ),
                ),
                bound=True,
            )

    def poll(self):
        if not self.closed:
            self.poll_now()
            self.root.after(4000, self.poll)

    def show_main(self):
        self.root.deiconify()
        self.root.lift()

    def show_quick(self):
        self.quick.deiconify()
        self.quick.lift()

    def close_main(self):
        if self.settings["background"] and self.native.available:
            self.root.withdraw()
        else:
            self.quit()

    def quit(self):
        if self.busy:
            self.status.set(
                "Waiting for the active operation before quitting. Try Quit when it finishes."
            )
            self.show_main()
            return
        if self.closed:
            return
        self.closed = True
        self.native.close()
        self.shutdown()
        self.root.destroy()
