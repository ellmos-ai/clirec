# CLIRec format v2

Format v2 adds optional media sidecars while preserving the human-readable
event stream. Version 1 files remain accepted by `read`, `validate`, and replay.
Recordings without audio continue to use v1 unless a v2-only feature is added.

## Commit layout

```text
demo.clirec                         commit marker, published last
demo.clirec.frames/                 optional PNG evidence
demo.clirec.media/
  manifest.json                     canonical UTF-8 JSON manifest
  audio.wav                         optional PCM WAV
  transcript.json                   optional reviewed transcript
```

The `.clirec` header references `manifest.json` by a relative path and records
its SHA-256. Each manifest entry contains a relative path, SHA-256, byte size,
kind, retention state, and kind-specific metadata. Audio additionally records
container, codec, sample rate, channel count, sample format, duration, monotonic
start offset, pause windows, consent, drift, status, and a redacted device
fingerprint. Transcript entries record the source-audio hash, provider/model,
language, redaction state, and generation method.

Absolute paths, `..`, symlinks, missing files, orphan files, duplicate IDs,
size mismatches, and hash mismatches are validation errors. Replay ignores
audio by default.

## Atomic publication and recovery

Frames, media, manifest, and the recording are built in one same-filesystem
staging directory. Sidecar directories are published before `demo.clirec`;
the `.clirec` hard link is the final no-replace commit marker. A failed commit
removes newly published sidecars. `clirec recover recordings` removes only
sidecar directories for which no commit marker exists.

Purge operations build a replacement media directory, swap it with rollback,
then publish the updated `.clirec` marker content. A crash therefore fails
closed through a manifest-hash mismatch instead of presenting partial media as
valid.
