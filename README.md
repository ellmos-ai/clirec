# clirec

[![clirec tests](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml)

`clirec` records mouse and keyboard demonstrations as human-readable `.clirec`
files and replays them through an injected executor. It is built for agent and
CLI workflows where a short demonstration is more reliable than a long verbal
description.

The core package has no runtime dependencies. Windows capture uses a ctypes
backend by default; cross-platform capture is available with the optional
`record` extra.

## Install

```bash
pip install clirec
pip install clirec[record]       # optional pynput backend
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
```

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
python -m compileall -q clirec tests
```
