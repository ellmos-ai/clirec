# Third-Party Licenses & Transparency Notice

> **Project:** `ellmos-ai/clirec` (CLIRec — Demonstration Recordings for CLI & Agent Workflows)<br>
> **Audited:** 2026-09-26 (Pfad B Re-Audit)<br>
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

## Level 1 SBOM & Governance Invariant Cross-Reference Matrix

`clirec` affirms, implements, and certifies ten core governance and runtime invariants:

| Invariant | Category | Description | Verification Method | Status |
|---|---|---|---|---|
| `INV-LOCAL-01` | Local-First & Zero-Egress | 100% offline-ready; recordings, sidecars, and logs reside strictly on local disk with zero external network egress. | `tests/test_metadata.py` & `clirec/format.py` | VERIFIED |
| `INV-PRIVACY-02` | Default Input Sanitization | Keystrokes parameterized by default into `${input_N}` placeholders to protect credentials, secrets, and PII. | `tests/test_clirec_recorder.py` & `clirec/recorder.py` | VERIFIED |
| `INV-INSPECT-03` | Human-Readable Spec | Plaintext `.clirec` specification transparently diffable and auditable by humans and AI agents without binary parsers. | `tests/test_clirec_format.py` & `clirec/format.py` | VERIFIED |
| `INV-REPLAY-04` | Injected Agent Replay | Replay decoupled from capture; backend-neutral executor injection protocol (e.g. `open-compute`). | `tests/test_clirec_replay.py` & `clirec/replay.py` | VERIFIED |
| `INV-AUDIO-05` | Audio Consent Boundary | Strict dual opt-in (`--audio` + `--audio-consent`) compliant with § 201 StGB; no background or unconsented recording. | `tests/test_clirec_format_v2.py` & `clirec/audio.py` | VERIFIED |
| `INV-SIDECAR-06` | Atomic Media Sidecars | Format v2 relative `.clirec.media/` storage with SHA-256 verification and atomic commit markers; zero orphan files. | `tests/test_clirec_format_v2.py` & `clirec/format.py` | VERIFIED |
| `INV-ADAPTER-07` | Decoupled STT Adapter | Caller-provided transcription adapter enforcing `persist=False` to prevent secondary secret transcript stores. | `tests/test_clirec_transcription.py` & `clirec/transcribe.py` | VERIFIED |
| `INV-UNPRIV-08` | Unprivileged Execution | Strict `RunAsInvoker` user-mode execution; zero administrator, root elevation, or UAC prompts required. | `SECURITY.md` & `clirec/win_backend.py` | VERIFIED |
| `INV-PORTABLE-09` | Zero Mandatory Dependencies | Pure Python standard library + Windows ctypes; all external packages isolated behind explicit optional extras. | `pyproject.toml` & `tests/test_metadata.py` | VERIFIED |
| `INV-SLA-10` | Transparent SLA & CI Matrix | Permissive MIT license, formal `[NOTICE](NOTICE)` cross-reference, multi-OS CI matrix, and binding 48h Security SLA. | `SECURITY.md`, `README.md`, `.github/workflows/` | VERIFIED |

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
