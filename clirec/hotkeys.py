"""Foreground-owned global hotkeys; no daemon is started or installed."""

from __future__ import annotations


def validate_hotkeys(pause_hotkey: str, stop_hotkey: str) -> tuple[str, str]:
    pause = pause_hotkey.strip().lower()
    stop = stop_hotkey.strip().lower()
    if not pause or not stop or "+" not in pause or "+" not in stop:
        raise ValueError(
            "pause and stop hotkeys must be explicit modifier combinations"
        )
    if pause == stop:
        raise ValueError("pause and stop hotkeys conflict")
    return pause, stop


class GlobalHotkeyController:
    """Optional pynput adapter whose lifecycle is bound to the foreground CLI."""

    def __init__(self, pause_hotkey: str, stop_hotkey: str):
        self.pause_hotkey, self.stop_hotkey = validate_hotkeys(
            pause_hotkey, stop_hotkey
        )
        self._listener = None

    def start(self, *, on_pause, on_stop) -> None:
        if self._listener is not None:
            raise RuntimeError("global hotkeys are already active")
        try:
            from pynput.keyboard import GlobalHotKeys  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "global hotkeys require the optional 'record' extra (pynput)"
            ) from exc
        mappings = {
            self._pynput_form(self.pause_hotkey): on_pause,
            self._pynput_form(self.stop_hotkey): on_stop,
        }
        self._listener = GlobalHotKeys(mappings)
        self._listener.start()

    @staticmethod
    def _pynput_form(value: str) -> str:
        parts = value.split("+")
        return "+".join(
            f"<{part}>" if part in {"ctrl", "alt", "shift"} else part for part in parts
        )

    def stop(self) -> None:
        listener, self._listener = self._listener, None
        if listener is not None:
            listener.stop()
            listener.join(timeout=2.0)
