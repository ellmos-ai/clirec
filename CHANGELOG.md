# Changelog

This file records source changes. Publication status and release prerequisites are
tracked in [RELEASE_GATE.md](RELEASE_GATE.md).

## Unreleased

### 2026-10-03 (Pfad B Discoverability & Visual Architecture)

- Projected Section 1 ASCII Four-View Architectural Topology in `README.md` and `README_de.md` (`[VIEW 1]`..`[VIEW 4]` and `[SICHT 1]`..`[SICHT 4]`).
- Synchronized Shields.io badges for tests (138 passed | 100% green), verified currency (`Verified: 2026-10-03` / `Verifiziert: 2026-10-03`), Level 1 SBOM text companion, and contributing guidelines.
- Re-audited Level-1-SBOM companions (`THIRD_PARTY_LICENSES.md` & `THIRD_PARTY_LICENSES.txt`) Stand 2026-10-03 with cross-links to contributing guidelines and plain-text inventory.
- Synchronized `llms.txt` with Four-View topology references and 138 tests baseline.
- Extended automated contract tests in `tests/test_metadata.py` covering ASCII Four-View topology parity across English and German READMEs, Level 1 SBOM currency, and test badge recency.

- Updated public documentation to match implementation boundaries: typed-text
  masking does not cover audio, UI metadata, or optional frame evidence;
  caller-supplied transcription modules may store data or use the network;
  audio flags opt in the operator and do not collect consent from other people;
  the recorder uses current process permissions; recovery handles media
  sidecars, not optional frame directories.
- Replaced unsupported certification, zero-egress, competitor, and response-time
  guarantees with scoped implementation descriptions and response targets.
- Updated dependency-license documentation to identify declared dependencies
  without presenting the inventory as a certification. Removed internal
  operational material from the tracked source tree.

## 2026-09-29

- Added a plain-text dependency-license inventory and linked it from project
  documentation.
- Added contributor guidance and repository workflow automation; updated
  package metadata, test configuration, and the context index.

## 2026-09-26

- Added reciprocal navigation anchors to the English and German READMEs and
  expanded their persona and project-discovery sections.
- Updated package metadata, context documentation, and repository contract tests.

## 2026-09-23

- Added attribution documentation and repository workflows for contributor
  onboarding and issue/PR maintenance.
- Updated package metadata, ignore rules, and contributor documentation.

## 2026-09-16

- Added bilingual README navigation, target-user descriptions, and an earlier
  product comparison table. The unsupported comparison claims were removed in
  the 2026-10 documentation update.

## 2026-09-13

- Added CI timeouts, concurrency controls, stale-issue automation, repository
  metadata checks, and local ignore rules.

- Removed the built-in default STT module. `clirec transcribe` had a hard-coded
  fallback to a module that is published nowhere, so the only documented
  transcription path ended in `ModuleNotFoundError` for every installation that
  was not the maintainer's. The module is now named explicitly with `--module`
  or `CLIREC_STT_MODULE`, and the error says so.
- Changed the default transcription language from `de` to `en`, overridable with
  `--lang` or `CLIREC_STT_LANGUAGE`. An English-facing package silently
  transcribing as German produced transcripts whose language depended on an
  undocumented default.
- Fixed the CodeQL workflow so init and analyze use matching action versions; Dependabot groups their updates.
- Synchronised the shipped `skills/clirec/SKILL.md` with the canonical
  `SKILL.md`. The shipped copy still announced the global pause hotkey as
  planned and did not mention audio capture, although both features are present
  in the current source. The test now
  compares the two copies and rejects unbuilt-feature claims.
- Replaced organisation-internal component and folder names in `SECURITY.md`,
  `docs/AUDIO_PRIVACY.md`, `docs/EPISODE_EXPORT.md` and the Windows
  verification note with wording that is resolvable for outside readers.
- Updated installation guidance after the PyPI JSON endpoint returned HTTP 404 on 2026-09-03; current distribution evidence and its limits are recorded in `RELEASE_GATE.md`.

- Added `THIRD_PARTY_LICENSES.md`. The optional `record` extra pulls in
  `pynput` (LGPL-3.0), which was nowhere stated.
- Added a note on § 201 StGB to `SECURITY.md` and `docs/AUDIO_PRIVACY.md`:
  `--audio-consent` is the operator's consent, never a bystander's.
- Added cross-references to related Open Bricks ecosystem repositories.
- Expanded regression coverage for platform-specific capture behavior.

## 0.3.0 - unreleased

- Added opt-in microphone capture through an injectable audio contract and
  optional sounddevice adapter. Audio remains off by default.
- Added monotonic event/audio timing, pause/resume, bounded buffers and limits,
  cut_last alignment, drift reporting, separate audio stop, and optional
  foreground-owned global hotkeys.
- Added format v2 with relative SHA-256 media sidecars, publication of the
  clirec commit marker after sidecar writes, and recovery for orphaned media
  sidecars. This does not cover optional frame directories.
- Added a configurable external STT adapter that passes `persist=False` to the
  selected module; the module controls whether it honors that request.
- Added reviewed episode and skill-extractor/workflow-extract job exports.
  Audio test fixtures are synthetic.
- Fixed Windows dead-key capture so the physical OEM dead key remains raw
  evidence and is not duplicated as a replay action before Windows emits the composed
  Unicode character.
- Configured `pythonpath = "."` in `pyproject.toml` for test collection without
  an editable install.

## 0.2.1 - 2026-07-26

- Added Shields.io badges (CI, CodeQL, Python versions, License) to English and German READMEs.
- Added a GFM callout describing LLM/agent integration and default typed-text parameterization.
- Added Mermaid system architecture and replay flow diagram to both English and German READMEs.
- Ensured full German translation parity for the Python API usage section in `README_de.md`.
- Updated `llms.txt` verification timestamp to 2026-07-26.
- Updated language switcher links and explicit AI/LLM integration callout blocks in `README.md` and `README_de.md`.

## 0.2.0 - 2026-07-17

- Added default parameterization of typed keyboard text with an explicit opt-out flag.
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
