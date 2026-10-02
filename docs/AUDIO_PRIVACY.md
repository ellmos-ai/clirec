# Audio, consent, and privacy

Audio is off unless the caller explicitly enables it. The standalone CLI
requires both `--audio` and `--audio-consent`; the Python API requires
`RecorderConfig(audio_enabled=True)` and `Recorder.start(..., audio_consent=True)`.
These settings record the operator's choice. They do not obtain or verify
permission from anyone else or establish legal compliance.

The foreground CLI displays recording state, selected input, and destination.
`--global-hotkeys` optionally adds conflict-checked pause and stop combinations
through the record extra; the listener belongs to the foreground process and is
stopped with it. Recorder.stop_audio() can stop audio while event capture
continues.

## Limits and failure behavior

- monotonic session time is shared by events, frames, and audio chunks;
- pause windows, start offset, sample position, and measured drift are stored;
- size, duration, free-space, and drift limits are checked;
- device loss, permission denial, and I/O failures fail closed by default;
- `--audio-partial-ok` retains an explicitly marked partial track;
- audio ring buffering has its own disabled-by-default gate;
- audio is never played during replay.

Audio may capture bystanders, health information, internal conversations, and
spoken credentials. Keyboard masking does not protect spoken secrets. The
recorder writes to the configured filesystem path; a selected path may be
synced or network-mounted. Tests and CI use synthetic PCM only.

Retention is recorded per track. `purge_expired()` applies it to eligible files.
Audio and transcripts are separately removable with `purge-audio` and
`purge-transcript`. The core does not create a separate memory-store,
knowledge-base, or extractor copy. The configured path may itself be
synchronized or network-mounted. A caller-provided transcription module can
read the audio file and may have its own storage or network behavior.

## Recording other people

In Germany, § 201 (1) no. 1 StGB addresses the unauthorized recording of another
person's non-publicly spoken words. The `--audio-consent` option records the
operator's decision to open the microphone and does not establish permission
from other people. See the official text:
https://www.gesetze-im-internet.de/stgb/__201.html.
Check the rules that apply to the recording context and avoid recording
uninvolved people. This is a first orientation, not legal advice; see
SECURITY.md.

## Backend provenance

clirec ships no audio engine of its own. It imports the optional sounddevice
stream API through the AudioBackend adapter, so the microphone dependency
stays optional and replaceable.

STT is a separate opt-in TranscriptionBackend. There is no built-in default
module: select the external module with `--module` or CLIREC_STT_MODULE, and
the transcription language with `--lang` or CLIREC_STT_LANGUAGE (en if neither
is set). The adapter calls the selected module with
`transcribe_file(path, language=..., persist=False)`. `persist=False` is a
parameter passed to the external module, not an enforced storage or network
control; review that module's behavior before using it. clirec implements no
Whisper, Vosk, or cloud STT engine.

For a local-first STT/TTS building block in the same ecosystem, see
https://github.com/ellmos-ai/ellmos-voice-io. It exposes transcribe_file as a
method on SpeechToText rather than at module level and takes no persist
argument, so a thin wrapper module is needed to satisfy the contract above.
