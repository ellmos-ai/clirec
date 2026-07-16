"""Pull-based recorder: drain a CaptureBackend, build a clirec Recording.

Testable without threads/real hooks: the caller drives `pump()`. The live
CLI loop calls pump() on a timer.

Pure standard library (frame/probe are injected, optional).
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path

from .capture.base import RawEvent
from .format import Recording, write
from .segment import events_to_steps

_WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def validate_recording_name(name: str) -> str:
    """Return a safe local recording basename or raise ``ValueError``."""

    invalid_windows_chars = '<>:"/\\|?*'
    reserved_stem = name.split(".", 1)[0].upper() if isinstance(name, str) else ""
    if (
        not isinstance(name, str)
        or not name
        or len(name) > 128
        or name != name.strip()
        or name in {".", ".."}
        or Path(name).name != name
        or any(character in invalid_windows_chars for character in name)
        or any(ord(character) < 32 for character in name)
        or name.endswith((".", " "))
        or reserved_stem in _WINDOWS_RESERVED_NAMES
    ):
        raise ValueError(
            "recording name must be one safe local filename component "
            "(not a reserved Windows device name)"
        )
    return name


@dataclass
class RecorderConfig:
    recordings_dir: str = "recordings"
    capture_screenshots: bool = True
    # Legacy name: the safe default conservatively parameterizes all typed text
    # because field-level password detection cannot be race-free cross-platform.
    mask_password_fields: bool = True
    ringbuffer_enabled: bool = False
    ringbuffer_minutes: int = 15


def _now_iso() -> str:
    # local time without importing datetime.now at module import; cheap + ok here
    import datetime
    return datetime.datetime.now().replace(microsecond=0).isoformat()


class Recorder:
    def __init__(self, backend, *, config: RecorderConfig, probe=None,
                 frame_grabber=None, host: str = "HOST", resolution: str = "0x0",
                 origin_x: int = 0, origin_y: int = 0,
                 clock=time.monotonic):
        self.backend = backend
        self.config = config
        self.probe = probe
        self.frame_grabber = frame_grabber
        self.host = host
        self.resolution = resolution
        self.origin_x = origin_x
        self.origin_y = origin_y
        self._clock = clock
        self._title = ""
        self._buf: list[RawEvent] = []
        self._frames: dict[str, bytes] = {}
        self._started_at = 0.0
        self._running = False
        self._next_frame_id = 1

    def start(self, title: str) -> None:
        if self._running:
            raise RuntimeError("recording is already running")
        self._title = title
        self._buf = []
        self._frames = {}
        self._started_at = self._clock()
        self._next_frame_id = 1
        provider = self._mask_text_state if self.config.mask_password_fields else None
        setter = getattr(self.backend, "set_sensitive_provider", None)
        if callable(setter):
            setter(provider)
        # Pause is session state, not backend lifetime state.
        self.backend.set_paused(False)
        try:
            self.backend.start()
        except Exception:
            if callable(setter):
                setter(None)
            raise
        self._running = True

    def set_paused(self, paused: bool) -> None:
        self.backend.set_paused(paused)

    def pump(self) -> None:
        new = self.backend.poll()
        if not new:
            return
        self._bind_sensitive_events(new)
        self._bind_ui_metadata(new)
        self._buf.extend(new)
        if self.config.capture_screenshots and self.frame_grabber is not None:
            for e in new:
                if e.kind == "mouse_down":
                    png = self.frame_grabber()
                    if png is not None:
                        frame_name = f"{self._next_frame_id:04d}.png"
                        self._next_frame_id += 1
                        self._frames[frame_name] = bytes(png)
                        e.frame = frame_name
        if self.config.ringbuffer_enabled:
            self._prune(self.config.ringbuffer_minutes)

    @staticmethod
    def _mask_text_state() -> bool:
        return True

    def _bind_sensitive_events(self, events: list[RawEvent]) -> None:
        if not self.config.mask_password_fields:
            return
        for event in events:
            if event.kind in {"char", "key_down", "key_up"}:
                event.sensitive = True
                event.sensitive_captured = True

    def _bind_ui_metadata(self, events: list[RawEvent]) -> None:
        for event in events:
            if event.kind not in {"mouse_down", "wheel"} or event.ui_captured:
                continue
            if any(value is not None for value in (event.ui_name, event.ui_window, event.ui_role)):
                event.ui_captured = True
                continue
            element = None
            if self.probe is not None and event.x is not None and event.y is not None:
                try:
                    element = self.probe.element_at(event.x, event.y)
                except Exception:
                    pass
            if element:
                event.ui_name = element.get("name")
                event.ui_window = element.get("window")
                event.ui_role = element.get("role")
            # Remember even a failed/empty lookup so stop() never attaches
            # metadata from a different control minutes later.
            event.ui_captured = True

    def _prune(self, minutes: float) -> None:
        cutoff = (self._clock() - self._started_at) - minutes * 60.0
        self._buf = [e for e in self._buf if e.t >= cutoff]
        referenced = {event.frame for event in self._buf if event.frame is not None}
        self._frames = {
            frame_name: png
            for frame_name, png in self._frames.items()
            if frame_name in referenced
        }

    def _build(self, events: list[RawEvent]) -> Recording:
        rel = []
        base = events[0].t if events else 0.0
        for e in events:
            rel.append(replace(e, t=e.t - base))
        steps = events_to_steps(rel, probe=self.probe,
                                mask_passwords=self.config.mask_password_fields)
        params = []
        if self.config.mask_password_fields:
            for step in steps:
                if step.action == "type" and step.text == "***":
                    name = f"input_{len(params) + 1}"
                    step.text = "${" + name + "}"
                    params.append(
                        {
                            "name": name,
                            "desc": f"Masked keyboard input for step {step.index}",
                        }
                    )
        referenced_frames = {
            step.frame: self._frames[step.frame]
            for step in steps
            if step.frame is not None and step.frame in self._frames
        }
        return Recording(title=self._title, created=_now_iso(), host=self.host,
                         resolution=self.resolution, params=params, steps=steps,
                         origin_x=self.origin_x, origin_y=self.origin_y,
                         _frame_data=referenced_frames)

    def stop(self) -> Recording:
        stopped = not self._running
        try:
            if self._running:
                self.backend.stop()
                stopped = True
                self._running = False
                tail = self.backend.poll()
                self._bind_sensitive_events(tail)
                self._bind_ui_metadata(tail)
                self._buf.extend(tail)
            return self._build(self._buf)
        finally:
            if stopped:
                self._running = False
                self._buf = []
                self._frames = {}

    def cut_last(self, minutes: float, title: str) -> Recording:
        cutoff = (self._clock() - self._started_at) - minutes * 60.0
        kept = [e for e in self._buf if e.t >= cutoff]
        self._title = title
        return self._build(kept)

    def save(self, rec: Recording, name: str) -> str:
        name = validate_recording_name(name)

        root = Path(self.config.recordings_dir)
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{name}.clirec"
        frames_dir = Path(f"{path}.frames")
        if path.exists() or frames_dir.exists():
            raise FileExistsError(f"recording already exists: {path}")

        referenced_frames = {step.frame for step in rec.steps if step.frame is not None}
        provided_frames = set(rec._frame_data)
        if referenced_frames != provided_frames:
            missing = sorted(referenced_frames - provided_frames)
            orphaned = sorted(provided_frames - referenced_frames)
            details = []
            if missing:
                details.append(f"missing frame data: {', '.join(missing)}")
            if orphaned:
                details.append(f"orphan frame data: {', '.join(orphaned)}")
            raise ValueError("frame evidence is inconsistent: " + "; ".join(details))

        for frame_name, png in rec._frame_data.items():
            if Path(frame_name).name != frame_name or not frame_name.lower().endswith(".png"):
                raise ValueError(f"invalid frame filename: {frame_name!r}")
            if not isinstance(png, bytes):
                raise TypeError(f"frame {frame_name!r} must contain bytes")

        staging = Path(tempfile.mkdtemp(prefix=f".{name}.", suffix=".tmp", dir=root))
        frames_committed = False
        recording_committed = False
        try:
            staged_recording = staging / path.name
            write(rec, staged_recording)
            staged_frames = staging / frames_dir.name
            if rec._frame_data:
                staged_frames.mkdir()
                for frame_name, png in rec._frame_data.items():
                    with open(staged_frames / frame_name, "xb") as handle:
                        handle.write(png)
                        handle.flush()
                        os.fsync(handle.fileno())

            if rec._frame_data:
                os.replace(staged_frames, frames_dir)
                frames_committed = True
            # The recording is the commit marker.  A hard link publishes its
            # complete staged bytes atomically and fails instead of replacing
            # an existing recording.  Keeping staging on the same filesystem
            # makes this a safe no-replace primitive on Windows, macOS, Linux.
            os.link(staged_recording, path)
            recording_committed = True
            return str(path)
        except Exception:
            if not recording_committed and frames_committed and frames_dir.exists():
                shutil.rmtree(frames_dir)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
