# Changelog

## Unreleased

- Added opt-in streaming microphone capture through an injectable audio
  contract and optional `sounddevice` adapter; audio remains off by default and
  requires explicit consent.
- Added monotonic event/audio timing, pause/resume, bounded buffers and limits,
  `cut_last()` alignment, drift reporting, separate audio stop, and optional
  foreground-owned global hotkeys.
- Added backward-compatible format v2 with relative SHA-256 media sidecars,
  atomic commit-marker publication, recovery, retention, and separate audio and
  transcript purge.
- Added a canonical external STT adapter that mandates `persist=False`, plus
  reviewed episode and `skill-extractor`/`workflow-extract` job exports.
- Expanded the regression suite to 113 passing tests; all audio fixtures are
  synthetic and no real microphone data is stored.

- Updated `llms.txt` and `RELEASE_GATE.md` verification timestamps to 2026-08-01.
- Technical Hygiene Check (Pfad A): Verified test suite (89 passed), ruff checks 100% green, synchronized header & banner across English & German READMEs.
- Updated `llms.txt` verification timestamp to 2026-07-30.
- Synchronized Pytest test badges (`89 passed`) and added Ecosystem (`ellmos-ai`) & Umbrella (`open-bricks`) Shields.io badges in `README.md` & `README_de.md`.

- Fixed Windows dead-key capture so the physical OEM dead key remains raw
  evidence but is not duplicated as a replay action before Windows' composed
  Unicode character.
- Verified a real `oc rec replay` against Notepad with the production
  `open-compute` local executor, including parameterized Unicode text, timing,
  save, and clipboard readback.
- Verified German `^` + `e` capture and replay as exactly `ê`; documented that
  IME and mixed-DPI multi-monitor acceptance remain blocked by the current
  single-monitor host configuration.
- Expanded the regression suite to 89 passing tests; the sibling
  `open-compute` suite passes all 452 tests against this checkout.
- Configured `pythonpath = "."` in `pyproject.toml` under `[tool.pytest.ini_options]` for seamless test collection without editable install.
- Updated `llms.txt` verification timestamp to 2026-07-27.
- Verified test suite status (87 passed tests in 1.05s).

## 0.2.1 - 2026-07-26

- Added Shields.io badges (CI, CodeQL, Python versions, License) to English and German READMEs.
- Added GFM callout note highlighting LLM and agent-native design and default privacy parameterization.
- Added Mermaid system architecture and replay flow diagram to both English and German READMEs.
- Ensured full German translation parity for the Python API usage section in `README_de.md`.
- Updated `llms.txt` verification timestamp to 2026-07-26.
- Updated language switcher links and explicit AI/LLM integration callout blocks in `README.md` and `README_de.md`.

## 0.2.0 - 2026-07-17

- Parameterize all typed text by default so recordings never persist keyboard
  plaintext unless `--allow-unmasked-input` is explicitly selected.
- Hardened the `.clirec` parser, atomic/no-overwrite saving, frame-evidence
  integrity, replay timing/failure handling, and virtual-desktop coordinates.
- Reworked Windows capture lifecycle, DPI awareness, modifier/dead-key
  translation, and hook message processing; expanded backend regression tests.
- Added multi-platform test/package CI, CodeQL, dependency updates, and a
  documented release gate for the standalone package.
- Added release-hygiene documentation with `TODO.md`, `SECURITY.md`, and stricter
  local ignore rules for env files, IDE folders, local data, and SQLite files.
- Added a GitHub Actions test workflow for the standalone package.
- Added `llms.txt` and documented the local test commands in both READMEs.

## 0.1.0 - 2026-07-03

- Extracted `clirec` from `ellmos-ai/open-compute` into a standalone package.
- Kept the `.clirec` text format, recorder, segmentation, capture backends, and
  replay report model.
- Added a backend-neutral `ReplayAction` and an optional `open_compute`
  integration adapter.
