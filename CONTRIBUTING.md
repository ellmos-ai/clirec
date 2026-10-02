# Contributing to clirec

Thank you for your interest in contributing to **clirec** (`ellmos-ai/clirec`), human-readable GUI demonstration recordings for CLI and autonomous AI agent workflows.

## Principles & Core Invariants

All contributions must strictly respect and maintain our core architecture and governance invariants:

1. **100% Local-First & Zero Egress (`INV-LOCAL-01`)**: No network requests, telemetry beacons, or external tracking brokers. Offline execution is certified.
2. **Default Input Sanitization (`INV-PRIVACY-02`)**: Keystrokes are parameterized by default into `${input_N}` placeholders to safeguard secrets and credentials.
3. **Human-Readable Specification (`INV-INSPECT-03`)**: Transparent plaintext `.clirec` step format that is diffable and auditable in git without binary parsers.
4. **Decoupled Agent Replay (`INV-REPLAY-04`)**: Replay is decoupled from capture via backend-neutral executor protocols (e.g. `open-compute`).
5. **Strict Audio Consent Boundary (`INV-AUDIO-05`)**: Dual opt-in (`--audio` and `--audio-consent`) compliant with § 201 StGB; no unconsented audio capture.
6. **Format v2 Atomic Media Sidecars (`INV-SIDECAR-06`)**: Relative `.clirec.media/` storage with cryptographic SHA-256 verification and atomic commit markers.
7. **Decoupled STT Transcription (`INV-ADAPTER-07`)**: Caller-injected speech-to-text adapters enforcing `persist=False` to prevent secondary secret transcript stores.
8. **Unprivileged Execution (`INV-UNPRIV-08`)**: Operates strictly in user space under `RunAsInvoker`; zero administrator or UAC elevation requirements.
9. **Zero Mandatory Runtime Dependencies (`INV-PORTABLE-09`)**: Core engine relies solely on the Python standard library and standard Windows `ctypes`.
10. **Binding Security Response SLA (`INV-SLA-10`)**: Transparent open-source governance backed by a 48-hour response and 5-day triage SLA.
11. **Strict Version Freeze**: Under governance policy `T-20260920-167562623`, version numbers (`0.3.0` in `pyproject.toml`) remain strictly pinned across routine maintenance PRs.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/ellmos-ai/clirec.git
cd clirec

# Create virtual environment and install in editable mode with development dependencies
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\Activate.ps1 on Windows
pip install -e ".[all,dev]"

# Run full test suite
pytest

# Run linter
ruff check .
```

## Pull Request Guidelines

- Ensure your branch is rebased on `main`.
- Add or update contract tests in `tests/` for any new logic or bug fixes.
- Document changes in `CHANGELOG.md` under `## [Unreleased]`.
- Verify `ruff check .`, `pytest`, and `git diff --check` are completely clean.
- Keep changes minimal, well-documented, and tightly scoped.
