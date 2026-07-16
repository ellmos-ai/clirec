"""Cross-platform capture via pynput (opt-in: pip install clirec[record])."""

from __future__ import annotations

import queue
import time
from collections.abc import Callable

from .base import RawEvent


class PynputCaptureBackend:
    def __init__(self):
        self._q: "queue.Queue[RawEvent]" = queue.Queue()
        self._paused = False
        self._t0 = 0.0
        self._ml = None
        self._kl = None
        self._held: set[str] = set()
        self._sensitive_provider: Callable[[], bool | None] | None = None

    def available(self) -> bool:
        try:
            import pynput  # noqa: F401
            return True
        except Exception:
            return False

    def set_sensitive_provider(self, provider: Callable[[], bool | None] | None) -> None:
        self._sensitive_provider = provider

    def _sensitive_state(self) -> bool | None:
        if self._sensitive_provider is None:
            return None
        try:
            return self._sensitive_provider()
        except Exception:
            return None

    def start(self) -> None:
        from pynput import mouse, keyboard

        if self._ml is not None or self._kl is not None:
            raise RuntimeError("pynput capture is already running")
        self._t0 = time.monotonic()
        self._held.clear()
        self.poll()

        def key_name(key) -> str:
            name = getattr(key, "name", None)
            if name:
                return str(name)
            char = getattr(key, "char", None)
            return str(char) if char else str(key)

        def on_click(x, y, button, pressed):
            if self._paused:
                return
            kind = "mouse_down" if pressed else "mouse_up"
            self._q.put(RawEvent(kind, time.monotonic() - self._t0,
                                 x=int(x), y=int(y), button=button.name))

        def on_scroll(x, y, dx, dy):
            if self._paused:
                return
            self._q.put(RawEvent("wheel", time.monotonic() - self._t0,
                                 x=int(x), y=int(y), delta=int(dy)))

        def on_press(key):
            if self._paused:
                return
            name = key_name(key)
            sensitive = self._sensitive_state()
            if name in {"ctrl", "ctrl_l", "ctrl_r", "alt", "alt_l", "alt_r",
                        "alt_gr", "shift", "shift_l", "shift_r", "cmd", "cmd_l",
                        "cmd_r"}:
                self._held.add(name)
                self._q.put(
                    RawEvent(
                        "key_down",
                        time.monotonic() - self._t0,
                        key=name,
                        sensitive=sensitive,
                        sensitive_captured=True,
                    )
                )
                return
            ch = getattr(key, "char", None)
            held_modifiers = {held.split("_", 1)[0] for held in self._held}
            if ch and held_modifiers <= {"shift"}:
                self._q.put(
                    RawEvent(
                        "char",
                        time.monotonic() - self._t0,
                        char=ch,
                        sensitive=sensitive,
                        sensitive_captured=True,
                    )
                )
            else:
                self._q.put(
                    RawEvent(
                        "key_down",
                        time.monotonic() - self._t0,
                        key=name,
                        sensitive=sensitive,
                        sensitive_captured=True,
                    )
                )

        def on_release(key):
            if self._paused:
                return
            name = key_name(key)
            self._held.discard(name)
            self._q.put(
                RawEvent(
                    "key_up",
                    time.monotonic() - self._t0,
                    key=name,
                    sensitive=self._sensitive_state(),
                    sensitive_captured=True,
                )
            )

        self._ml = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        self._kl = keyboard.Listener(on_press=on_press, on_release=on_release)
        try:
            self._ml.start()
            self._kl.start()
            self._ml.wait()
            self._kl.wait()
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        listeners = (self._ml, self._kl)
        for listener in listeners:
            if listener is not None:
                listener.stop()
        for listener in listeners:
            if listener is not None:
                listener.join(timeout=1.0)
        if any(listener is not None and listener.is_alive() for listener in listeners):
            raise RuntimeError("pynput capture listener did not stop")
        self._ml = None
        self._kl = None
        self._held.clear()

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
