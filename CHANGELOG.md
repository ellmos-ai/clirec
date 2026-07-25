# Changelog

## Unreleased

- Updated `llms.txt` index header timestamp to 2026-07-25.
- Added language switcher links and explicit AI/LLM integration callout blocks in `README.md` and `README_de.md`.

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
