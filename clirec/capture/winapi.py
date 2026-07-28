"""Windows low-level capture via ctypes SetWindowsHookEx (zero extra deps).

A dedicated thread runs a message loop with WH_MOUSE_LL + WH_KEYBOARD_LL
hooks and pushes RawEvents into a thread-safe queue. poll() drains it.

NOTE: Real hook + message loop -- not CI-testable. Smoke test only checks the
available()/protocol contract.
"""

from __future__ import annotations

import ctypes
import queue
import threading
import time
from collections.abc import Callable
from ctypes import wintypes

from .base import RawEvent, ensure_per_monitor_dpi_awareness

WH_MOUSE_LL = 14
WH_KEYBOARD_LL = 13
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_QUIT = 0x0012
PM_NOREMOVE = 0x0000

_BTN_DOWN = {WM_LBUTTONDOWN: "left", WM_RBUTTONDOWN: "right", WM_MBUTTONDOWN: "middle"}
_BTN_UP = {WM_LBUTTONUP: "left", WM_RBUTTONUP: "right", WM_MBUTTONUP: "middle"}


class _MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM),
    ]


class _KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.WPARAM),
    ]


_CALLBACK = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
_LRESULT = ctypes.c_ssize_t
_HHOOK = getattr(wintypes, "HHOOK", ctypes.c_void_p)
_HOOKPROC = _CALLBACK(_LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


class WinApiCaptureBackend:
    def __init__(self):
        self._q: "queue.Queue[RawEvent]" = queue.Queue()
        self._paused = False
        self._t0 = 0.0
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._error: BaseException | None = None
        self._held: set[str] = set()
        self._wheel_remainder = 0
        self._sensitive_provider: Callable[[], bool | None] | None = None

    def available(self) -> bool:
        try:
            import platform

            return platform.system() == "Windows" and hasattr(ctypes, "windll")
        except Exception:
            return False

    def set_sensitive_provider(
        self, provider: Callable[[], bool | None] | None
    ) -> None:
        self._sensitive_provider = provider

    def _sensitive_state(self) -> bool | None:
        if self._sensitive_provider is None:
            return None
        try:
            return self._sensitive_provider()
        except Exception:
            return None

    def _emit(self, ev: RawEvent) -> None:
        if not self._paused:
            self._q.put(ev)

    def _run(self) -> None:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.SetWindowsHookExW.argtypes = [
            ctypes.c_int,
            _HOOKPROC,
            wintypes.HINSTANCE,
            wintypes.DWORD,
        ]
        user32.SetWindowsHookExW.restype = _HHOOK
        user32.CallNextHookEx.argtypes = [
            _HHOOK,
            ctypes.c_int,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.CallNextHookEx.restype = _LRESULT
        user32.UnhookWindowsHookEx.argtypes = [_HHOOK]
        user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        user32.GetMessageW.argtypes = [
            ctypes.POINTER(wintypes.MSG),
            wintypes.HWND,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.GetMessageW.restype = wintypes.BOOL
        user32.PostThreadMessageW.argtypes = [
            wintypes.DWORD,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.PostThreadMessageW.restype = wintypes.BOOL
        user32.GetForegroundWindow.argtypes = []
        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.c_void_p]
        user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
        user32.GetKeyboardLayout.restype = ctypes.c_void_p
        user32.GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        user32.GetKeyboardState.restype = wintypes.BOOL
        user32.ToUnicodeEx.argtypes = [
            wintypes.UINT,
            wintypes.UINT,
            ctypes.POINTER(ctypes.c_ubyte),
            wintypes.LPWSTR,
            ctypes.c_int,
            wintypes.UINT,
            ctypes.c_void_p,
        ]
        user32.ToUnicodeEx.restype = ctypes.c_int

        def mouse_proc(nCode, wParam, lParam):
            if nCode >= 0:
                info = ctypes.cast(lParam, ctypes.POINTER(_MSLLHOOKSTRUCT)).contents
                t = time.monotonic() - self._t0
                x, y = info.pt.x, info.pt.y
                w = int(wParam)
                if w in _BTN_DOWN:
                    self._emit(RawEvent("mouse_down", t, x=x, y=y, button=_BTN_DOWN[w]))
                elif w in _BTN_UP:
                    self._emit(RawEvent("mouse_up", t, x=x, y=y, button=_BTN_UP[w]))
                elif w == WM_MOUSEWHEEL:
                    delta = ctypes.c_short(info.mouseData >> 16).value
                    self._wheel_remainder += delta
                    steps = int(self._wheel_remainder / 120)
                    if steps:
                        self._wheel_remainder -= steps * 120
                        self._emit(RawEvent("wheel", t, x=x, y=y, delta=steps))
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        def kbd_proc(nCode, wParam, lParam):
            message = int(wParam)
            if nCode >= 0 and message in (
                WM_KEYDOWN,
                WM_SYSKEYDOWN,
                WM_KEYUP,
                WM_SYSKEYUP,
            ):
                info = ctypes.cast(lParam, ctypes.POINTER(_KBDLLHOOKSTRUCT)).contents
                t = time.monotonic() - self._t0
                name = self._vk_name(info.vkCode)
                sensitive = self._sensitive_state()
                if message in (WM_KEYUP, WM_SYSKEYUP):
                    self._held.discard(name)
                    self._emit(
                        RawEvent(
                            "key_up",
                            t,
                            key=name,
                            sensitive=sensitive,
                            sensitive_captured=True,
                        )
                    )
                else:
                    if name.split("_", 1)[0] in {"ctrl", "alt", "shift", "win"}:
                        self._held.add(name)
                        self._emit(
                            RawEvent(
                                "key_down",
                                t,
                                key=name,
                                sensitive=sensitive,
                                sensitive_captured=True,
                            )
                        )
                    else:
                        ch, is_dead_key = self._translate_vk(info.vkCode, info.scanCode)
                        held_modifiers = {held.split("_", 1)[0] for held in self._held}
                        if is_dead_key:
                            # A dead key has no visible standalone result yet.
                            # Windows emits the composed character for the next
                            # key (for example "^" + "e" -> "ê"). Keeping the
                            # physical OEM key as a replay step as well would
                            # duplicate or corrupt the composed text.
                            self._emit(
                                RawEvent(
                                    "dead_key",
                                    t,
                                    key=name,
                                    sensitive=sensitive,
                                    sensitive_captured=True,
                                )
                            )
                        elif ch and held_modifiers <= {"shift"}:
                            self._emit(
                                RawEvent(
                                    "char",
                                    t,
                                    char=ch,
                                    sensitive=sensitive,
                                    sensitive_captured=True,
                                )
                            )
                        else:
                            key = ch.lower() if ch else name
                            self._emit(
                                RawEvent(
                                    "key_down",
                                    t,
                                    key=key,
                                    sensitive=sensitive,
                                    sensitive_captured=True,
                                )
                            )
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        self._mp = _HOOKPROC(mouse_proc)
        self._kp = _HOOKPROC(kbd_proc)
        mh = kh = None
        try:
            mh = user32.SetWindowsHookExW(WH_MOUSE_LL, self._mp, None, 0)
            if not mh:
                raise ctypes.WinError(ctypes.get_last_error())
            kh = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._kp, None, 0)
            if not kh:
                raise ctypes.WinError(ctypes.get_last_error())
            self._thread_id = int(ctypes.windll.kernel32.GetCurrentThreadId())
            # Force creation of this thread's message queue before start()
            # exposes readiness; PostThreadMessage can then stop it reliably.
            msg = wintypes.MSG()
            user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_NOREMOVE)
            self._ready.set()
            while True:
                result = int(user32.GetMessageW(ctypes.byref(msg), None, 0, 0))
                if result == 0:  # WM_QUIT
                    break
                if result == -1:
                    raise ctypes.WinError(ctypes.get_last_error())
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        except BaseException as exc:
            self._error = exc
            self._ready.set()
        finally:
            self._thread_id = 0
            if kh:
                user32.UnhookWindowsHookEx(kh)
            if mh:
                user32.UnhookWindowsHookEx(mh)

    @staticmethod
    def _vk_name(vk: int) -> str:
        names = {
            0x0D: "enter",
            0x09: "tab",
            0x1B: "esc",
            0x08: "backspace",
            0x20: "space",
            0x2E: "delete",
            0x25: "left",
            0x26: "up",
            0x27: "right",
            0x28: "down",
            0x10: "shift",
            0x11: "ctrl",
            0x12: "alt",
            0x5B: "win_l",
            0x5C: "win_r",
            0xA0: "shift_l",
            0xA1: "shift_r",
            0xA2: "ctrl_l",
            0xA3: "ctrl_r",
            0xA4: "alt_l",
            0xA5: "alt_r",
        }
        if 0x30 <= vk <= 0x39 or 0x41 <= vk <= 0x5A:
            return chr(vk).lower()
        return names.get(vk, f"vk_{vk}")

    def _translate_vk(self, vk: int, scan: int) -> tuple[str | None, bool]:
        """Return printable text and whether *vk* is a dead key.

        ``ToUnicodeEx`` returns a negative value for a dead key. That state
        must be distinguished from an ordinary non-printable key so the
        recorder can wait for Windows' later composed character instead of
        serializing the physical OEM key as a replay action.
        """

        user32 = ctypes.windll.user32
        buf = ctypes.create_unicode_buffer(8)
        state = (ctypes.c_ubyte * 256)()
        user32.GetKeyboardState(state)
        state[vk] |= 0x80
        held_vks = {
            "shift": (0x10,),
            "shift_l": (0x10, 0xA0),
            "shift_r": (0x10, 0xA1),
            "ctrl": (0x11,),
            "ctrl_l": (0x11, 0xA2),
            "ctrl_r": (0x11, 0xA3),
            "alt": (0x12,),
            "alt_l": (0x12, 0xA4),
            "alt_r": (0x12, 0xA5),
            "win_l": (0x5B,),
            "win_r": (0x5C,),
        }
        for held in self._held:
            for held_vk in held_vks.get(held, ()):
                state[held_vk] |= 0x80

        foreground = user32.GetForegroundWindow()
        foreground_thread = (
            user32.GetWindowThreadProcessId(foreground, None) if foreground else 0
        )
        layout = user32.GetKeyboardLayout(foreground_thread)
        # Bit 2 keeps ToUnicodeEx from changing the kernel-mode keyboard
        # buffer (supported since Windows 10 1607). Dead keys return n < 0 and
        # are deliberately not serialized as literal shortcuts.
        n = user32.ToUnicodeEx(vk, scan, state, buf, len(buf), 0x4, layout)
        if n > 0:
            text = "".join(buf[index] for index in range(min(n, len(buf))))
            if text and text.isprintable():
                return text, False
        return None, n < 0

    def _vk_to_char(self, vk: int, scan: int) -> str | None:
        """Compatibility helper returning only printable translated text."""

        return self._translate_vk(vk, scan)[0]

    def start(self) -> None:
        if not self.available():
            raise RuntimeError("WinAPI capture is unavailable on this platform")
        if not ensure_per_monitor_dpi_awareness():
            raise RuntimeError(
                "per-monitor DPI awareness is unavailable; refusing mixed coordinates"
            )
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("WinAPI capture is already running")
        self._t0 = time.monotonic()
        self._stop.clear()
        self._ready.clear()
        self._error = None
        self._held.clear()
        self._wheel_remainder = 0
        self.poll()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=2.0):
            self._stop.set()
            if self._thread_id:
                ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            self._thread.join(timeout=2.0)
            raise RuntimeError("WinAPI capture hook initialization timed out")
        if self._error is not None:
            self._thread.join(timeout=2.0)
            raise RuntimeError(
                f"WinAPI capture hook initialization failed: {self._error}"
            ) from self._error

    def stop(self) -> None:
        self._stop.set()
        if self._thread_id:
            posted = ctypes.windll.user32.PostThreadMessageW(
                self._thread_id, WM_QUIT, 0, 0
            )
            if not posted:
                raise ctypes.WinError(ctypes.get_last_error())
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                raise RuntimeError("WinAPI capture thread did not stop")
        self._thread = None
        self._held.clear()
        if self._error is not None:
            error = self._error
            self._error = None
            raise RuntimeError(f"WinAPI capture failed: {error}") from error

    def set_paused(self, paused: bool) -> None:
        self._paused = paused
        if paused:
            self._held.clear()

    def poll(self) -> list[RawEvent]:
        out: list[RawEvent] = []
        while True:
            try:
                out.append(self._q.get_nowait())
            except queue.Empty:
                break
        return out
