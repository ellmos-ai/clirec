# clirec

<img src="assets/banner.png" width="100%" alt="Clirec Banner">



[![clirec tests](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml)
[![Pytest Status](https://img.shields.io/badge/pytest-119%20passed-brightgreen.svg)](https://github.com/ellmos-ai/clirec)
[![CodeQL](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/ellmos-ai/clirec)
[![Ecosystem](https://img.shields.io/badge/ecosystem-ellmos--ai-blue.svg)](https://github.com/ellmos-ai)
[![Umbrella: open-bricks](https://img.shields.io/badge/umbrella-open--bricks-purple.svg)](https://github.com/open-bricks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Deutsch** | [English](README.md)

> [!NOTE]
> **KI / LLM Integration**: Maschinenlesbare Kontexte, LLM-Suchbegriffe und Architektur-Hinweise finden sich in [`llms.txt`](./llms.txt).

`clirec` speichert Maus-/Tastatur-Demonstrationen als menschenlesbare
`.clirec`-Dateien und spielt sie über einen injizierten Executor wieder ab.
Gedacht ist es für Agenten- und CLI-Workflows, bei denen ein kurzer Vormachpfad
zuverlässiger ist als eine lange verbale Beschreibung.

> [!NOTE]
> **LLM- & Agenten-Nativität**: Das `.clirec`-Format ist für KI-Agenten optimiert. Texteingaben werden standardmäßig in parametrisierte Platzhalter (`${input_1}`) umgewandelt, um den Datenschutz beim Teilen und Abspielen zu gewährleisten.

## Architektur & Replay-Ablauf

```mermaid
graph TD
    User(["Benutzer / Agent"]) -->|clirec start| Recorder["Recording Engine"]
    Recorder -->|Erfassung Maus & Tastatur| Param["Parameter Sanitizer"]
    Param -->|Menschenlesbares Format| Spec[".clirec Dateiformat"]
    Spec -->|clirec validate| Val["Format Validator"]
    Spec -->|clirec replay| Executor["Injizierter Executor / open-compute"]
    Executor -->|Automatische Aktionen| TargetApp["Ziel-GUI / Terminal"]
```

Der Kern hat keine zwingenden Laufzeitabhängigkeiten. Unter Windows gibt es standardmäßig
ein ctypes-Capture-Backend; plattformübergreifend kann optional `pynput`
installiert werden. Windows-UIA-Metadaten sind ein separates optionales Extra.
Die Mikrofonaufnahme ist standardmäßig aus und über das optionale Extra
`audio` verfügbar. Sie erfordert gemeinsam `--audio` und `--audio-consent`.

## Installation

`clirec` liegt **noch nicht auf PyPI** — `pip install clirec` löst nicht auf.
Installation direkt aus dem Repository:

```bash
pip install git+https://github.com/ellmos-ai/clirec.git
pip install "clirec[record] @ git+https://github.com/ellmos-ai/clirec.git"  # pynput-Backend
pip install "clirec[uia] @ git+https://github.com/ellmos-ai/clirec.git"     # Windows-UI-Metadaten
pip install "clirec[audio] @ git+https://github.com/ellmos-ai/clirec.git"   # sounddevice-Mikrofon
```

Nach einer Veröffentlichung stehen die Extras als `pip install clirec[record]`
usw. zur Verfügung. Die optionalen Extras ziehen Fremdabhängigkeiten mit eigenen
Lizenzen nach — `pynput` steht unter LGPL-3.0; vor einer Weitergabe
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) lesen.

## CLI

```bash
clirec start login-flow
clirec start kommentierter-ablauf --audio --audio-consent
clirec validate recordings/login-flow.clirec
clirec list --dir recordings
clirec replay recordings/login-flow.clirec --param input_1=Wert
```

Im sicheren Standard wird eingegebener Text nie im Klartext gespeichert. Jeder
Textabschnitt wird zu einem Parameter wie `${input_1}` und beim Replay mit
`--param input_1=Wert` befüllt. `--allow-unmasked-input` ist eine ausdrückliche
unsichere Freigabe; solche Aufnahmen müssen vor dem Teilen geprüft werden.

Audio ist eine getrennte, ausdrückliche Datenschutzgrenze. CLIRec zeichnet nie
vor der Freigabe, während einer Pause, nach dem Audio-Stopp oder über einen
versteckten Daemon auf. Format v2 speichert Audio und Transkripte als relative,
SHA-256-geprüfte `.clirec.media/`-Sidecars; v1-Aufnahmen bleiben lesbar. Audio
und Transkript lassen sich getrennt entfernen:

```bash
clirec audio-devices
clirec purge-audio recordings/kommentierter-ablauf.clirec
clirec purge-transcript recordings/kommentierter-ablauf.clirec
clirec recover recordings
```

Die Transkription ist ein Opt-in-Adapter zu einem externen STT-Modul. CLIRec
enthält keine eigene STT-Engine und liefert kein voreingestelltes Backend mit —
das Modul wird selbst benannt, per `--module NAME` oder `CLIREC_STT_MODULE`. Es
muss `transcribe_file(pfad, language=..., persist=False)` anbieten; das
verpflichtende `persist=False` verhindert, dass unbemerkt eine zweite
Transkript-Ablage entsteht. Die Sprache kommt aus `--lang` oder
`CLIREC_STT_LANGUAGE`, ohne beides gilt `en`.

Geprüfte Episoden und Extraktor-Aufträge können als JSON für `skill-extractor`
oder `workflow-extract` exportiert werden; dadurch wird weder ein Skill noch ein
Zeitplan automatisch aktiviert.

Details: [Format v2](docs/FORMAT_V2.md),
[Audio-Datenschutz](docs/AUDIO_PRIVACY.md) und
[Episoden-Reviewexport](docs/EPISODE_EXPORT.md).

Replay ist backend-neutral. Aus Python mit einem Executor-Objekt oder über eine
Integration wie `open-compute`:

```bash
oc rec replay recordings/login-flow.clirec
```

## Python

```python
from clirec.format import read
from clirec.replay import replay

recording = read("recordings/login-flow.clirec")
report = replay(recording, executor)
```

`executor` muss `width`, `height` und `execute(action)` bereitstellen.

## Tests

```bash
python -m pytest -q
python -m ruff check clirec tests
python -m ruff format --check clirec tests
python -m compileall -q clirec tests
```

Die aktuelle Paket- und Plattformgrenze steht in [RELEASE_GATE.md](RELEASE_GATE.md).

## Verwandte Projekte

`clirec` nimmt eine Demonstration nur auf und beschreibt sie. Das Ausführen, die
Bereitstellung für Agenten und die Umwandlung von Audio in Text passieren in
Nachbarprojekten:

| Projekt | Wozu es für `clirec` gebraucht wird |
|---|---|
| [open-compute](https://github.com/ellmos-ai/open-compute) | Liefert den Executor, der tatsächlich Maus und Tastatur bewegt, und kapselt das Replay als `oc rec replay`. Ohne Executor lässt sich eine Aufnahme gar nicht abspielen. |
| [open-compute-mcp](https://github.com/ellmos-ai/open-compute-mcp) | Stellt dieses Replay als MCP-Werkzeug `rec_replay` bereit, damit ein Agent eine Aufnahme ohne Shell starten kann. |
| [ellmos-voice-io](https://github.com/ellmos-ai/ellmos-voice-io) | Lokale Bausteine für Spracherkennung und Sprachausgabe — der Kandidat, den man umhüllt, wenn `clirec transcribe` ein `--module`-Backend braucht. |
| [ellmos](https://github.com/ellmos-ai/ellmos) | Der Ökosystem-Überblick: welches Modul welches Problem löst und wie sie zusammenspielen. |

## Lizenz

MIT, siehe [LICENSE](LICENSE). Optionale Extras haben eigene Lizenzen —
`pynput` steht unter LGPL-3.0; siehe
[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
