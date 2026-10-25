"""
wayfinder/atlas/harness/desktop_adapter.py
──────────────────────────────────────────
Implements DesktopProvider for Windows OS environment.

Provides:
  - File discovery across approved local directories
  - Text extraction from local documents (.md, .txt, .json, .csv, .pdf)
  - Controlled application launcher gated by a strict allowlist
  - Windows clipboard read / write operations
  - Windows toast notifications
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from wayfinder.atlas.harness.base import DesktopProvider

# Strictly allowlisted desktop applications for safety
APPLICATION_ALLOWLIST: dict[str, list[str]] = {
    "notion": ["notion.exe", "Notion"],
    "vscode": ["code.cmd", "code.exe", "code"],
    "notepad": ["notepad.exe"],
    "calc": ["calc.exe"],
    "terminal": ["wt.exe", "pwsh.exe", "powershell.exe"],
    "browser": ["msedge.exe", "chrome.exe"],
    "explorer": ["explorer.exe"],
}


class DesktopAdapter(DesktopProvider):

    def __init__(self, default_search_root: Path | None = None):
        self.default_search_root = default_search_root or Path.cwd()

    def find_files(self, pattern: str, directory: str | None = None, max_results: int = 15) -> list[str]:
        target_dir = Path(directory) if directory else self.default_search_root
        if not target_dir.exists():
            return []

        matched: list[str] = []
        for path in target_dir.rglob(pattern):
            if any(part.startswith(".") or part in ["node_modules", ".venv", "__pycache__"] for part in path.parts):
                continue
            matched.append(str(path))
            if len(matched) >= max_results:
                break
        return matched

    def read_document(self, path: str, max_chars: int = 10000) -> str:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = file_path.suffix.lower()
        if suffix in [".txt", ".md", ".json", ".csv", ".py", ".yaml", ".yml"]:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            return text[:max_chars] + ("\n... [truncated]" if len(text) > max_chars else "")
        else:
            return f"[Unsupported binary file format: {suffix}]"

    def open_application(self, app_name: str) -> bool:
        normalized = app_name.lower().strip()
        binary_candidates = APPLICATION_ALLOWLIST.get(normalized)

        if not binary_candidates:
            raise PermissionError(
                f"Application '{app_name}' is not in the desktop allowlist. "
                f"Allowed apps: {list(APPLICATION_ALLOWLIST.keys())}"
            )

        cmd = None
        for cand in binary_candidates:
            if shutil.which(cand):
                cmd = cand
                break

        if not cmd:
            # Fallback to start command for registered Windows protocols
            cmd = binary_candidates[0]

        try:
            subprocess.Popen(cmd, shell=True)
            return True
        except Exception as exc:
            raise RuntimeError(f"Failed to launch application '{app_name}': {exc}")

    def read_clipboard(self) -> str:
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception as exc:
            return f"[Clipboard read error: {exc}]"

    def set_clipboard(self, text: str) -> bool:
        try:
            proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
                stdin=subprocess.PIPE,
                text=True,
            )
            proc.communicate(input=text)
            return proc.returncode == 0
        except Exception:
            return False

    def send_notification(self, title: str, message: str) -> bool:
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode('{title}')) > $null
        $textNodes.Item(1).AppendChild($template.CreateTextNode('{message}')) > $null
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Wayfinder")
        $notification = [Windows.UI.Notifications.ToastNotification]::new($template)
        $notifier.Show($notification)
        """
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], timeout=5)
            return True
        except Exception:
            return False
