# Security Policy

## Supported versions

clirec is an alpha package. Security-relevant fixes should target the current
main branch until a stable release line exists.

## Reporting

For sensitive reports, use GitHub Private Vulnerability Reporting if it is
enabled on the repository. If unavailable, do not post sensitive details
publicly; use another private channel only if the project owner has provided one.

## Response targets and process permissions

- Initial response target: within 48 hours of receiving a report, subject to
  maintainer availability.
- Triage target: within 5 business days, subject to the report and available
  information. These are targets, not a guarantee that a fix will be delivered
  by that date.
- Process permissions: clirec uses the permissions of the process that starts
  it and does not itself request elevation.

## Local recording risks

clirec records local mouse and keyboard demonstrations and, after explicit
operator opt-in, microphone audio. Treat recordings, sidecars, transcripts,
metadata, and frame evidence as sensitive by default:

- Review recordings before sharing or committing them.
- Do not publish recordings that contain client data, credentials, private
  paths, account names, personal documents, browser sessions, or internal URLs.
- Typed text is parameterized by default. `--allow-unmasked-input` disables that
  behavior for the session.
- UI metadata and optional frame evidence can identify systems, people, or
  workflows even when keyboard text is parameterized.
- Spoken credentials are not protected by keyboard parameterization. Audio may
  also capture bystanders, health data, private conversations, or background
  devices.
- Audio is off by default. `--audio` and `--audio-consent` record the operator's
  opt-in; they do not obtain or verify anyone else's permission. Audio is not
  replayed by default.
- The recorder writes to the configured filesystem path. A selected path may be
  backed by sync or network storage. Caller-provided STT modules can read the
  audio file and may store data or make network requests; review them separately.
- Keep recordings, frame directories, media sidecars, local data, and secrets
  out of release artifacts.

## Recording other people

In Germany, § 201 (1) no. 1 StGB addresses the unauthorized recording of another
person's non-publicly spoken words. Under § 201 (4), the attempt is punishable.
The `--audio-consent` option records the operator's decision to start the
microphone. It does not establish permission from another person. See the
official text: https://www.gesetze-im-internet.de/stgb/__201.html.

Rules differ between jurisdictions and depend on context. Before recording
audio where other people may be heard, check the applicable requirements and
avoid capturing uninvolved people. This is a first orientation, not legal advice.

Replay is backend-neutral and executes through an injected executor. Integrations
must keep their own permission, confirmation, and safety gates.
