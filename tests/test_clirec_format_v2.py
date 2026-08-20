import hashlib
import json
import os
from pathlib import Path

import pytest

from clirec.format import Recording, Step, read
from clirec.media import (
    attach_transcript,
    purge_audio,
    purge_transcript,
    recover_orphans,
)
from clirec.recorder import Recorder, RecorderConfig
from clirec.capture.mock import MockCaptureBackend


V1 = """# clirec-version: 1
title: "legacy"
created: "now"
host: "H"
resolution: "10x10"
origin: 0,0

--- steps ---
[001] t=0   click      x=1 y=1  btn=left
"""


def test_v1_remains_readable_and_replayable(tmp_path):
    path = tmp_path / "legacy.clirec"
    path.write_text(V1, encoding="utf-8")
    recording = read(path)
    assert recording.version == 1
    assert recording.steps[0].action == "click"


def _save_v2(tmp_path):
    recorder = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    recording = Recording(
        "v2", "now", "H", "10x10", version=2, steps=[Step(1, 0.0, "key", keys="enter")]
    )
    recording.media = [
        {
            "id": "audio",
            "kind": "audio",
            "path": "audio.wav",
            "container": "wav",
            "codec": "pcm_s16le",
            "sample_rate": 10,
            "channels": 1,
            "sample_format": "int16",
            "duration": 0.1,
            "start_offset": 0.0,
            "pauses": [],
            "consent": True,
            "retention": {"status": "active", "days": 30},
        },
        {
            "id": "transcript",
            "kind": "transcript",
            "path": "transcript.json",
            "source_audio_sha256": hashlib.sha256(b"RIFF-test").hexdigest(),
            "provider": "mock",
            "model": "synthetic",
            "redacted": True,
        },
    ]
    recording._media_data = {
        "audio.wav": b"RIFF-test",
        "transcript.json": json.dumps({"text": "synthetisch"}).encode(),
    }
    path = Path(recorder.save(recording, "v2"))
    return path


def test_v2_relative_media_hashes_are_verified(tmp_path):
    path = _save_v2(tmp_path)
    recording = read(path)
    assert recording.version == 2
    assert all(not Path(item["path"]).is_absolute() for item in recording.media)
    assert len(recording.media[0]["sha256"]) == 64

    (tmp_path / "v2.clirec.media" / "audio.wav").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        read(path)


def test_v2_rejects_traversal_and_symlinked_media(tmp_path):
    path = _save_v2(tmp_path)
    manifest_path = tmp_path / "v2.clirec.media" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["media"][0]["path"] = "../escape.wav"
    payload = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    manifest_path.write_bytes(payload)
    text = path.read_text(encoding="utf-8")
    old_hash = next(
        line.split(":", 1)[1].strip().strip('"')
        for line in text.splitlines()
        if line.startswith("manifest-sha256:")
    )
    path.write_text(
        text.replace(old_hash, hashlib.sha256(payload).hexdigest()), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="relative|traversal"):
        read(path)


def test_audio_and_transcript_can_be_purged_separately(tmp_path):
    path = _save_v2(tmp_path)
    purge_transcript(path)
    after_transcript = read(path)
    assert [item["kind"] for item in after_transcript.media] == ["audio"]
    assert not (tmp_path / "v2.clirec.media" / "transcript.json").exists()

    purge_audio(path)
    after_audio = read(path)
    assert after_audio.media == []
    assert not (tmp_path / "v2.clirec.media" / "audio.wav").exists()


def test_audio_can_be_purged_while_reviewed_transcript_is_retained(tmp_path):
    path = _save_v2(tmp_path)
    purge_audio(path)
    recording = read(path)
    assert [item["kind"] for item in recording.media] == ["transcript"]
    assert (tmp_path / "v2.clirec.media" / "transcript.json").exists()


def test_attach_transcript_uses_injected_canonical_backend(tmp_path):
    path = _save_v2(tmp_path)
    purge_transcript(path)

    class Backend:
        def transcribe(self, audio_path, *, language="de"):
            assert Path(audio_path).name == "audio.wav"
            return {"text": "synthetisch", "backend": "canonical", "model": "v1"}

    descriptor = attach_transcript(path, Backend(), redacted=True)
    assert descriptor["generation"] == "canonical-adapter-no-secondary-store"
    assert [item["kind"] for item in read(path).media] == ["audio", "transcript"]


def test_recovery_removes_orphan_sidecars_but_not_committed_media(tmp_path):
    _save_v2(tmp_path)
    orphan = tmp_path / "lost.clirec.media"
    orphan.mkdir()
    (orphan / "audio.wav").write_bytes(b"synthetic")
    removed = recover_orphans(tmp_path)
    assert orphan in removed
    assert (tmp_path / "v2.clirec.media").exists()


def test_commit_marker_failure_rolls_back_published_media(tmp_path, monkeypatch):
    recorder = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    recording = Recording("atomic", "now", "H", "10x10", version=2)
    recording.media = [{"id": "audio", "kind": "audio", "path": "audio.wav"}]
    recording._media_data = {"audio.wav": b"synthetic"}

    def fail_link(_source, _destination):
        raise OSError("simulated commit-marker crash")

    monkeypatch.setattr(os, "link", fail_link)
    with pytest.raises(OSError, match="commit-marker"):
        recorder.save(recording, "atomic")
    assert not (tmp_path / "atomic.clirec").exists()
    assert not (tmp_path / "atomic.clirec.media").exists()
