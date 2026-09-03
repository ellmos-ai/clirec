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
`purge-transcript`. Raw audio is never automatically copied to a memory store,
knowledge base, sync folder, cloud storage, or an extractor bundle.

## Recording other people

`--audio-consent` is the operator's own decision to open the microphone. It is
not the consent of anyone else who can be heard. In Germany, recording the
non-publicly spoken word of another person without authorisation is a criminal
offence under § 201 (1) no. 1 StGB, and other jurisdictions have comparable or
stricter rules. Obtain the agreement of everyone who may be recorded. See
[`SECURITY.md`](../SECURITY.md).

## Backend provenance

CLIRec ships no audio engine of its own. It imports the optional `sounddevice`
stream API through the narrow `AudioBackend` adapter, so the microphone
dependency stays optional and replaceable.

STT is a separate opt-in `TranscriptionBackend`. There is **no built-in default
module**: name the external module with `--module` or `CLIREC_STT_MODULE`, and
the transcription language with `--lang` or `CLIREC_STT_LANGUAGE` (`en` if
neither is set). The module must expose
`transcribe_file(path, language=..., persist=False)`; the mandatory
`persist=False` keeps the backend from silently writing a second copy of the
transcript beside CLIRec's reviewed sidecar. CLIRec implements no Whisper,
Vosk, or cloud STT engine.

For a local-first STT/TTS building block in the same ecosystem, see
[`ellmos-voice-io`](https://github.com/ellmos-ai/ellmos-voice-io). It exposes
`transcribe_file` as a method on `SpeechToText` rather than at module level and
takes no `persist` argument, so a thin wrapper module is needed to satisfy the
contract above.
