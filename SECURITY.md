# Security Policy

## Supported Versions

`clirec` is currently an alpha package. Security-relevant fixes should target the
current `main` branch until a stable release line exists.

## Reporting

For private reports, use GitHub private vulnerability reporting if it is enabled
on the repository. If that is unavailable, open a minimal private issue or
contact the maintainer without attaching sensitive recordings.

## Local Recording Risks

`clirec` records local mouse and keyboard demonstrations and, only after a
separate opt-in, microphone audio. Treat recordings, sidecars, transcripts, and
frame evidence as sensitive by default:

- Review recordings before sharing or committing them.
- Do not publish recordings that contain client data, credentials, private
  paths, account names, personal documents, browser sessions, or internal URLs.
- The safe default parameterizes all typed text as `${input_N}` instead of
  persisting plaintext. `--allow-unmasked-input` disables that protection for
  the complete session and must only be used with deliberate review.
- UI metadata and frame evidence can still identify systems, people, or
  workflows even when keyboard text is parameterized.
- Spoken credentials are not protected by keyboard parameterization. Audio may
  also capture bystanders, health data, private conversations, or background
  devices. Obtain consent and use a quiet, controlled local environment.
- Audio is off by default, requires explicit consent, and is never replayed by
  default. Use retention and the separate audio/transcript purge commands.
- Keep `recordings/`, `*.clirec.frames/`, `*.clirec.media/`, audio files,
  `_session/`, local data, and secrets out of release artifacts.
- Never auto-ingest raw audio into a memory store, knowledge base, sync folder,
  cloud storage, extractor job, package, CI artifact, or public repository.

## Recording other people

Recording a person's speech is not only a privacy question. In Germany,
§ 201 (1) no. 1 StGB makes it a criminal offence, punishable by up to three
years' imprisonment or a fine, to record the non-publicly spoken word of
another person without authorisation; the attempt is punishable as well
(§ 201 (4) StGB). `--audio-consent` records *your* decision to start the
microphone. It is not, and cannot be, the consent of anyone else in the room.
Comparable rules exist in other jurisdictions, several of which require the
agreement of every participant.

Before recording audio in the presence of others, obtain their agreement, and
prefer a controlled setting in which no uninvolved person is captured. This is
a first orientation, not legal advice.

Replay is backend-neutral and executes through an injected executor. Integrations
must keep their own permission, confirmation, and safety gates.
