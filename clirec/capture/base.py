from __future__ import annotations

import platform
from dataclasses import dataclass
from collections.abc import Callable
from typing import Protocol, runtime_checkable


@dataclass
class RawEvent:
    kind: str  # mouse_down|mouse_up|mouse_move|wheel|key_down|key_up|char
    t: float
    x: int | None = None
    y: int | None = None
    button: str | None = None
    key: str | None = None
    char: str | None = None
    delta: int | None = None
    sensitive: bool | None = None
    sensitive_captured: bool = False
    ui_name: str | None = None
    ui_window: str | None = None
    ui_role: str | None = None
    frame: str | None = None
    ui_captured: bool = False


@runtime_checkable
class CaptureBackend(Protocol):
    def available(self) -> bool: ...
    def set_sensitive_provider(
        self, provider: Callable[[], bool | None] | None
    ) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def poll(self) -> list[RawEvent]: ...
    def set_paused(self, paused: bool) -> None: ...


def ensure_per_monitor_dpi_awareness() -> bool:
    """Establish one physical-pixel coordinate space for Windows capture."""

    if platform.system() != "Windows":
        return True
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        per_monitor_v2 = ctypes.c_void_p(-4)
        per_monitor_v1 = ctypes.c_void_p(-3)
        setter = getattr(user32, "SetProcessDpiAwarenessContext", None)
        if setter is not None:
            setter.argtypes = [ctypes.c_void_p]
            setter.restype = wintypes.BOOL
            if setter(per_monitor_v2):
                return True

        thread_context = getattr(user32, "GetThreadDpiAwarenessContext", None)
        contexts_equal = getattr(user32, "AreDpiAwarenessContextsEqual", None)
        if thread_context is not None and contexts_equal is not None:
            thread_context.argtypes = []
            thread_context.restype = ctypes.c_void_p
            contexts_equal.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            contexts_equal.restype = wintypes.BOOL
            current = thread_context()
            if contexts_equal(current, per_monitor_v2) or contexts_equal(
                current, per_monitor_v1
            ):
                return True

        shcore = getattr(ctypes.windll, "shcore", None)
        if shcore is not None:
            set_awareness = shcore.SetProcessDpiAwareness
            set_awareness.argtypes = [ctypes.c_int]
            set_awareness.restype = ctypes.c_long
            set_awareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            awareness = ctypes.c_int()
            get_awareness = shcore.GetProcessDpiAwareness
            get_awareness.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_int)]
            get_awareness.restype = ctypes.c_long
            ctypes.windll.kernel32.GetCurrentProcess.argtypes = []
            ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            process = ctypes.windll.kernel32.GetCurrentProcess()
            if get_awareness(process, ctypes.byref(awareness)) == 0:
                return awareness.value == 2
    except Exception:
        pass
    return False


def get_backend(name: str | None = None) -> CaptureBackend:
    """Select a capture backend.

    name=None  -> auto: 'winapi' on Windows, else 'pynput'.
    Explicit:   'mock' | 'winapi' | 'pynput'.
    """
    chosen = name or ("winapi" if platform.system() == "Windows" else "pynput")
    if chosen == "mock":
        from .mock import MockCaptureBackend

        return MockCaptureBackend([])
    if chosen == "winapi":
        from .winapi import WinApiCaptureBackend  # Task 9

        return WinApiCaptureBackend()
    if chosen == "pynput":
        from .pynput_backend import PynputCaptureBackend  # Task 9

        return PynputCaptureBackend()
    raise RuntimeError(f"unknown capture backend: {chosen!r}")


def get_desktop_geometry() -> tuple[int, int, int, int] | None:
    """Return ``(origin_x, origin_y, width, height)`` when it can be detected.

    Windows uses the full virtual desktop, including negative monitor origins.
    Other platforms use Tk's current desktop geometry when a display is
    available. ``None`` is preferable to silently recording unusable ``0x0``
    coordinates.
    """

    if platform.system() == "Windows":
        if not ensure_per_monitor_dpi_awareness():
            return None
        try:
            import ctypes

            user32 = ctypes.windll.user32
            x = int(user32.GetSystemMetrics(76))  # SM_XVIRTUALSCREEN
            y = int(user32.GetSystemMetrics(77))  # SM_YVIRTUALSCREEN
            width = int(user32.GetSystemMetrics(78))  # SM_CXVIRTUALSCREEN
            height = int(user32.GetSystemMetrics(79))  # SM_CYVIRTUALSCREEN
            if width > 0 and height > 0:
                return x, y, width, height
        except Exception:
            pass

    try:
        import tkinter

        root = tkinter.Tk()
        root.withdraw()
        try:
            width = int(root.winfo_screenwidth())
            height = int(root.winfo_screenheight())
        finally:
            root.destroy()
        if width > 0 and height > 0:
            return 0, 0, width, height
    except Exception:
        pass
    return None
