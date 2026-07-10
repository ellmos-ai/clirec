# Changelog

## Unreleased

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
