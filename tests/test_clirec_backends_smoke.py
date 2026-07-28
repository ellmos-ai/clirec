import platform
from types import SimpleNamespace

import pytest

from clirec.capture.base import CaptureBackend, get_backend


def test_get_backend_auto_returns_capturebackend():
    be = get_backend()  # winapi on Windows, pynput otherwise
    assert isinstance(be, CaptureBackend)
    assert hasattr(be, "available")


def test_backend_available_is_bool():
    be = get_backend()
    assert isinstance(be.available(), bool)


def test_winapi_translation_identifies_dead_key_without_mutating_buffer(monkeypatch):
    from clirec.capture import winapi

    class DeadKeyUser32:
        @staticmethod
        def GetKeyboardState(_state):
            return 1

        @staticmethod
        def GetForegroundWindow():
            return 0

        @staticmethod
        def GetKeyboardLayout(_thread_id):
            return 0x04070407

        @staticmethod
        def ToUnicodeEx(_vk, _scan, _state, _buffer, _size, flags, _layout):
            assert flags == 0x4
            return -1

    monkeypatch.setattr(
        winapi.ctypes,
        "windll",
        SimpleNamespace(user32=DeadKeyUser32()),
        raising=False,
    )

    assert winapi.WinApiCaptureBackend()._translate_vk(0xDC, 0x29) == (None, True)


@pytest.mark.skipif(
    platform.system() != "Windows", reason="Windows keyboard layout API"
)
def test_winapi_side_specific_shift_translates_printable_keys():
    import ctypes

    from clirec.capture.winapi import WinApiCaptureBackend

    backend = WinApiCaptureBackend()
    backend.set_sensitive_provider(lambda: True)
    backend.start()
    backend.stop()
    backend._held = {"shift_l"}
    scan_a = ctypes.windll.user32.MapVirtualKeyW(0x41, 0)
    scan_1 = ctypes.windll.user32.MapVirtualKeyW(0x31, 0)
    assert backend._vk_to_char(0x41, scan_a) == "A"
    assert backend._vk_to_char(0x31, scan_1) == "!"
