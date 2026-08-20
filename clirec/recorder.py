"""Pull-based recorder: drain a CaptureBackend, build a clirec Recording.

Testable without threads/real hooks: the caller drives `pump()`. The live
CLI loop calls pump() on a timer.

Pure standard library (frame/probe are injected, optional).
"""

from __future__ import annotations

import io
import os
import shutil
import tempfile
import time
import wave
from dataclasses import dataclass, replace
from pathlib import Path

from .audio import AudioChunk, AudioSpec
from .capture.base import RawEvent
from .format import Recording, write
from .media import canonical_json, sha256_bytes
from .segment import events_to_steps

_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
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
    audio_enabled: bool = False
    audio_device: str | None = None
    audio_ringbuffer_enabled: bool = False
    audio_retention_days: int = 30
    max_audio_bytes: int = 500 * 1024 * 1024
    max_duration_seconds: float = 4 * 60 * 60
    min_free_bytes: int = 100 * 1024 * 1024
    audio_fail_closed: bool = True
    max_audio_drift_seconds: float = 0.25
    global_hotkeys_enabled: bool = False
    pause_hotkey: str = "ctrl+alt+p"
    stop_hotkey: str = "ctrl+alt+s"


def _now_iso() -> str:
    # local time without importing datetime.now at module import; cheap + ok here
    import datetime

    return datetime.datetime.now().replace(microsecond=0).isoformat()


class Recorder:
    def __init__(
        self,
        backend,
        *,
        config: RecorderConfig,
        probe=None,
        frame_grabber=None,
        audio_backend=None,
        host: str = "HOST",
        resolution: str = "0x0",
        origin_x: int = 0,
        origin_y: int = 0,
        clock=time.monotonic,
    ):
        self.backend = backend
        self.config = config
        self.probe = probe
        self.frame_grabber = frame_grabber
        self.audio_backend = audio_backend
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
        self._audio_chunks: list[AudioChunk] = []
        self._audio_started_offset = 0.0
        self._audio_error: str | None = None
        self._audio_running = False
        self._paused = False
        self._pause_started_at: float | None = None
        self._pause_windows: list[tuple[float, float]] = []

    def start(self, title: str, *, audio_consent: bool = False) -> None:
        if self._running:
            raise RuntimeError("recording is already running")
        if self.config.audio_enabled and not audio_consent:
            raise PermissionError("explicit audio consent is required")
        if self.config.audio_enabled and self.audio_backend is None:
            raise RuntimeError("audio is enabled but no AudioBackend was provided")
        root = Path(self.config.recordings_dir)
        root.mkdir(parents=True, exist_ok=True)
        if self.config.audio_enabled:
            free = shutil.disk_usage(root).free
            if free < self.config.min_free_bytes:
                raise RuntimeError("insufficient free space for audio recording")
        self._title = title
        self._buf = []
        self._frames = {}
        self._audio_chunks = []
        self._audio_error = None
        self._audio_running = False
        self._paused = False
        self._pause_started_at = None
        self._pause_windows = []
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
            if self.config.audio_enabled:
                self.audio_backend.start(self.config.audio_device)
                self._audio_started_offset = self._clock() - self._started_at
                self._audio_running = True
        except Exception:
            try:
                self.backend.stop()
            except Exception:
                pass
            if callable(setter):
                setter(None)
            raise
        self._running = True

    def set_paused(self, paused: bool) -> None:
        if not self._running:
            raise RuntimeError("recording is not running")
        paused = bool(paused)
        if paused == self._paused:
            return
        now = self._clock()
        if paused:
            self._pause_started_at = now
            if self._audio_running:
                self.audio_backend.pause()
        else:
            if self._pause_started_at is not None:
                self._pause_windows.append(
                    (
                        self._pause_started_at - self._started_at,
                        now - self._started_at,
                    )
                )
            self._pause_started_at = None
            if self._audio_running:
                self.audio_backend.resume()
        self._paused = paused
        self.backend.set_paused(paused)

    def pump(self) -> None:
        new = self.backend.poll()
        if new:
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
        self._poll_audio()
        if self.config.ringbuffer_enabled:
            self._prune(self.config.ringbuffer_minutes)

    def _poll_audio(self) -> None:
        if not self._audio_running:
            return
        try:
            chunks = self.audio_backend.poll()
            for chunk in chunks:
                if not isinstance(chunk, AudioChunk):
                    raise TypeError("AudioBackend.poll() must return AudioChunk values")
                expected = (
                    chunk.frames
                    * self.audio_backend.spec.channels
                    * self.audio_backend.spec.bytes_per_sample
                )
                if chunk.frames < 0 or len(chunk.data) != expected:
                    raise ValueError("audio chunk byte count does not match its format")
            self._audio_chunks.extend(chunks)
            size = sum(len(chunk.data) for chunk in self._audio_chunks)
            if size > self.config.max_audio_bytes:
                raise RuntimeError("audio size limit exceeded")
            if self._clock() - self._started_at > self.config.max_duration_seconds:
                raise RuntimeError("recording duration limit exceeded")
        except Exception as exc:
            self._audio_error = str(exc)
            if self.config.audio_fail_closed:
                self.stop_audio()
                raise

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
            if any(
                value is not None
                for value in (event.ui_name, event.ui_window, event.ui_role)
            ):
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
        if self.config.audio_ringbuffer_enabled:
            self._audio_chunks = [
                chunk
                for chunk in self._audio_chunks
                if self._chunk_relative_end(chunk) >= cutoff
            ]

    def _chunk_relative_start(self, chunk: AudioChunk) -> float:
        return float(chunk.t) - self._started_at

    def _chunk_relative_end(self, chunk: AudioChunk) -> float:
        return self._chunk_relative_start(chunk) + (
            chunk.frames / self.audio_backend.spec.sample_rate
        )

    @staticmethod
    def _wav_bytes(spec: AudioSpec, pcm: bytes) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(spec.channels)
            wav.setsampwidth(spec.bytes_per_sample)
            wav.setframerate(spec.sample_rate)
            wav.writeframes(pcm)
        return buffer.getvalue()

    def _audio_for_window(
        self, window_start: float
    ) -> tuple[list[dict], dict[str, bytes]]:
        if not self.config.audio_enabled:
            return [], {}
        spec = self.audio_backend.spec
        selected = [
            chunk
            for chunk in self._audio_chunks
            if self._chunk_relative_end(chunk) > window_start
        ]
        if not selected:
            pcm = b""
            start_offset = max(0.0, self._audio_started_offset - window_start)
        else:
            payloads: list[bytes] = []
            first_start: float | None = None
            frame_bytes = spec.channels * spec.bytes_per_sample
            for chunk in selected:
                chunk_start = self._chunk_relative_start(chunk)
                trim_frames = max(
                    0, int(round((window_start - chunk_start) * spec.sample_rate))
                )
                trim_frames = min(trim_frames, chunk.frames)
                if trim_frames < chunk.frames:
                    if first_start is None:
                        first_start = max(chunk_start, window_start)
                    payloads.append(chunk.data[trim_frames * frame_bytes :])
            pcm = b"".join(payloads)
            start_offset = max(0.0, (first_start or window_start) - window_start)
        total_frames = len(pcm) // (spec.channels * spec.bytes_per_sample)
        duration = total_frames / spec.sample_rate
        pauses = []
        for start, end in self._pause_windows:
            clipped_start = max(start, window_start)
            clipped_end = max(clipped_start, end)
            if clipped_end > window_start and clipped_end > clipped_start:
                pauses.append(
                    [clipped_start - window_start, clipped_end - window_start]
                )
        timeline_end = 0.0
        if selected:
            timeline_end = (
                max(self._chunk_relative_end(chunk) for chunk in selected)
                - window_start
            )
        paused_duration = sum(end - start for start, end in pauses)
        drift = max(0.0, timeline_end - start_offset - paused_duration - duration)
        status = "partial" if self._audio_error else "complete"
        if drift > self.config.max_audio_drift_seconds:
            status = "partial"
            self._audio_error = (
                f"audio drift {drift:.6f}s exceeds "
                f"{self.config.max_audio_drift_seconds:.6f}s"
            )
            if self.config.audio_fail_closed:
                raise RuntimeError(self._audio_error)
        wav = self._wav_bytes(spec, pcm)
        media = [
            {
                "id": "audio",
                "kind": "audio",
                "path": "audio.wav",
                "container": "wav",
                "codec": "pcm_s16le"
                if spec.sample_format == "int16"
                else spec.sample_format,
                "sample_rate": spec.sample_rate,
                "channels": spec.channels,
                "sample_format": spec.sample_format,
                "duration": duration,
                "timeline_duration": max(0.0, timeline_end),
                "start_offset": start_offset,
                "pauses": pauses,
                "consent": True,
                "status": status,
                "error": self._audio_error,
                "drift_seconds": drift,
                "device": self.audio_backend.device_fingerprint(),
                "retention": {
                    "status": "active",
                    "days": self.config.audio_retention_days,
                },
            }
        ]
        return media, {"audio.wav": wav}

    def _build(self, events: list[RawEvent], *, window_start: float = 0.0) -> Recording:
        rel = []
        base = (
            self._started_at + window_start
            if self.config.audio_enabled
            else (events[0].t if events else 0.0)
        )
        for e in events:
            rel.append(replace(e, t=e.t - base))
        steps = events_to_steps(
            rel, probe=self.probe, mask_passwords=self.config.mask_password_fields
        )
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
        media, media_data = self._audio_for_window(window_start)
        return Recording(
            title=self._title,
            created=_now_iso(),
            host=self.host,
            resolution=self.resolution,
            params=params,
            steps=steps,
            origin_x=self.origin_x,
            origin_y=self.origin_y,
            version=2 if media else 1,
            media=media,
            _frame_data=referenced_frames,
            _media_data=media_data,
        )

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
                if self._paused and self._pause_started_at is not None:
                    now = self._clock()
                    self._pause_windows.append(
                        (
                            self._pause_started_at - self._started_at,
                            now - self._started_at,
                        )
                    )
                    self._pause_started_at = None
                    self._paused = False
                self.stop_audio()
                return self._build(self._buf)
            return self._build(self._buf)
        finally:
            if stopped:
                self._running = False
                self._buf = []
                self._frames = {}
                self._audio_chunks = []

    def stop_audio(self) -> None:
        """Stop and flush only the audio track; event recording can continue."""

        if not self._audio_running:
            return
        try:
            self._audio_chunks.extend(self.audio_backend.poll())
            self.audio_backend.stop()
            self._audio_chunks.extend(self.audio_backend.poll())
        finally:
            self._audio_running = False

    def cut_last(self, minutes: float, title: str) -> Recording:
        cutoff = (self._clock() - self._started_at) - minutes * 60.0
        kept = [e for e in self._buf if e.t >= cutoff]
        self._title = title
        return self._build(kept, window_start=max(0.0, cutoff))

    def save(self, rec: Recording, name: str) -> str:
        name = validate_recording_name(name)

        root = Path(self.config.recordings_dir)
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{name}.clirec"
        frames_dir = Path(f"{path}.frames")
        media_dir = Path(f"{path}.media")
        if path.exists() or frames_dir.exists() or media_dir.exists():
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
            if Path(frame_name).name != frame_name or not frame_name.lower().endswith(
                ".png"
            ):
                raise ValueError(f"invalid frame filename: {frame_name!r}")
            if not isinstance(png, bytes):
                raise TypeError(f"frame {frame_name!r} must contain bytes")

        media_entries: list[dict] = []
        referenced_media: set[str] = set()
        for item in rec.media:
            if not isinstance(item, dict):
                raise TypeError("media descriptors must be objects")
            local_name = item.get("path")
            if (
                not isinstance(local_name, str)
                or Path(local_name).name != local_name
                or local_name in {"", "manifest.json"}
            ):
                raise ValueError(f"invalid local media filename: {local_name!r}")
            if local_name in referenced_media:
                raise ValueError(f"duplicate media filename: {local_name}")
            referenced_media.add(local_name)
            if local_name not in rec._media_data:
                raise ValueError(f"missing media data: {local_name}")
            payload = rec._media_data[local_name]
            if not isinstance(payload, bytes):
                raise TypeError(f"media {local_name!r} must contain bytes")
            descriptor = dict(item)
            descriptor["path"] = f"{media_dir.name}/{local_name}"
            descriptor["sha256"] = sha256_bytes(payload)
            descriptor["size"] = len(payload)
            media_entries.append(descriptor)
        orphan_media = sorted(set(rec._media_data) - referenced_media)
        if orphan_media:
            raise ValueError("orphan media data: " + ", ".join(orphan_media))

        manifest_payload = b""
        published = rec
        if media_entries:
            manifest_payload = canonical_json(
                {"schema": "clirec.media.v1", "media": media_entries}
            )
            published = replace(
                rec,
                version=2,
                manifest_path=f"{media_dir.name}/manifest.json",
                manifest_sha256=sha256_bytes(manifest_payload),
                media=media_entries,
                _media_data={},
            )

        staging = Path(tempfile.mkdtemp(prefix=f".{name}.", suffix=".tmp", dir=root))
        frames_committed = False
        media_committed = False
        recording_committed = False
        try:
            staged_recording = staging / path.name
            write(published, staged_recording)
            staged_frames = staging / frames_dir.name
            if rec._frame_data:
                staged_frames.mkdir()
                for frame_name, png in rec._frame_data.items():
                    with open(staged_frames / frame_name, "xb") as handle:
                        handle.write(png)
                        handle.flush()
                        os.fsync(handle.fileno())

            staged_media = staging / media_dir.name
            if media_entries:
                staged_media.mkdir()
                for local_name in sorted(referenced_media):
                    with open(staged_media / local_name, "xb") as handle:
                        handle.write(rec._media_data[local_name])
                        handle.flush()
                        os.fsync(handle.fileno())
                with open(staged_media / "manifest.json", "xb") as handle:
                    handle.write(manifest_payload)
                    handle.flush()
                    os.fsync(handle.fileno())

            if rec._frame_data:
                os.replace(staged_frames, frames_dir)
                frames_committed = True
            if media_entries:
                os.rename(staged_media, media_dir)
                media_committed = True
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
            if not recording_committed and media_committed and media_dir.exists():
                shutil.rmtree(media_dir)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
