import platform

import pytest

from clirec.capture.base import CaptureBackend, get_backend


def test_get_backend_auto_returns_capturebackend():
    be = get_backend()  # winapi on Windows, pynput otherwise
    assert isinstance(be, CaptureBackend)
    assert hasattr(be, "available")


def test_backend_available_is_bool():
    be = get_backend()
    assert isinstance(be.available(), bool)


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows keyboard layout API")
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
