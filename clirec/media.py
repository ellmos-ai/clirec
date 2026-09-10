"""Validation, recovery, retention, and purge helpers for v2 sidecars."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _safe_relative(value: str, *, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.drive:
        raise ValueError(f"{label} must be a safe relative path without traversal")
    return path


def _reject_symlink_chain(root: Path, relative: Path) -> Path:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"media path contains a symlink: {relative.as_posix()}")
    return current


def load_and_validate_manifest(
    recording_path: Path, manifest_reference: str, expected_hash: str
) -> list[dict]:
    root = recording_path.parent.resolve()
    relative_manifest = _safe_relative(manifest_reference, label="manifest")
    manifest_path = _reject_symlink_chain(root, relative_manifest)
    if not manifest_path.is_file():
        raise ValueError(f"media manifest is missing: {manifest_reference}")
    payload = manifest_path.read_bytes()
    if sha256_bytes(payload) != expected_hash:
        raise ValueError("media manifest hash mismatch")
    try:
        manifest = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("media manifest is not valid UTF-8 JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != "clirec.media.v1":
        raise ValueError("unsupported media manifest schema")
    media = manifest.get("media")
    if not isinstance(media, list):
        raise ValueError("media manifest must contain a media list")

    manifest_dir = relative_manifest.parent
    referenced: set[Path] = set()
    ids: set[str] = set()
    audio_hashes: set[str] = set()
    for position, item in enumerate(media, 1):
        if not isinstance(item, dict):
            raise ValueError(f"media entry {position} must be an object")
        media_id = item.get("id")
        if not isinstance(media_id, str) or not media_id or media_id in ids:
            raise ValueError(f"media entry {position} has an invalid or duplicate id")
        ids.add(media_id)
        relative = _safe_relative(item.get("path"), label=f"media entry {position}")
        if relative.parent != manifest_dir:
            raise ValueError(
                "media references must stay directly inside the sidecar directory"
            )
        media_path = _reject_symlink_chain(root, relative)
        if not media_path.is_file():
            raise ValueError(f"media file is missing: {relative.as_posix()}")
        data = media_path.read_bytes()
        digest = item.get("sha256")
        if not isinstance(digest, str) or sha256_bytes(data) != digest:
            raise ValueError(f"media hash mismatch: {relative.as_posix()}")
        if item.get("size") != len(data):
            raise ValueError(f"media size mismatch: {relative.as_posix()}")
        referenced.add(media_path.resolve())
        if item.get("kind") == "audio":
            audio_hashes.add(digest)

    for item in media:
        if item.get("kind") == "transcript":
            source_hash = item.get("source_audio_sha256")
            if source_hash and audio_hashes and source_hash not in audio_hashes:
                raise ValueError(
                    "transcript is stale or references the wrong audio hash"
                )

    actual = {
        path.resolve()
        for path in manifest_path.parent.iterdir()
        if path.name != manifest_path.name and path.is_file()
    }
    if actual != referenced:
        raise ValueError("media sidecar contains missing or orphan files")
    return copy.deepcopy(media)


def recover_orphans(recordings_dir: str | os.PathLike) -> list[Path]:
    """Remove sidecar directories that have no `.clirec` commit marker."""

    root = Path(recordings_dir).resolve()
    removed: list[Path] = []
    if not root.is_dir():
        return removed
    for sidecar in root.glob("*.clirec.media"):
        if sidecar.is_symlink() or not sidecar.is_dir():
            continue
        marker = root / sidecar.name.removesuffix(".media")
        if not marker.exists():
            shutil.rmtree(sidecar)
            removed.append(sidecar)
    return removed


def _purge_kind(recording_path: str | os.PathLike, kind: str) -> bool:
    from .format import read, write

    target = Path(recording_path).resolve()
    recording = read(target)
    selected = [item for item in recording.media if item.get("kind") == kind]
    if not selected:
        return False
    keep = [item for item in recording.media if item.get("kind") != kind]
    manifest_ref = _safe_relative(recording.manifest_path or "", label="manifest")
    media_dir = target.parent / manifest_ref.parent
    staging = Path(
        tempfile.mkdtemp(prefix=f".{media_dir.name}.purge-", dir=target.parent)
    )
    replacement = staging / media_dir.name
    backup = staging / f"{media_dir.name}.backup"
    replacement.mkdir()
    try:
        new_media: list[dict] = []
        for item in keep:
            source = target.parent / _safe_relative(item["path"], label="media")
            destination = replacement / source.name
            destination.write_bytes(source.read_bytes())
            new_item = copy.deepcopy(item)
            new_media.append(new_item)
        manifest = {"schema": "clirec.media.v1", "media": new_media}
        manifest_payload = canonical_json(manifest)
        (replacement / "manifest.json").write_bytes(manifest_payload)

        os.replace(media_dir, backup)
        try:
            os.replace(replacement, media_dir)
            recording.media = new_media
            recording.manifest_sha256 = sha256_bytes(manifest_payload)
            write(recording, target)
        except Exception:
            if media_dir.exists():
                shutil.rmtree(media_dir)
            os.replace(backup, media_dir)
            raise
        shutil.rmtree(backup)
        return True
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def purge_audio(recording_path: str | os.PathLike) -> bool:
    return _purge_kind(recording_path, "audio")


def purge_transcript(recording_path: str | os.PathLike) -> bool:
    return _purge_kind(recording_path, "transcript")


def attach_transcript(
    recording_path: str | os.PathLike,
    backend,
    *,
    language: str | None = None,
    redacted: bool = False,
) -> dict:
    """Transcribe a v2 audio sidecar and atomically attach reviewed local text.

    ``backend`` is expected to implement the canonical ``TranscriptionBackend``
    contract.  The adapter itself is responsible for disabling any secondary
    database/store.
    """

    from .format import read, write
    from .transcription import default_language

    if language is None:
        language = default_language()

    target = Path(recording_path).resolve()
    recording = read(target)
    audio = next(
        (item for item in recording.media if item.get("kind") == "audio"), None
    )
    if audio is None:
        raise ValueError("recording has no audio track")
    if any(item.get("kind") == "transcript" for item in recording.media):
        raise FileExistsError("recording already has a transcript")
    audio_path = target.parent / _safe_relative(audio["path"], label="audio")
    result = backend.transcribe(audio_path, language=language)
    transcript_payload = canonical_json(
        {
            "schema": "clirec.transcript.v1",
            "text": result["text"],
            "language": language,
            "backend": result.get("backend"),
            "model": result.get("model"),
            "redacted": bool(redacted),
        }
    )
    manifest_ref = _safe_relative(recording.manifest_path or "", label="manifest")
    media_dir = target.parent / manifest_ref.parent
    staging = Path(
        tempfile.mkdtemp(prefix=f".{media_dir.name}.attach-", dir=target.parent)
    )
    replacement = staging / media_dir.name
    backup = staging / f"{media_dir.name}.backup"
    replacement.mkdir()
    try:
        new_media = copy.deepcopy(recording.media)
        for item in recording.media:
            source = target.parent / _safe_relative(item["path"], label="media")
            (replacement / source.name).write_bytes(source.read_bytes())
        transcript_name = "transcript.json"
        (replacement / transcript_name).write_bytes(transcript_payload)
        transcript = {
            "id": "transcript",
            "kind": "transcript",
            "path": f"{media_dir.name}/{transcript_name}",
            "sha256": sha256_bytes(transcript_payload),
            "size": len(transcript_payload),
            "source_audio_sha256": audio["sha256"],
            "provider": result.get("backend", "canonical"),
            "model": result.get("model"),
            "language": language,
            "redacted": bool(redacted),
            "generation": "canonical-adapter-no-secondary-store",
        }
        new_media.append(transcript)
        manifest_payload = canonical_json(
            {"schema": "clirec.media.v1", "media": new_media}
        )
        (replacement / "manifest.json").write_bytes(manifest_payload)
        os.replace(media_dir, backup)
        try:
            os.replace(replacement, media_dir)
            recording.media = new_media
            recording.manifest_sha256 = sha256_bytes(manifest_payload)
            write(recording, target)
        except Exception:
            if media_dir.exists():
                shutil.rmtree(media_dir)
            os.replace(backup, media_dir)
            raise
        shutil.rmtree(backup)
        return transcript
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def purge_expired(
    recordings_dir: str | os.PathLike, *, now: datetime | None = None
) -> list[Path]:
    """Purge audio whose declared local retention interval has elapsed."""

    from .format import read

    now = now or datetime.now()
    purged: list[Path] = []
    for path in Path(recordings_dir).glob("*.clirec"):
        recording = read(path)
        for item in recording.media:
            retention = item.get("retention", {})
            days = retention.get("days") if isinstance(retention, dict) else None
            if item.get("kind") != "audio" or not isinstance(days, int):
                continue
            created = datetime.fromisoformat(recording.created)
            if now >= created + timedelta(days=days) and purge_audio(path):
                purged.append(path)
                break
    return purged
