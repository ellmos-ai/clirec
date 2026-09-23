# clirec

<img src="assets/banner.svg" width="100%" alt="clirec banner">
<!-- alternate banner: assets/banner-b.png (swap on occasion) -->

[English](README.md) | [Deutsch](README_de.md)

[![clirec tests](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml)
[![Pytest Status](https://img.shields.io/badge/pytest-132%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![CodeQL](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/ellmos-ai/clirec)
[![Privacy](https://img.shields.io/badge/privacy-100%25%20Local--First%20%7C%20Zero--Egress-success.svg)](#5-governance--runtime-invariants)
[![Security](https://img.shields.io/badge/security-RunAsInvoker%20%7C%20Non--Elevation-informational.svg)](SECURITY.md)
[![Security SLA](https://img.shields.io/badge/security%20SLA-48h%20%2F%205d-blue.svg)](SECURITY.md)
[![Third-Party Audited](https://img.shields.io/badge/third--party-audited%20%7C%20MIT%20Core%20%7C%20LGPL--3.0%20Extra-success.svg)](THIRD_PARTY_LICENSES.md)
[![Marketing Log](https://img.shields.io/badge/marketing%20log-active-blueviolet.svg)](MARKETING-LOG.txt)
[![LLM Ready](https://img.shields.io/badge/llms.txt-ready-purple.svg)](llms.txt)
[![Ecosystem](https://img.shields.io/badge/ecosystem-ellmos--ai-blue.svg)](https://github.com/ellmos-ai)
[![Umbrella](https://img.shields.io/badge/umbrella-open--bricks-orange.svg)](https://github.com/open-bricks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Attribution](https://img.shields.io/badge/attribution-NOTICE-blue.svg)](NOTICE)

> Human-readable GUI demonstration recordings for CLI and autonomous AI agent workflows.

> [!NOTE]
> **AI / LLM Integration**: For machine-readable context, LLM search queries, and architecture notes, see [`llms.txt`](./llms.txt).

> [!NOTE]
> **LLM & Agent-Native Design**: `clirec` format is optimized for AI agents. Plain text inputs are sanitized by default into parameterized placeholders (`${input_1}`) to preserve privacy during recording and replay.

---

## Quick Navigation

1. [Overview](#1-overview)
2. [Key Capabilities](#2-key-capabilities)
3. [Target Personas & Discoverability](#3-target-personas--discoverability)
4. [Comparative Matrix vs. Alternatives](#4-comparative-matrix-vs-alternatives)
5. [Governance & Runtime Invariants](#5-governance--runtime-invariants)
6. [Architecture & Replay Flow](#6-architecture--replay-flow)
7. [Format v2 & SHA-256 Media Sidecars](#7-format-v2--sha-256-media-sidecars)
8. [Audio Privacy & Consent Boundary](#8-audio-privacy--consent-boundary)
9. [CLI Workflow & Quickstart](#9-cli-workflow--quickstart)
10. [Python API & Executor Protocol](#10-python-api--executor-protocol)
11. [Windows Desktop & Agent Environments](#11-windows-desktop--agent-environments)
12. [Installation & Optional Extras](#12-installation--optional-extras)
13. [Test Suite & Verification Gates](#13-test-suite--verification-gates)
14. [Ecosystem & Related Projects](#14-ecosystem--related-projects)
15. [Third-Party Licenses & Transparency](#15-third-party-licenses--transparency)
16. [Security & Vulnerability Reporting](#16-security--vulnerability-reporting)
17. [Directory Listings & AI Discoverability](#17-directory-listings--ai-discoverability)
18. [License & Maintainers](#18-license--maintainers)

---

<a id="1-overview"></a>
<a id="overview"></a>
## 1. Overview

`clirec` records mouse and keyboard demonstrations as human-readable `.clirec` files and replays them through an injected executor. It is built for autonomous AI agents, computer-use frameworks, and CLI workflows where a short, reproducible demonstration is dramatically more reliable and token-efficient than a long verbal prompt or multi-gigabyte video file.

The software operates on an uncompromising local-first architectural principle: every recording step, parameterization map, media sidecar, and transcript is stored exclusively on your local filesystem. Zero telemetry is collected, zero external servers are queried, and no demonstration data ever leaves your device without explicit user intent.

---

<a id="2-key-capabilities"></a>
<a id="key-capabilities"></a>
## 2. Key Capabilities

| Capability | Description |
|---|---|
| **Human-Readable Specification** | Demonstrations stored as transparent, diffable, git-friendly `.clirec` plaintext files. |
| **Default Input Sanitization** | Sensitive typed keystrokes are automatically converted into parameter placeholders (`${input_1}`). |
| **Injected Executor Replay** | Replay is backend-neutral and decoupled from capture mechanics (e.g. via `open-compute` `oc rec replay`). |
| **Format v2 Media Sidecars** | Relative SHA-256-verified `.clirec.media/` storage with atomic commit markers and zero orphan files. |
| **Strict Audio Consent Boundary** | Synchronous streaming microphone capture requires explicit dual opt-in (`--audio` and `--audio-consent`). |
| **Decoupled STT Adapter** | Caller-provided transcription adapter (`--module`) enforcing `persist=False` to eliminate secondary transcript leaks. |
| **Episode & Skill Export** | Standardized JSON export format for downstream learning workflows (`skill-extractor`, `workflow-extract`). |
| **Zero Mandatory Dependencies** | Core package runs on pure Python standard library + Windows ctypes; optional extras are cleanly isolated. |
| **Unprivileged Execution** | Executes completely in user space (`RunAsInvoker`) without requiring administrator elevation or UAC prompts. |

---

<a id="3-target-personas--discoverability"></a>
<a id="target-personas--discoverability"></a>
## 3. Target Personas & Discoverability

`clirec` is engineered to solve demonstration and automation challenges for four core personas across the AI and developer ecosystems:

| Persona ID | Target Audience | Primary Need | Key clirec Architectural Solution |
|---|---|---|---|
| `[PERSONA-01]` | **Autonomous AI Agent Engineers & Computer-Use Developers** | Deterministic, token-efficient GUI demonstration traces for training, evaluation, and headless replay without vision-token overhead. | Human-readable `.clirec` step format, automatic parameter sanitization (`${input_1}`), injected executor replay protocol, and JSON episode export for `skill-extractor`. |
| `[PERSONA-02]` | **CLI & Workflow Automation Builders (Sysadmins / DevOps)** | Turn repetitive interactive desktop operations into scriptable CLI commands with parameter injection. | Zero-dependency core CLI (`clirec start`, `clirec replay --param key=val`), headless schema validation (`clirec validate`), and tight `open-compute` integration (`oc rec replay`). |
| `[PERSONA-03]` | **QA, Test Automation & E2E Validation Engineers** | Verifiable, reproducible test demonstration runs that can be checked into Git without binary blob bloat or fragile UI selector breakage. | Git-friendly text spec, optional Windows UI Automation metadata probing (`[uia]`), cryptographic SHA-256 sidecar verification, and cross-platform capture. |
| `[PERSONA-04]` | **Privacy-Conscious Teams & Enterprise Compliance Officers** | Record workflow demonstrations and user tutorials without leaking credentials, passwords, PII, or bystander speech. | Strict default text parameterization, zero cloud telemetry, explicit dual-opt-in audio consent boundary (`--audio` + `--audio-consent`, § 201 StGB), separate audio/transcript purge, and unprivileged `RunAsInvoker` execution. |

### High-Intent Search Queries

To facilitate discoverability across developer directories, package managers, and search engines:
- `human-readable GUI demonstration recording CLI agent workflow` — Open-source local-first demonstration capture.
- `local-first computer-use replay without video vision tokens` — Compact action traces for multi-modal and headless agents.
- `parameterized keystroke replay for AI agents open-compute` — Safe input templating for credential-safe replays.
- `privacy-preserving desktop interaction recorder with text sanitization` — Desktop recorder masking keystrokes by default.
- `reproducible mouse keyboard action trace .clirec format v2` — Cryptographically verified demonstration sidecars.
- `agent-native demonstration channel with SHA-256 media sidecars` — Atomic commit markers and independent media purge.
- `opt-in microphone commentary recording with explicit consent boundary` — Dual-flag consent compliant with § 201 StGB.
- `zero-dependency Windows desktop capture ctypes WH_MOUSE_LL WH_KEYBOARD_LL` — Unprivileged user-mode WinAPI hooks.

---

<a id="4-comparative-matrix-vs-alternatives"></a>
<a id="comparative-matrix-vs-alternatives"></a>
## 4. Comparative Matrix vs. Alternatives

The following matrix compares `clirec` against existing recording and automation solutions across 10 technical dimensions directly mapped to our governance invariants:

| Technical Dimension | Governance Invariant | clirec | Video Recorders (OBS / Loom) | Web E2E (Playwright / Cypress) | Macro Recorders (AutoHotkey / TinyTask) | Enterprise RPA (UiPath / Automation Anywhere) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. Offline-First & Zero Egress** | `INV-LOCAL-01` | **100% Offline (Local disk, zero telemetry)** | High (Local OBS) / Low (Cloud Loom) | High (Local test runners) | High (Local execution) | Low (Mandatory cloud telemetry & licensing) |
| **2. Default Input Sanitization** | `INV-PRIVACY-02` | **Default Masking (`${input_1}`)** | None (Plain video captures all secrets) | None (Stores raw selectors/inputs) | None (Raw plaintext keystrokes recorded) | Partial (Configurable credential vaults) |
| **3. Human-Readable Spec** | `INV-INSPECT-03` | **Yes (`.clirec` plaintext spec)** | None (Opaque multi-GB binary video) | High (Generated JS/TS scripts) | Partial (Complex or binary script files) | Low (Proprietary workflows / XML blobs) |
| **4. Injected Agent Replay** | `INV-REPLAY-04` | **Native Injected Executor Protocol** | None (Video cannot be executed) | Web DOM Only (No native desktop/CLI) | Brittle (Fixed screen pixel coordinates) | Heavy (Requires dedicated desktop runtime) |
| **5. Audio Consent Boundary** | `INV-AUDIO-05` | **Dual Opt-In (`--audio` + `--audio-consent`)** | Uncontrolled (Bystander audio captured) | None (Audio recording not supported) | None (No audio integration) | Proprietary (Audio capture behind enterprise add-ons) |
| **6. Atomic Media Sidecars** | `INV-SIDECAR-06` | **Format v2 SHA-256 + Atomic Commit** | Single monolithic media file | None (Video/audio artifacts loose) | None (No media sidecar integrity) | Cloud-managed blob stores |
| **7. Decoupled STT Adapter** | `INV-ADAPTER-07` | **Plug-and-Play (`persist=False`)** | Cloud transcription service | None | None | Cloud AI service |
| **8. Unprivileged Execution** | `INV-UNPRIV-08` | **Strict RunAsInvoker (Zero root/admin)** | User-level | User-level | User-level (some hooks need admin) | Often requires admin service daemons |
| **9. Zero Mandatory Dependencies** | `INV-PORTABLE-09` | **Pure Python Stdlib + OS ctypes** | Heavy native binary installations | Large Node.js / browser downloads | Native executable | Heavy enterprise software suites |
| **10. Security SLA & CI Matrix** | `INV-SLA-10` | **48h SLA / Multi-OS CI Matrix** | Community / Commercial SLA | Large corporate maintenance | Community / Inactive | Commercial enterprise SLA |

---

<a id="5-governance--runtime-invariants"></a>
<a id="governance--runtime-invariants"></a>
## 5. Governance & Runtime Invariants

`clirec` is architected and maintained according to ten foundational governance and runtime invariants:

- **`INV-LOCAL-01` (100% Offline & Local-First Zero-Egress):** All recordings, media sidecars, logs, and transcripts reside solely on the local filesystem. Zero telemetry, zero analytics, zero external network requests.
- **`INV-PRIVACY-02` (Default Parameter Sanitization & Text Masking):** Typed keyboard text is parameterized by default into `${input_N}` placeholders to prevent credentials, secrets, or personal identifiable information from persisting into demonstration files.
- **`INV-INSPECT-03` (Human-Readable Plaintext Spec):** Demonstrations are recorded into transparent, versionable, and git-diffable `.clirec` files inspectable by human operators and AI agents without binary parsers.
- **`INV-REPLAY-04` (Agent & CLI Native Replay via Injected Executor):** Replay execution is backend-neutral and requires an explicit injected executor (such as `open-compute`), cleanly decoupling recorded intent from actuation mechanics.
- **`INV-AUDIO-05` (Strict Dual-Opt-In Audio Consent Boundary):** Microphone capture is off by default and strictly requires simultaneous `--audio` and `--audio-consent` flags; audio capture halts during pause and never runs as a background service (§ 201 StGB compliance).
- **`INV-SIDECAR-06` (Format v2 Atomic Media Sidecars with SHA-256):** Media sidecars are stored with cryptographic SHA-256 hashes in relative `.clirec.media/` directories; atomic commit markers guarantee no corrupted recordings; audio and transcripts support independent purge.
- **`INV-ADAPTER-07` (Decoupled STT Adapter Architecture):** Speech-to-text integration uses an unbundled, caller-provided adapter with mandatory `persist=False` to prevent secondary secret transcript stores; no proprietary or unverified speech models are bundled.
- **`INV-UNPRIV-08` (Unprivileged User-Mode Operation — `RunAsInvoker`):** The application runs with standard user-level permissions, never requiring administrative elevation, UAC prompts, or root access.
- **`INV-PORTABLE-09` (Zero Mandatory Runtime Dependencies):** Core package executes on pure Python standard library and OS ctypes; all external features are isolated behind explicit optional extras (`record`, `audio`, `uia`).
- **`INV-SLA-10` (Transparent Open-Source Governance & 48h Security SLA):** Permissive MIT core license, transparent third-party disclosures, automated GitHub Actions CI matrices, and a committed 48-hour response SLA for reported security issues.

---

<a id="6-architecture--replay-flow"></a>
<a id="architecture--replay-flow"></a>
## 6. Architecture & Replay Flow

```mermaid
graph TD
    User(["User / Agent"]) -->|"clirec start"| Recorder["Recording Engine"]
    Recorder -->|"Capture Mouse & Keys"| Param["Parameter Sanitizer"]
    Param -->|"Human-Readable Format"| Spec[".clirec File Format"]
    Spec -->|"clirec validate"| Val["Format Validator"]
    Spec -->|"clirec replay"| Executor["Injected Executor / open-compute"]
    Executor -->|"Automated Actions"| TargetApp["Target GUI / Terminal"]
```

The core package has no mandatory runtime dependencies. Windows capture uses a ctypes backend by default; cross-platform capture is available with the optional `record` extra (`pynput`). Windows UI Automation metadata is an optional `uia` extra (`uiautomation`). Microphone capture is off by default and available through the optional `audio` extra (`sounddevice` + PortAudio). It requires both `--audio` and `--audio-consent`.

---

<a id="7-format-v2--sha-256-media-sidecars"></a>
<a id="format-v2--sha-256-media-sidecars"></a>
## 7. Format v2 & SHA-256 Media Sidecars

Format v2 introduces robust atomic media sidecars:
- Media files (audio, transcripts) are placed inside a sibling folder named `<recording>.clirec.media/`.
- Every media asset is cryptographically verified against SHA-256 hashes recorded inside the `.clirec` manifest.
- Publication is atomic: media sidecars and temporary buffers are assembled first, and the `.clirec` commit file is written last.
- If an interruption or crash occurs during recording, `clirec recover recordings` automatically cleans up uncommitted orphan sidecars without affecting valid recordings.
- Complete backward compatibility: legacy Format v1 recordings remain fully readable and replayable.

---

<a id="8-audio-privacy--consent-boundary"></a>
<a id="audio-privacy--consent-boundary"></a>
## 8. Audio Privacy & Consent Boundary

Audio is treated as a distinct, sensitive privacy boundary:
- **Explicit Dual Opt-In:** Microphone capture never starts without passing both `--audio` and `--audio-consent` flags simultaneously.
- **No Background Recording:** Audio is never captured during pause states, after session completion, or by background daemons.
- **Independent Purge:** Operators can selectively strip audio or transcripts at any time without compromising the underlying GUI action trace:
  ```bash
  clirec purge-audio recordings/narrated-flow.clirec
  clirec purge-transcript recordings/narrated-flow.clirec
  ```
- **Legal Compliance:** In many jurisdictions (such as Germany under § 201 StGB), recording other individuals' speech without authorization is a criminal offense. The `--audio-consent` flag affirms the operator's personal consent and must never substitute for bystander agreement.

---

<a id="9-cli-workflow--quickstart"></a>
<a id="cli-workflow--quickstart"></a>
## 9. CLI Workflow & Quickstart

```bash
# Record an interactive demonstration (text masked by default)
clirec start login-flow

# Record a narrated demonstration with audio commentary
clirec start narrated-flow --audio --audio-consent

# Validate recording integrity and schema compliance
clirec validate recordings/login-flow.clirec

# List all available recordings in directory
clirec list --dir recordings

# Replay demonstration with parameterized values
clirec replay recordings/login-flow.clirec --param input_1=secret_value

# Inspect audio devices and purge sidecars
clirec audio-devices
clirec purge-audio recordings/narrated-flow.clirec
clirec purge-transcript recordings/narrated-flow.clirec
clirec recover recordings
```

---

<a id="10-python-api--executor-protocol"></a>
<a id="python-api--executor-protocol"></a>
## 10. Python API & Executor Protocol

Replay is backend-neutral. Use it directly from Python with any executor adhering to the protocol:

```python
from clirec.format import read
from clirec.replay import replay

# Load and validate demonstration
recording = read("recordings/login-flow.clirec")

# Execute via injected executor (e.g. open-compute or custom actuator)
report = replay(recording, executor, params={"input_1": "test-user"})
print(f"Replay completed: {report.successful_steps}/{report.total_steps} steps succeeded")
```

The `executor` must implement `width`, `height`, and `execute(action)`.

---

<a id="11-windows-desktop--agent-environments"></a>
<a id="windows-desktop--agent-environments"></a>
## 11. Windows Desktop & Agent Environments

When recording demonstrations on Windows:
- **Interactive Terminal:** `clirec` hooks into the active user session directly via low-level WinAPI hooks (`WH_MOUSE_LL`, `WH_KEYBOARD_LL`).
- **Agent & Daemon Environments:** When launched from background processes, agent subshells, or sandboxed environments (such as Antigravity, Claude Code, or services), the WinAPI capture thread automatically attaches to the interactive user desktop station (`WinSta0\Default`) to ensure mouse clicks and keystrokes on the real desktop are captured without missing events.

---

<a id="12-installation--optional-extras"></a>
<a id="installation--optional-extras"></a>
## 12. Installation & Optional Extras

Install directly from the Git repository:

```bash
# Core package (pure Python stdlib + ctypes, zero dependencies)
pip install git+https://github.com/ellmos-ai/clirec.git

# Optional extras
pip install "clirec[record] @ git+https://github.com/ellmos-ai/clirec.git"  # pynput cross-platform backend
pip install "clirec[uia] @ git+https://github.com/ellmos-ai/clirec.git"     # Windows UI Automation metadata
pip install "clirec[audio] @ git+https://github.com/ellmos-ai/clirec.git"   # sounddevice microphone capture
pip install "clirec[all] @ git+https://github.com/ellmos-ai/clirec.git"     # All extras combined
```

---

<a id="13-test-suite--verification-gates"></a>
<a id="test-suite--verification-gates"></a>
## 13. Test Suite & Verification Gates

```bash
# Run pytest test suite
python -m pytest -ra -v

# Run code style and linter checks
python -m ruff check clirec tests

# Verify Python bytecode compilation
python -m compileall -q clirec tests
```

See [RELEASE_GATE.md](RELEASE_GATE.md) for package and platform verification boundaries.

---

<a id="14-ecosystem--related-projects"></a>
<a id="ecosystem--related-projects"></a>
## 14. Ecosystem & Related Projects

`clirec` focuses exclusively on recording, parameterizing, and describing demonstrations. Replay actuation and ecosystem integrations are provided by sibling projects:

| Project | Role in the Ecosystem |
|---|---|
| [open-compute](https://github.com/ellmos-ai/open-compute) | Supplies the physical execution engine that actuates mouse movements and keypresses (`oc rec replay`). |
| [open-compute-mcp](https://github.com/ellmos-ai/open-compute-mcp) | Exposes demonstration replay as the MCP tool `rec_replay`, enabling AI agents to run demonstrations without shell access. |
| [ellmos-voice-io](https://github.com/ellmos-ai/ellmos-voice-io) | Local-first STT/TTS primitives suitable as a `--module` backend for `clirec transcribe`. |
| [ellmos](https://github.com/ellmos-ai/ellmos) | The central architectural ecosystem hub coordinating AI agents and desktop automation modules. |
| [open-bricks](https://github.com/open-bricks) | Umbrella organisation for modular, local-first software engineering bricks. |

---

<a id="15-third-party-licenses--transparency"></a>
<a id="third-party-licenses--transparency"></a>
## 15. Third-Party Licenses & Transparency

The core `clirec` package is licensed under the permissive [MIT License](LICENSE) with **zero mandatory external runtime dependencies**.

Optional extras pull in external open-source packages:
- `pynput` is licensed under **LGPL-3.0** and linked dynamically in full compliance with **LGPLv3 Section 4**.
- `sounddevice` and PortAudio are licensed under **MIT**.
- `uiautomation` is licensed under **Apache-2.0**.

For detailed SPDX audits, runtime matrices, and licensing notices, refer to [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

<a id="16-security--vulnerability-reporting"></a>
<a id="security--vulnerability-reporting"></a>
## 16. Security & Vulnerability Reporting

- **Policy:** For sensitive reports, use GitHub Private Vulnerability Reporting or open a private issue without attaching sensitive recording traces.
- **SLA Commitment:** 48-hour response SLA and 5-day triage commitment (`INV-SLA-10`).
- **Security Model:** Strict user-mode execution under `RunAsInvoker` (`INV-UNPRIV-08`).
- Full details: [SECURITY.md](SECURITY.md).

---

<a id="17-directory-listings--ai-discoverability"></a>
<a id="directory-listings--ai-discoverability"></a>
## 17. Directory Listings & AI Discoverability

`clirec` is indexed across developer directories and LLM registries:
- **LLM Context:** Machine-readable knowledge file available at [`llms.txt`](llms.txt).
- **Tooling Registries:** Glama, mcp.so, LobeHub, Smithery, awesome-mcp-servers.
- **Marketing Audit:** Tracked in [MARKETING-LOG.txt](MARKETING-LOG.txt).

---

<a id="18-license--maintainers"></a>
<a id="license--maintainers"></a>
## 18. License & Maintainers

- **License:** MIT License, see [LICENSE](LICENSE).
- **Attribution & Notice:** See [NOTICE](NOTICE) for canonical copyright and attribution notices.
- **Maintainers:** The `ellmos-ai` authors & community contributors.
- **Umbrella:** Part of the [open-bricks](https://github.com/open-bricks) open-source software family.
- **Statutory Disclaimer (§ 521 BGB):** This open-source software and documentation are provided free of charge. In accordance with Section 521 of the German Civil Code (BGB), the provider's liability for gratuitous provision is limited to intent and gross negligence.
