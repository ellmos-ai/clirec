"""Configuration helpers for clirec.

The public API is intentionally plain dictionaries plus ``RecorderConfig`` so
host projects can map their own config systems without importing clirec at
process startup.
"""

from __future__ import annotations

from typing import Any

from .recorder import RecorderConfig


DEFAULT_CONFIG: dict[str, Any] = {
    "ringbuffer_enabled": False,
    "ringbuffer_minutes": 15,
    "capture_screenshots": True,
    "mask_password_fields": True,
    "pause_hotkey": "ctrl+alt+p",
    "recordings_dir": "recordings",
}


def merge_config(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return clirec defaults shallow-merged with caller overrides."""

    if not overrides:
        return dict(DEFAULT_CONFIG)
    return {**DEFAULT_CONFIG, **overrides}


def recorder_config_from_dict(
    overrides: dict[str, Any] | None = None,
) -> RecorderConfig:
    """Map a plain config dictionary to ``RecorderConfig``."""

    c = merge_config(overrides)
    return RecorderConfig(
        recordings_dir=c.get("recordings_dir", "recordings"),
        capture_screenshots=c.get("capture_screenshots", True),
        mask_password_fields=c.get("mask_password_fields", True),
        ringbuffer_enabled=c.get("ringbuffer_enabled", False),
        ringbuffer_minutes=c.get("ringbuffer_minutes", 15),
    )
