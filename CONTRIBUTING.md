# Contributing to clirec

Thank you for your interest in contributing to clirec (ellmos-ai/clirec), a
Python CLI and library for human-readable GUI demonstrations.

## Implementation notes

- The recorder core writes to the configured filesystem path and has no
  built-in telemetry. Caller-provided modules may use network services or
  additional storage.
- Typed keyboard text is parameterized by default. Review UI metadata, optional
  frames, and audio for sensitive information before sharing.
- Audio is off by default. The CLI flags record the operator's opt-in; clirec
  does not obtain or verify permission from other people.
- The `.clirec` manifest is published last, and readers validate referenced media
  hashes. Recovery removes orphan `.clirec.media` sidecars; optional
  `.clirec.frames` directories are not included.
- The selected STT module receives `persist=False`; this parameter does not
  enforce the module's storage or network behavior.
- clirec uses the permissions of the process that starts it and does not itself
  request elevation.
- The core declares no mandatory runtime dependencies. Optional extras are
  listed in `pyproject.toml`.
- Initial-response and triage times in SECURITY.md are targets subject to
  maintainer availability, not guaranteed fix deadlines.

The source version remains 0.3.0 during this maintenance cycle.

## Development setup

    git clone https://github.com/ellmos-ai/clirec.git
    cd clirec
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[all,dev]"
    pytest
    ruff check .

On PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

## Pull request guidelines

- Base branches on the current main.
- Add or update functional tests for logic or bug fixes.
- Document user-visible changes in CHANGELOG.md under Unreleased.
- Run ruff check ., pytest, and git diff --check.
- Keep changes minimal, documented, and tightly scoped.
