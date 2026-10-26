"""Windows notification area and Ctrl+Alt+Space; no third-party UI runtime."""

import ctypes
from ctypes import wintypes
import os
import threading


class WindowsControls:
    def __init__(self, post):
        self.post = post
        self.ready = threading.Event()
        self.hwnd = None
        self.available = False
        self.hotkey = False
        if os.name == "nt":
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        user, shell, kernel = (
            ctypes.windll.user32,
            ctypes.windll.shell32,
            ctypes.windll.kernel32,
        )
        WNDPROC = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        )

        class WNDCLASS(ctypes.Structure):
            _fields_ = [
                ("style", wintypes.UINT),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HANDLE),
                ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
            ]

        class NID(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("hWnd", wintypes.HWND),
                ("uID", wintypes.UINT),
                ("uFlags", wintypes.UINT),
                ("uCallbackMessage", wintypes.UINT),
                ("hIcon", wintypes.HICON),
                ("szTip", wintypes.WCHAR * 128),
                ("dwState", wintypes.DWORD),
                ("dwStateMask", wintypes.DWORD),
                ("szInfo", wintypes.WCHAR * 256),
                ("uTimeout", wintypes.UINT),
                ("szInfoTitle", wintypes.WCHAR * 64),
                ("dwInfoFlags", wintypes.DWORD),
                ("guidItem", ctypes.c_byte * 16),
                ("hBalloonIcon", wintypes.HICON),
            ]

        user.DefWindowProcW.restype = ctypes.c_ssize_t
        user.CreateWindowExW.restype = wintypes.HWND
        user.LoadIconW.restype = wintypes.HICON
        kernel.GetModuleHandleW.restype = wintypes.HMODULE
        user.CreatePopupMenu.restype = wintypes.HMENU
        user.RegisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        user.DestroyMenu.argtypes = [wintypes.HMENU]
        user.LoadIconW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]
        user.TrackPopupMenu.restype = wintypes.UINT
        user.AppendMenuW.argtypes = [
            wintypes.HMENU,
            wintypes.UINT,
            ctypes.c_size_t,
            wintypes.LPCWSTR,
        ]
        user.TrackPopupMenu.argtypes = [
            wintypes.HMENU,
            wintypes.UINT,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            ctypes.c_void_p,
        ]
        user.DefWindowProcW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user.PostMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user.SetForegroundWindow.argtypes = [wintypes.HWND]
        user.DestroyWindow.argtypes = [wintypes.HWND]
        shell.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NID)]
        callback_message = 0x8001

        @WNDPROC
        def proc(hwnd, message, wparam, lparam):
            if message == 0x312:  # WM_HOTKEY
                self.post("quick")
                return 0
            if message == callback_message:
                if lparam in (0x202, 0x203):
                    self.post("quick")
                elif lparam == 0x205:
                    menu = user.CreatePopupMenu()
                    for number, label in (
                        (1, "Open Wayfinder"),
                        (2, "Quick chat"),
                        (3, "Quit Wayfinder"),
                    ):
                        user.AppendMenuW(menu, 0, number, label)
                    point = wintypes.POINT()
                    user.GetCursorPos(ctypes.byref(point))
                    user.SetForegroundWindow(hwnd)
                    choice = user.TrackPopupMenu(
                        menu, 0x100 | 0x2, point.x, point.y, 0, hwnd, None
                    )
                    user.DestroyMenu(menu)
                    if choice:
                        self.post({1: "main", 2: "quick", 3: "quit"}[choice])
                return 0
            if message == 0x10:
                user.DestroyWindow(hwnd)
                return 0
            if message == 0x2:
                user.PostQuitMessage(0)
                return 0
            return user.DefWindowProcW(hwnd, message, wparam, lparam)

        self.proc = proc
        instance = kernel.GetModuleHandleW(None)
        name = "WayfinderTray_" + str(os.getpid())
        wc = WNDCLASS(0, proc, 0, 0, instance, None, None, None, None, name)
        user.RegisterClassW(ctypes.byref(wc))
        user.CreateWindowExW.argtypes = [
            wintypes.DWORD,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            wintypes.HMENU,
            wintypes.HINSTANCE,
            ctypes.c_void_p,
        ]
        self.hwnd = user.CreateWindowExW(
            0, name, "Wayfinder controls", 0, 0, 0, 0, 0, None, None, instance, None
        )
        nid = NID()
        nid.cbSize, nid.hWnd, nid.uID = ctypes.sizeof(NID), self.hwnd, 1
        nid.uFlags, nid.uCallbackMessage = 1 | 2 | 4, callback_message
        nid.hIcon, nid.szTip = (
            user.LoadIconW(None, ctypes.c_void_p(32512)),
            "Wayfinder — quick chat (Ctrl+Alt+Space)",
        )
        self.available = bool(shell.Shell_NotifyIconW(0, ctypes.byref(nid)))
        self.hotkey = bool(user.RegisterHotKey(self.hwnd, 1, 0x4000 | 1 | 2, 0x20))
        self.ready.set()
        msg = wintypes.MSG()
        while user.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user.TranslateMessage(ctypes.byref(msg))
            user.DispatchMessageW(ctypes.byref(msg))
        user.UnregisterHotKey(self.hwnd, 1)
        shell.Shell_NotifyIconW(2, ctypes.byref(nid))
        self.available = False

    def close(self):
        if self.hwnd:
            ctypes.windll.user32.PostMessageW(self.hwnd, 0x10, 0, 0)
