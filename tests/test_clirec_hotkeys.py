import pytest

from clirec.hotkeys import GlobalHotkeyController, validate_hotkeys


def test_hotkey_conflicts_are_rejected():
    with pytest.raises(ValueError, match="conflict"):
        validate_hotkeys("ctrl+alt+p", "CTRL+ALT+P")


def test_hotkeys_require_modifier_combinations():
    with pytest.raises(ValueError, match="modifier"):
        validate_hotkeys("p", "ctrl+alt+s")


def test_pynput_mapping_is_explicit():
    controller = GlobalHotkeyController("ctrl+alt+p", "ctrl+alt+s")
    assert controller._pynput_form(controller.pause_hotkey) == "<ctrl>+<alt>+p"
