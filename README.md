# clirec

<img src="assets/banner.png" width="100%" alt="Clirec banner">


[![clirec tests](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml)
[![Pytest Status](https://img.shields.io/badge/pytest-119%20passed-brightgreen.svg)](https://github.com/ellmos-ai/clirec)
[![CodeQL](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/ellmos-ai/clirec)
[![Ecosystem](https://img.shields.io/badge/ecosystem-ellmos--ai-blue.svg)](https://github.com/ellmos-ai)
[![Umbrella: open-bricks](https://img.shields.io/badge/umbrella-open--bricks-purple.svg)](https://github.com/open-bricks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Deutsch](README_de.md) | **English**

> [!NOTE]
> **AI / LLM Integration**: For machine-readable context, LLM search terms, and architecture notes, see [`llms.txt`](./llms.txt).

`clirec` records mouse and keyboard demonstrations as human-readable `.clirec`
files and replays them through an injected executor. It is built for agent and
CLI workflows where a short demonstration is more reliable than a long verbal
description.

> [!NOTE]
> **LLM & Agent-Native Design**: `clirec` format is optimized for AI agents. Plain text inputs are sanitized by default into parameterized placeholders (`${input_1}`) to preserve privacy during replay.

## Architecture & Replay Flow

```mermaid
graph TD
    User(["User / Agent"]) -->|clirec start| Recorder["Recording Engine"]
    Recorder -->|Capture Mouse & Keys| Param["Parameter Sanitizer"]
    Param -->|Human-Readable Format| Spec[".clirec File Format"]
    Spec -->|clirec validate| Val["Format Validator"]
    Spec -->|clirec replay| Executor["Injected Executor / open-compute"]
    Executor -->|Automated Actions| TargetApp["Target GUI / Terminal"]
```

The core package has no mandatory runtime dependencies. Windows capture uses a ctypes
backend by default; cross-platform capture is available with the optional
`record` extra. Windows UI Automation metadata is an optional `uia` extra.
Microphone capture is off by default and available through the optional
`audio` extra. It requires both `--audio` and `--audio-consent`.

## Install

`clirec` is **not on PyPI yet** -- `pip install clirec` does not resolve. Install
from the repository:

```bash
pip install git+https://github.com/ellmos-ai/clirec.git
pip install "clirec[record] @ git+https://github.com/ellmos-ai/clirec.git"  # pynput backend
pip install "clirec[uia] @ git+https://github.com/ellmos-ai/clirec.git"     # Windows UI metadata
pip install "clirec[audio] @ git+https://github.com/ellmos-ai/clirec.git"   # sounddevice microphone
```

Once a release exists the extras will be available as `pip install clirec[record]`
and so on. The optional extras pull in third-party dependencies with their own
licences -- `pynput` is LGPL-3.0; see
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) before redistributing.

## CLI

```bash
clirec start login-flow
clirec start narrated-flow --audio --audio-consent
clirec validate recordings/login-flow.clirec
clirec list --dir recordings
clirec replay recordings/login-flow.clirec --param input_1=value
```

The safe recording default never persists typed text. Each text segment becomes
a parameter such as `${input_1}` and can be supplied during replay with
`--param input_1=value`. `--allow-unmasked-input` is an explicit unsafe opt-in
for recordings whose plaintext has been reviewed before sharing.

Audio is a separate, explicit privacy boundary. It is never captured before
consent, during a pause, after audio stop, or by a hidden daemon. Format v2 keeps
audio and transcripts in relative SHA-256-verified `.clirec.media/` sidecars;
v1 recordings remain readable. Audio and transcripts can be purged separately:

```bash
clirec audio-devices
clirec purge-audio recordings/narrated-flow.clirec
clirec purge-transcript recordings/narrated-flow.clirec
clirec recover recordings
```

Transcription is an opt-in adapter to an external STT module. CLIRec implements
no STT engine and ships no default backend, so you name the module yourself with
`--module NAME` (or `CLIREC_STT_MODULE`); it must expose
`transcribe_file(path, language=..., persist=False)`, and the mandatory
`persist=False` keeps it from silently creating a second transcript store. The
language comes from `--lang` or `CLIREC_STT_LANGUAGE` and defaults to `en`.

Reviewed episodes and extractor jobs can be exported as JSON for `skill-extractor` or
`workflow-extract`; neither export activates a skill or schedule automatically.

See [format v2](docs/FORMAT_V2.md), [audio privacy](docs/AUDIO_PRIVACY.md), and
[episode review exports](docs/EPISODE_EXPORT.md).

Replay is backend-neutral. Use it from Python with an executor object, or via an
integration such as `open-compute`:

```bash
oc rec replay recordings/login-flow.clirec
```

## Python

```python
from clirec.format import read
from clirec.replay import replay

recording = read("recordings/login-flow.clirec")
report = replay(recording, executor)
```

`executor` must expose `width`, `height`, and `execute(action)`.

## Tests

```bash
python -m pytest -q
python -m ruff check clirec tests
python -m ruff format --check clirec tests
python -m compileall -q clirec tests
```

See [RELEASE_GATE.md](RELEASE_GATE.md) for the current package and platform
verification boundary.

## Related projects

`clirec` only records and describes a demonstration. Executing one, exposing it
to an agent, or turning audio into text happens in neighbouring projects:

| Project | What it does for `clirec` |
|---|---|
| [open-compute](https://github.com/ellmos-ai/open-compute) | Supplies the executor that actually moves the mouse and types, and wraps replay as `oc rec replay`. Without an executor a recording cannot be played back at all. |
| [open-compute-mcp](https://github.com/ellmos-ai/open-compute-mcp) | Exposes that replay as the MCP tool `rec_replay`, so an agent can run a recording without a shell. |
| [ellmos-voice-io](https://github.com/ellmos-ai/ellmos-voice-io) | Local-first speech-to-text and text-to-speech primitives -- the building block to wrap when you need a `--module` backend for `clirec transcribe`. |
| [ellmos](https://github.com/ellmos-ai/ellmos) | The ecosystem hub: which module solves which problem, and how they compose. |

## Licence

MIT, see [LICENSE](LICENSE). Optional extras carry their own licences --
`pynput` is LGPL-3.0; see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
