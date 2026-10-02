# Third-Party License Information

> Project: ellmos-ai/clirec (source version 0.3.0)
> Project license: MIT License (see LICENSE)
> Attribution: NOTICE

This document lists direct optional and development dependencies declared in
`pyproject.toml` and links to their upstream license information. It is a
dependency license index, not a formal SBOM or a certification of legal or
runtime behavior. Transitive dependencies may vary by platform and installation.

## Optional runtime dependencies

| Package / extra | Role | License information | Upstream |
|:---|:---|:---|:---|
| pynput (record) | Optional cross-platform keyboard and mouse capture | LGPL-3.0 | https://github.com/moses-palmer/pynput/blob/master/COPYING.LESSER |
| sounddevice (audio) | Optional microphone stream adapter | MIT | https://github.com/spatialaudio/python-sounddevice/blob/master/LICENSE |
| PortAudio (used by sounddevice) | Audio I/O library | MIT | https://github.com/PortAudio/portaudio/blob/master/LICENSE.txt |
| uiautomation (uia) | Optional Windows UI Automation metadata probing | Apache-2.0 | https://github.com/yinkaisheng/Python-UIAutomation-for-Windows/blob/master/LICENSE |

The core package declares no mandatory runtime dependencies. Optional audio,
UI Automation, and capture extras are selected by the installer.

## Build and development dependencies

| Package | Role | License information | Upstream |
|:---|:---|:---|:---|
| setuptools | Build backend | MIT | https://github.com/pypa/setuptools/blob/main/LICENSE |
| build | Build frontend | MIT | https://github.com/pypa/build/blob/main/LICENSE |
| twine | Distribution checker | Apache-2.0 | https://github.com/pypa/twine/blob/main/LICENSE |
| pytest | Test runner | MIT | https://github.com/pytest-dev/pytest/blob/main/LICENSE |
| ruff | Linter and formatter | MIT / Apache-2.0 | https://github.com/astral-sh/ruff/blob/main/LICENSE-MIT |
| tomli (conditional dev extra) | TOML compatibility for Python 3.10 development tests | MIT | https://github.com/hukkin/tomli/blob/master/LICENSE |

## Runtime scope notes

- The recorder core writes to the configured filesystem path and has no
  built-in telemetry. Caller-provided modules may make network requests or use
  additional storage.
- The audio flags represent operator opt-in. clirec does not obtain or verify
  permission from other people or certify legal compliance.
- The STT adapter passes `persist=False` to the selected module; it cannot
  enforce that module's storage or network behavior.
- Readers validate media hashes in format v2 `.clirec` files. The recorder
  publishes the `.clirec` manifest last. Recovery handles orphan
  `.clirec.media` sidecars, not optional `.clirec.frames` directories.
- The application uses the permissions of the process that starts it.
- Security response times are targets subject to maintainer availability; see
  SECURITY.md.

For the project license, use LICENSE. Upstream license information is linked
above. Recording other people and sharing their data may raise separate legal
questions; see SECURITY.md and docs/AUDIO_PRIVACY.md for a first orientation.
