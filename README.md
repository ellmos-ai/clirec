# clirec

<img src="assets/banner.png" width="100%" alt="Clirec banner">


[![clirec tests](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml)
[![Pytest Status](https://img.shields.io/badge/pytest-89%20passed-brightgreen.svg)](https://github.com/ellmos-ai/clirec)
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

The core package has no runtime dependencies. Windows capture uses a ctypes
backend by default; cross-platform capture is available with the optional
`record` extra. Windows UI Automation metadata is an optional `uia` extra.

## Install

```bash
pip install clirec
pip install clirec[record]       # optional pynput backend
pip install clirec[uia]          # optional Windows UI metadata
```

Until a package release exists, install directly from GitHub:

```bash
pip install git+https://github.com/ellmos-ai/clirec.git
```

## CLI

```bash
clirec start login-flow
clirec validate recordings/login-flow.clirec
clirec list --dir recordings
clirec replay recordings/login-flow.clirec --param input_1=value
```

The safe recording default never persists typed text. Each text segment becomes
a parameter such as `${input_1}` and can be supplied during replay with
`--param input_1=value`. `--allow-unmasked-input` is an explicit unsafe opt-in
for recordings whose plaintext has been reviewed before sharing.

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
