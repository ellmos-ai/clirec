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
    "stop_hotkey": "ctrl+alt+s",
    "global_hotkeys_enabled": False,
    "recordings_dir": "recordings",
    "audio_enabled": False,
    "audio_device": None,
    "audio_ringbuffer_enabled": False,
    "audio_retention_days": 30,
    "max_audio_bytes": 500 * 1024 * 1024,
    "max_duration_seconds": 4 * 60 * 60,
    "min_free_bytes": 100 * 1024 * 1024,
    "audio_fail_closed": True,
    "max_audio_drift_seconds": 0.25,
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
        audio_enabled=c.get("audio_enabled", False),
        audio_device=c.get("audio_device"),
        audio_ringbuffer_enabled=c.get("audio_ringbuffer_enabled", False),
        audio_retention_days=c.get("audio_retention_days", 30),
        max_audio_bytes=c.get("max_audio_bytes", 500 * 1024 * 1024),
        max_duration_seconds=c.get("max_duration_seconds", 4 * 60 * 60),
        min_free_bytes=c.get("min_free_bytes", 100 * 1024 * 1024),
        audio_fail_closed=c.get("audio_fail_closed", True),
        max_audio_drift_seconds=c.get("max_audio_drift_seconds", 0.25),
        global_hotkeys_enabled=c.get("global_hotkeys_enabled", False),
        pause_hotkey=c.get("pause_hotkey", "ctrl+alt+p"),
        stop_hotkey=c.get("stop_hotkey", "ctrl+alt+s"),
    )
