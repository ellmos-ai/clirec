"""Optional streaming-audio contracts and backends.

The core remains dependency-free.  Real microphone capture is provided by the
optional, imported ``sounddevice`` backend; tests use ``MockAudioBackend`` and
never touch hardware.
"""

from __future__ import annotations

import hashlib
import queue
import threading
import time
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class AudioSpec:
    sample_rate: int = 16_000
    channels: int = 1
    sample_format: str = "int16"

    @property
    def bytes_per_sample(self) -> int:
        sizes = {"int16": 2, "int32": 4, "float32": 4}
        try:
            return sizes[self.sample_format]
        except KeyError as exc:
            raise ValueError(
                f"unsupported audio sample format: {self.sample_format}"
            ) from exc


@dataclass(frozen=True)
class AudioChunk:
    """A bounded PCM chunk positioned on the session's monotonic timeline."""

    t: float
    start_sample: int
    frames: int
    data: bytes


@runtime_checkable
class AudioBackend(Protocol):
    spec: AudioSpec

    def list_devices(self) -> list[dict[str, str]]: ...
    def start(self, device_id: str | None = None) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def stop(self) -> None: ...
    def poll(self) -> list[AudioChunk]: ...
    def device_fingerprint(self) -> str | None: ...


class MockAudioBackend:
    """Deterministic backend for tests and synthetic CLI smokes."""

    def __init__(self, chunks: list[AudioChunk], *, spec: AudioSpec | None = None):
        self.spec = spec or AudioSpec()
        self._chunks = list(chunks)
        self.started = False
        self.paused = False
        self.pause_calls = 0
        self.resume_calls = 0

    def list_devices(self) -> list[dict[str, str]]:
        return [{"id": "mock", "label": "Synthetic test input"}]

    def start(self, device_id: str | None = None) -> None:
        self.started = True
        self.paused = False

    def pause(self) -> None:
        self.paused = True
        self.pause_calls += 1

    def resume(self) -> None:
        self.paused = False
        self.resume_calls += 1

    def stop(self) -> None:
        self.started = False

    def poll(self) -> list[AudioChunk]:
        if not self.started or self.paused:
            return []
        chunks, self._chunks = self._chunks, []
        return chunks

    def queue(self, chunk: AudioChunk) -> None:
        self._chunks.append(chunk)

    def device_fingerprint(self) -> str:
        return "mock"


class SoundDeviceAudioBackend:
    """Thin optional adapter around the canonical ``sounddevice`` stream API."""

    def __init__(self, *, spec: AudioSpec | None = None, clock=time.monotonic):
        self.spec = spec or AudioSpec()
        self._clock = clock
        self._queue: queue.SimpleQueue[AudioChunk] = queue.SimpleQueue()
        self._lock = threading.Lock()
        self._stream = None
        self._paused = False
        self._sample_position = 0
        self._device_id: str | None = None

    @staticmethod
    def _module():
        try:
            import sounddevice  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "audio capture requires the optional 'audio' extra (sounddevice)"
            ) from exc
        return sounddevice

    def list_devices(self) -> list[dict[str, str]]:
        devices = self._module().query_devices()
        return [
            {"id": str(index), "label": str(device.get("name", "input"))}
            for index, device in enumerate(devices)
            if int(device.get("max_input_channels", 0)) > 0
        ]

    def start(self, device_id: str | None = None) -> None:
        if self._stream is not None:
            raise RuntimeError("audio stream is already running")
        module = self._module()
        self._device_id = device_id
        self._sample_position = 0
        self._paused = False

        def callback(indata, frames, _time_info, status):
            if status:
                raise RuntimeError(f"audio backend status: {status}")
            with self._lock:
                start_sample = self._sample_position
                self._sample_position += int(frames)
                paused = self._paused
            if not paused:
                self._queue.put(
                    AudioChunk(
                        t=self._clock(),
                        start_sample=start_sample,
                        frames=int(frames),
                        data=bytes(indata),
                    )
                )

        self._stream = module.RawInputStream(
            samplerate=self.spec.sample_rate,
            channels=self.spec.channels,
            dtype=self.spec.sample_format,
            device=int(device_id) if device_id is not None else None,
            callback=callback,
        )
        self._stream.start()

    def pause(self) -> None:
        with self._lock:
            self._paused = True

    def resume(self) -> None:
        with self._lock:
            self._paused = False

    def stop(self) -> None:
        stream, self._stream = self._stream, None
        if stream is not None:
            stream.stop()
            stream.close()

    def poll(self) -> list[AudioChunk]:
        chunks: list[AudioChunk] = []
        while True:
            try:
                chunks.append(self._queue.get_nowait())
            except queue.Empty:
                return chunks

    def device_fingerprint(self) -> str | None:
        if self._device_id is None:
            return None
        return hashlib.sha256(self._device_id.encode("utf-8")).hexdigest()[:16]


def get_audio_backend(name: str = "sounddevice") -> AudioBackend:
    if name == "sounddevice":
        return SoundDeviceAudioBackend()
    if name == "mock":
        return MockAudioBackend([])
    raise RuntimeError(f"unknown audio backend: {name!r}")
