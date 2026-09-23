# Third-Party Licenses & Transparency Notice

> **Project:** `ellmos-ai/clirec` (CLIRec — Demonstration Recordings for CLI & Agent Workflows)<br>
> **Audited:** 2026-09-23 (Pfad A Re-Audit)<br>
> **Repository License:** [MIT License](LICENSE) | [Attribution Notice](NOTICE)<br>
> **Architecture & Privacy:** 100% Local-First, Zero-Egress by default, Unprivileged User-Mode (`RunAsInvoker`)

---

## Executive Summary & Compliance Assurance

`clirec` is a local-first Python library and CLI tool for recording mouse and keyboard demonstrations into human-readable `.clirec` files and replaying them via an injected executor. The core software is licensed under the permissive [MIT License](LICENSE) and canonical attribution is provided in [NOTICE](NOTICE).

The core runtime package has **no mandatory external runtime dependencies**; on Windows, keyboard and mouse hooks utilize Python standard library `ctypes` bindings directly against Windows subsystem APIs (`user32.dll`), operating entirely unprivileged in user space.

All optional extras and development dependencies are distributed under well-established open-source licenses (MIT, Apache-2.0, PSFL-2.0, LGPL-3.0):

- **Zero Mandatory External Dependencies:** A standard installation requires only Python 3.10+ and standard library modules (`ctypes`, `json`, `hashlib`, `pathlib`, `dataclasses`).
- **`pynput` (LGPL-3.0):** The optional `record` extra installs `pynput` for cross-platform capture. `pynput` is utilized exclusively via dynamic linking (standard PyPI distribution / unmodified library). In accordance with **LGPLv3 Section 4**, users retain full freedom to inspect, modify, and dynamically relink the library in their environments.
- **`sounddevice` (MIT) & PortAudio (MIT):** The optional `audio` extra enables streaming microphone capture with explicit dual opt-in (`--audio` and `--audio-consent`). It binds PortAudio under the permissive MIT license.
- **`uiautomation` (Apache-2.0):** The optional `uia` extra enables Windows UI Automation accessibility metadata probing under Apache-2.0.
- **Zero-Copyleft Contagion:** Recorded `.clirec` demonstration files, media sidecars (`.clirec.media/`), transcripts, and derived agent skill definitions remain 100% the property of the operator and are never subject to viral copyleft claims.
- **Zero-Egress & Unprivileged Execution:** `clirec` runs strictly as an unprivileged user process (`RunAsInvoker`), never requiring administrative elevation or root permissions, and performs zero telemetry or automated outbound network requests.

---

## Governance & Runtime Invariants

`clirec` affirms and implements ten core governance and runtime invariants:

1. **`INV-LOCAL-01` (100% Offline & Local-First Zero-Egress):** All recordings, media sidecars, logs, and transcripts reside solely on the local filesystem. Zero telemetry, zero analytics, zero external network requests.
2. **`INV-PRIVACY-02` (Default Parameter Sanitization & Text Masking):** Typed keyboard text is parameterized by default into `${input_N}` placeholders to prevent credentials, secrets, or PII from persisting into demonstration files.
3. **`INV-INSPECT-03` (Human-Readable Plaintext Spec):** Demonstrations are recorded into transparent, versionable, and git-diffable `.clirec` files inspectable by human operators and AI agents without binary parsers.
4. **`INV-REPLAY-04` (Agent & CLI Native Replay via Injected Executor):** Replay execution is backend-neutral and requires an explicit injected executor (such as `open-compute`), cleanly decoupling recorded intent from actuation mechanics.
5. **`INV-AUDIO-05` (Strict Dual-Opt-In Audio Consent Boundary):** Microphone capture is off by default and strictly requires simultaneous `--audio` and `--audio-consent` flags; audio capture halts during pause and never runs as a background service (§ 201 StGB compliance).
6. **`INV-SIDECAR-06` (Format v2 Atomic Media Sidecars with SHA-256):** Media sidecars are stored with cryptographic SHA-256 hashes in relative `.clirec.media/` directories; atomic commit markers guarantee no corrupted recordings; audio and transcripts support independent purge.
7. **`INV-ADAPTER-07` (Decoupled STT Adapter Architecture):** Speech-to-text integration uses an unbundled, caller-provided adapter with mandatory `persist=False` to prevent secondary secret transcript stores; no proprietary or unverified speech models are bundled.
8. **`INV-UNPRIV-08` (Unprivileged User-Mode Operation — `RunAsInvoker`):** The application runs with standard user-level permissions, never requiring administrative elevation, UAC prompts, or root access.
9. **`INV-PORTABLE-09` (Zero Mandatory Runtime Dependencies):** Core package executes on pure Python standard library and OS ctypes; all external features are isolated behind explicit optional extras (`record`, `audio`, `uia`).
10. **`INV-SLA-10` (Transparent Open-Source Governance & 48h Security SLA):** Permissive MIT core license, transparent third-party disclosures, automated GitHub Actions CI matrices, and a committed 48-hour response SLA for reported security issues.

---

## Runtime & Optional Extras Dependency Matrix

| Package / Extra | Version Range | Role / Functional Scope | License | Project Repository / Upstream | Compliance Mechanism |
|:---|:---|:---|:---|:---|:---|
| **Python Standard Library** | >=3.10 | Core engine, CLI, format parsing, ctypes hooks, SHA-256 validation | [PSFL-2.0](https://docs.python.org/3/license.html) | [python/cpython](https://github.com/python/cpython) | Built-in stdlib |
| **`pynput`** (`[record]`) | >=1.7.0 | Optional cross-platform keyboard and mouse input capture | [LGPL-3.0](https://www.gnu.org/licenses/lgpl-3.0.html) | [moses-palmer/pynput](https://github.com/moses-palmer/pynput) | Dynamic linking (LGPLv3 §4), unprivileged user-mode |
| **`sounddevice`** (`[audio]`) | >=0.5.0 | Optional streaming microphone audio capture via PortAudio | [MIT](https://github.com/spatialaudio/python-sounddevice/blob/master/LICENSE) | [spatialaudio/python-sounddevice](https://github.com/spatialaudio/python-sounddevice) | Permissive MIT, PortAudio C library bundled in wheel |
| **`uiautomation`** (`[uia]`) | >=2.0.0 | Optional Windows UI Automation accessibility element probing | [Apache-2.0](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows/blob/master/LICENSE) | [yinkaisheng/Python-UIAutomation-for-Windows](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows) | Permissive Apache-2.0 with redistribution notice |

---

## Development & Quality Assurance Tooling

| Package | Usage & Scope | License | Source / Upstream |
|:---|:---|:---|:---|
| **`pytest`** | Test runner, regression testing, repository contract test suites | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **`ruff`** | High-speed Python linter and code formatting enforcement | [MIT / Apache-2.0](https://github.com/astral-sh/ruff/blob/main/LICENSE-MIT) | [astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **`build`** | Standards-compliant PEP 517 build frontend | [MIT](https://github.com/pypa/build/blob/main/LICENSE) | [pypa/build](https://github.com/pypa/build) |
| **`twine`** | Package distribution checking and publishing utility | [Apache-2.0](https://github.com/pypa/twine/blob/main/LICENSE) | [pypa/twine](https://github.com/pypa/twine) |
| **`setuptools`** | Package build backend and distribution management | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) | [pypa/setuptools](https://github.com/pypa/setuptools) |

---

## LGPL Dynamic Linking Compliance Statement

`pynput` is distributed under the GNU Lesser General Public License Version 3 (LGPL-3.0). `clirec` complies with LGPLv3 Section 4:
1. `clirec` links dynamically to unmodified `pynput` shared modules distributed via PyPI.
2. Users and integrators are entitled to inspect, modify, and replace the `pynput` dependency in their Python environments.
3. No proprietary modifications to `pynput` are made or distributed.
4. Core `clirec` does not depend on `pynput`; on Windows, native `ctypes` hooks operate completely independently without `pynput`.

---

## Practical Deployment Guidelines

- **Standard `pip install` of `clirec`**: Zero third-party runtime dependencies installed. Pure MIT code with standard library ctypes.
- **Redistribution of Bundles / Containers**: When packaging environments including `clirec[record]`, include license notices for `pynput` and ensure shared library replacement remains feasible.
- **No Bundled STT Engine**: `clirec transcribe` invokes an external module specified by the operator (`--module` / `CLIREC_STT_MODULE`). Licensing terms of speech models and inference engines chosen by the operator remain outside this package.
- **Audio Consent Obligations**: In jurisdictions such as Germany (§ 201 StGB), recording speech without consent is a criminal offense. The `--audio-consent` flag represents the operator's consent and must be paired with mutual agreement from all participants.

---

## Full License Notices (Excerpts)

### 1. MIT License (MIT)
Used for `clirec`, `sounddevice`, `pytest`, `build`, and `setuptools`.
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### 2. GNU Lesser General Public License Version 3 (LGPL-3.0)
Applies to optional extra `pynput`. Full text: https://www.gnu.org/licenses/lgpl-3.0.html

### 3. Apache License Version 2.0 (Apache-2.0)
Applies to optional extra `uiautomation`, `twine`, and co-licensed `ruff`. Full text: https://www.apache.org/licenses/LICENSE-2.0

### 4. Python Software Foundation License Version 2 (PSFL-2.0)
Applies to Python standard library modules. Full text: https://docs.python.org/3/license.html
