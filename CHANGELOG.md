# Changelog

Version `0.3.0` is the current source version (`pyproject.toml`, `RELEASE_GATE.md`).
It has **not** been released: the repository carries no tags, and `clirec` is not
on PyPI. Everything below `0.3.0 - unreleased` is therefore still unpublished.

## Unreleased

- Discoverability, Visual Architecture, Bilingual Navigation Parity & SBOM Invariants (Pfad B, 2026-09-26):
  - Standardized 18-point bilateral quick navigation parity with reciprocal dual HTML anchors (`<a id="sec-01"></a>` through `<a id="sec-18"></a>`) and reciprocal cross-language aliases across `README.md` and `README_de.md`.
  - Saturated GitHub repository topics and PEP 621 keywords to 20/20 topics (`agent-workflow`, `audio-recording`, `automation`, `cli`, `clirec`, `computer-use`, `demonstration`, `developer-tools`, `ellmos-ai`, `gui-automation`, `keyboard`, `local-first`, `mouse`, `open-bricks`, `privacy`, `python`, `recording`, `replay`, `screen-recording`, `zero-egress`).
  - Added Level 1 SBOM Invariant Cross-Reference Matrix table to `THIRD_PARTY_LICENSES.md` Stand 2026-09-26 mapping all 10 governance invariants `INV-LOCAL-01` through `INV-SLA-10` with verified status.
  - Hardened `pyproject.toml` with `addopts = "-ra -v --basetemp=.pytest_temp"` and extended `norecursedirs` with `.pytest_temp` and `.hypothesis`.
  - Harmonized Shields.io badges across `README.md` and `README_de.md` (`Verified: 2026-09-26`, `Last-Checked: 2026-09-26`, pytest green status).
  - Updated `llms.txt` context index with Stand 2026-09-26 recency, 20/20 topics, and Level 1 SBOM notes.
  - Documented Pfad B discoverability audit in `MARKETING-LOG.txt`.
  - Extended automated contract tests in `tests/test_metadata.py` verifying 20 saturated keywords, reciprocal dual HTML anchors `sec-01`..`sec-18`, Level 1 SBOM invariant table, and Stand 2026-09-26 recency.

- Technical Hygiene, Lifecycle CI, NOTICE Attribution & PEP 621 Hardening (Pfad A, 2026-09-23):
  - Created canonical open-source `NOTICE` attribution file designating copyright to Lukas Geiger under the ellmos-ai / open-bricks umbrella.
  - Added new contributor welcome automation workflow (`.github/workflows/welcome.yml`) using `actions/first-interaction@v3` with concurrency cancel-in-progress and 5-minute timeout.
  - Hardened `.github/workflows/stale.yml` with concurrency `cancel-in-progress: true` guard.
  - Extended `.gitignore` against additional multi-host conflict files (`*-MacBook*`, `*.sync-conflict-*`, `*.conflict`), canonical locks (`LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`), `.automation-lock`, and `.nyc_output/`.
  - Standardized `pyproject.toml` per PEP 621 with `license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md"]`, added `Notice` URL to `[project.urls]`, and configured `minversion = "7.0"` and `norecursedirs` for pytest.
  - Updated `THIRD_PARTY_LICENSES.md` to reference `NOTICE` and confirmed Level 1 SBOM recency with unprivileged `RunAsInvoker` Non-Elevation & Zero-Copyleft guarantee.
  - Synchronized documentation in `README.md`, `README_de.md` (links to `NOTICE`, statutory note § 521 BGB), and `llms.txt` (Last-checked 2026-09-23).
  - Recorded Pfad A Technical Hygiene Audit in `MARKETING-LOG.txt`.
  - Extended automated contract tests in `tests/test_metadata.py` with assertions covering NOTICE presence, welcome workflow guardrails, stale concurrency, and extended gitignore patterns.

- Discoverability, Visual Architecture, Target Personas & Comparative Matrix (Pfad B, 2026-09-16):
  - Added 18-point bilingual quick navigation parity with reciprocal anchor support across `README.md` and `README_de.md`.
  - Documented 4 target personas (`[PERSONA-01]` Autonomous AI Agent Engineers, `[PERSONA-02]` CLI Automation Builders, `[PERSONA-03]` QA & E2E Validation Engineers, `[PERSONA-04]` Privacy-Conscious Teams & Compliance Officers) and high-intent SEO queries.
  - Added 10-dimension comparative matrix vs. 4 alternatives (Video Recorders, Web E2E, Macro Recorders, Enterprise RPA) mapped to governance invariants `INV-LOCAL-01` through `INV-SLA-10`.
  - Upgraded `THIRD_PARTY_LICENSES.md` with complete SPDX audit, unprivileged `RunAsInvoker` confirmation, Zero-Copyleft assurance for demonstrations, and LGPLv3 § 4 dynamic linking transparency for `pynput`.
  - Added `Third-Party Licenses` and `Marketing Log` URLs to `pyproject.toml` [project.urls].
  - Synchronized `MARKETING-LOG.txt` and `llms.txt` (Last-checked 2026-09-16) with new discovery metadata.
  - Expanded automated contract test suite in `tests/test_metadata.py` covering navigation parity, personas, comparative matrix, third-party license audit, and governance invariants.
- Technical Hygiene Check & CI Hardening (Pfad A, 2026-09-13):
  - Hardened CI workflows (`tests.yml`, `codeql.yml`) with job-level `timeout-minutes` (15m tests/analyze, 10m package) and concurrency cancel-in-progress guards.
  - Added automated stale issues and PRs lifecycle workflow (`.github/workflows/stale.yml`).
  - Hardened `.gitignore` against multi-host conflict files (`* (kopie)*`, `* (copy)*`, `*-WORKSTATION*`, `*-ASUS*`), canonical lock files, and build/test caches.
  - Conformed `pyproject.toml` to PEP 621 with `license-files = ["LICENSE"]`, added `Issues` and `LLM Context` project URLs, configured `addopts = "-ra -v"`, and expanded ruff lint rules to `["E", "F", "W", "B", "C4"]`.
  - Added repository contract test suite `tests/test_metadata.py` covering CI timeouts, stale workflow, multi-host gitignore defense, PEP 621 metadata, version parity, and doc sync.
  - Initialized `MARKETING-LOG.txt` tracking repository hygiene and discoverability status.
  - Test suite expanded to 127 tests (100% green).
- Removed the built-in default STT module. `clirec transcribe` had a hard-coded
  fallback to a module that is published nowhere, so the only documented
  transcription path ended in `ModuleNotFoundError` for every installation that
  was not the maintainer's. The module is now named explicitly with `--module`
  or `CLIREC_STT_MODULE`, and the error says so.
- Changed the default transcription language from `de` to `en`, overridable with
  `--lang` or `CLIREC_STT_LANGUAGE`. An English-facing package silently
  transcribing as German produced transcripts whose language depended on an
  undocumented default.
- Fixed the CodeQL workflow: `init` and `analyze` were pinned to one version but
  Dependabot bumps them as two independent dependencies, so each bump produced
  two pull requests that were individually unmergeable (`Loaded a configuration
  file for version X, but running version Y`). Both are now on v4.37.9 and are
  grouped in `dependabot.yml`.
- Synchronised the shipped `skills/clirec/SKILL.md` with the canonical
  `SKILL.md`. The shipped copy still announced the global pause hotkey as
  planned and did not mention audio capture -- both shipped in 0.3.0 -- and the
  only test covering it pinned that outdated wording in place. The test now
  compares the two copies and rejects unbuilt-feature claims.
- Replaced organisation-internal component and folder names in `SECURITY.md`,
  `docs/AUDIO_PRIVACY.md`, `docs/EPISODE_EXPORT.md` and the Windows
  verification note with wording that is resolvable for outside readers.
- Corrected the install instructions: `pip install clirec` was listed first but
  does not resolve, because the package is not on PyPI.
- Added `THIRD_PARTY_LICENSES.md`. The optional `record` extra pulls in
  `pynput` (LGPL-3.0), which was nowhere stated.
- Added a note on § 201 StGB to `SECURITY.md` and `docs/AUDIO_PRIVACY.md`:
  `--audio-consent` is the operator's consent, never a bystander's.
- Added cross-references to `open-compute`, `open-compute-mcp`,
  `ellmos-voice-io` and `ellmos`; all three of the first pointed at `clirec`
  while `clirec` linked to none of them.
- Regression suite 113 -> 119 tests (117 on non-Windows hosts, where one keyboard-layout test skips).

## 0.3.0 - unreleased

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
