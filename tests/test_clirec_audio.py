import pytest

from clirec.audio import AudioChunk, AudioSpec, MockAudioBackend
from clirec.capture.base import RawEvent
from clirec.capture.mock import MockCaptureBackend
from clirec.recorder import Recorder, RecorderConfig


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _audio_recorder(tmp_path, *, clock=None, chunks=None, **overrides):
    clock = clock or Clock()
    audio = MockAudioBackend(
        chunks or [], spec=AudioSpec(sample_rate=10, channels=1, sample_format="int16")
    )
    config = RecorderConfig(
        recordings_dir=str(tmp_path), audio_enabled=True, **overrides
    )
    recorder = Recorder(
        MockCaptureBackend([]), config=config, audio_backend=audio, clock=clock
    )
    return recorder, audio, clock


def test_audio_is_off_by_default_and_requires_explicit_consent(tmp_path):
    recorder = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    recorder.start("silent-default")
    result = recorder.stop()
    assert result.version == 1
    assert result.media == []

    recorder, audio, _ = _audio_recorder(tmp_path)
    with pytest.raises(PermissionError, match="consent"):
        recorder.start("no-consent")
    assert audio.started is False


def test_audio_timeline_pause_resume_and_cut_are_monotonic(tmp_path):
    clock = Clock()
    chunks = [
        AudioChunk(t=0.0, start_sample=0, frames=10, data=b"\x01\x00" * 10),
        AudioChunk(t=2.0, start_sample=10, frames=10, data=b"\x02\x00" * 10),
    ]
    recorder, audio, _ = _audio_recorder(tmp_path, clock=clock, chunks=chunks)
    recorder.backend._events = [RawEvent("char", 0.0, char="a")]
    recorder.start("timeline", audio_consent=True)
    recorder.pump()
    clock.t = 1.0
    recorder.set_paused(True)
    clock.t = 2.0
    recorder.set_paused(False)
    recorder.pump()
    clock.t = 3.0
    result = recorder.cut_last(1 / 60, "last-second")
    assert result.steps == []
    assert result.media[0]["start_offset"] == pytest.approx(0.0)
    assert result.media[0]["duration"] == pytest.approx(1.0)
    assert result.media[0]["pauses"] == []
    assert audio.pause_calls == 1 and audio.resume_calls == 1


def test_audio_stop_flushes_and_save_creates_hashed_sidecar(tmp_path):
    chunk = AudioChunk(t=0.0, start_sample=0, frames=2, data=b"\x01\x00\x02\x00")
    recorder, audio, _ = _audio_recorder(tmp_path, chunks=[chunk])
    recorder.start("voice", audio_consent=True)
    recorder.pump()
    audio.queue(AudioChunk(t=0.2, start_sample=2, frames=1, data=b"\x03\x00"))
    result = recorder.stop()
    path = recorder.save(result, "voice")
    assert result.version == 2
    assert path.endswith("voice.clirec")
    assert (tmp_path / "voice.clirec.media" / "audio.wav").exists()
    assert (tmp_path / "voice.clirec.media" / "manifest.json").exists()


def test_audio_size_limit_fails_closed(tmp_path):
    chunk = AudioChunk(t=0.0, start_sample=0, frames=3, data=b"\x00\x00" * 3)
    recorder, _, _ = _audio_recorder(tmp_path, chunks=[chunk], max_audio_bytes=4)
    recorder.start("too-large", audio_consent=True)
    with pytest.raises(RuntimeError, match="size limit"):
        recorder.pump()
