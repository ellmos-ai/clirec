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

## Staged publication and recovery

Frames, media, manifest, and the recording are first written to a same-filesystem
staging directory. Sidecars are published before the `.clirec` file, which
serves as the final no-replace marker for that save. A handled commit error
triggers cleanup of newly published sidecars; abrupt process or system failure
can leave orphan sidecars. `clirec recover recordings` removes unreferenced
`.clirec.media` directories. It does not remove optional `.clirec.frames`
directories.

Purge operations build a replacement media directory and swap with rollback
before updating the `.clirec` manifest. Readers validate referenced files
against recorded hashes and reject mismatches. These checks detect changed or
incomplete referenced media; the marker and hashes do not make all file
operations crash-atomic or guarantee that a whole recording cannot be
corrupted.
