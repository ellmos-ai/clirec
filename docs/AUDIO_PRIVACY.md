# Audio, consent, and privacy

Audio is always off unless the caller explicitly enables it. The standalone
CLI requires both `--audio` and `--audio-consent`; the Python API requires
`RecorderConfig(audio_enabled=True)` and `Recorder.start(...,
audio_consent=True)`. No import, application start, ring buffer, or hidden
daemon starts a microphone.

The foreground CLI displays recording state, selected input, and destination.
`--global-hotkeys` optionally adds conflict-checked pause and stop combinations
through the `record` extra; the listener belongs to the foreground process and
is stopped with it. `Recorder.stop_audio()` can stop audio while event capture
continues.

## Limits and failure behavior

- monotonic session time is shared by events, frames, and audio chunks;
- pause windows, start offset, sample position, and measured drift are stored;
- size, duration, free-space, and drift limits are checked;
- device loss, permission denial, and I/O failures fail closed by default;
- `--audio-partial-ok` retains an explicitly marked partial track;
- audio ring buffering has its own disabled-by-default gate;
- audio is never played during replay.

Audio can capture bystanders, health information, internal conversations, and
spoken credentials. Keyboard masking does not protect spoken secrets. Real
recordings stay local and are excluded by `.gitignore`; fixtures and CI use
synthetic PCM only.

Retention is recorded per track. `purge_expired()` applies it locally. Audio
and transcripts remain separately removable with `purge-audio` and
`purge-transcript`. Raw audio is never automatically copied to Gardener, USMC,
BYUM, `.SYNC`, OneDrive, or an extractor bundle.

## Backend provenance

The current canonical public `voice` skill is a provider-neutral method core
and intentionally exposes no Python audio implementation. CLIRec therefore
imports the established optional `sounddevice` stream API through the narrow
`AudioBackend` adapter; no code was copied from proprietary Klangpult modules.

STT is a separate opt-in `TranscriptionBackend`. The canonical adapter requires
an external module with `transcribe_file(path, language=..., persist=False)`.
The mandatory `persist=False` prevents the older transcription skill's default
SQLite store from silently creating a second copy. CLIRec implements no Whisper,
Vosk, or cloud STT engine.
