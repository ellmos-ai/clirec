# Contributing to clirec

Thank you for your interest in contributing to clirec (ellmos-ai/clirec), a
Python CLI and library for human-readable GUI demonstrations.

[English](#implementation-notes) | [Deutsch](#hinweise-zur-implementierung-deutsch)

---

## Implementation notes

- The recorder core writes to the configured filesystem path and has no
  built-in telemetry. Caller-provided modules may use network services or
  additional storage.
- Typed keyboard text is parameterized by default. Review UI metadata, optional
  frames, and audio for sensitive information before sharing.
- Audio is off by default. The CLI flags record the operator's opt-in; clirec
  does not obtain or verify permission from other people.
- The `.clirec` manifest is published last, and readers validate referenced media
  hashes. Recovery removes orphan `.clirec.media` sidecars; optional
  `.clirec.frames` directories are not included.
- The selected STT module receives `persist=False`; this parameter does not
  enforce the module's storage or network behavior.
- clirec uses the permissions of the process that starts it and does not itself
  request elevation (unprivileged user-mode execution, RunAsInvoker).
- The core declares no mandatory runtime dependencies. Optional extras are
  listed in `pyproject.toml`.
- Initial-response and triage times in SECURITY.md are targets subject to
  maintainer availability, not guaranteed fix deadlines (48h security response SLA target).
- Statutory disclaimer: Under applicable German law (§ 521 BGB, gratuitous/courtesy
  software provision), liability for defects in title and quality is limited to intent
  and gross negligence.

The source version remains 0.3.0 during this maintenance cycle (frozen per T-20260920-167562623).

## Development setup (Plan D)

In accordance with Plan D development standards, development takes place in the
canonical local repository (`C:\_Local_DEV\repos\clirec`):

```bash
git clone https://github.com/ellmos-ai/clirec.git
cd clirec
python -m venv .venv
source .venv/bin/activate  # On PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[all,dev]"
pytest
ruff check .
```

## Pull request guidelines

- Base branches on current `main`.
- Add or update contract and regression tests for logic or bug fixes.
- Document user-visible changes in `CHANGELOG.md` under `## Unreleased`.
- Run `ruff check clirec tests`, `pytest`, `python -m compileall clirec tests`, and `git diff --check`.
- Keep changes minimal, documented, and tightly scoped.

---

## Hinweise zur Implementierung (Deutsch)

- Der Aufzeichnungskern schreibt ausschließlich in den konfigurierten Dateisystempfad
  und besitzt keine eingebaute Telemetrie. Aufrufende Module können Netzwerk oder
  zusätzlichen Speicher nutzen.
- Getippter Tastaturtext wird standardmäßig durch Platzhalter (`${input_N}`) parametrisiert.
  Prüfe UI-Metadaten, optionale Frames und Audio vor dem Teilen auf vertrauliche Inhalte.
- Audio ist standardmäßig inaktiv. Die CLI-Flags (`--audio`, `--audio-consent`) halten
  die Entscheidung des Operators fest; clirec holt keine Einwilligung Dritter ein.
- Das `.clirec`-Manifest wird zuletzt als atomarer Commit-Marker veröffentlicht, und Leser
  validieren referenzierte Medien über SHA-256-Hashes. `clirec recover` bereinigt verwaiste
  `.clirec.media`-Sidecars; optionale `.clirec.frames`-Verzeichnisse verbleiben unangetastet.
- Das ausgewählte Transkriptionsmodul erhält `persist=False`; clirec kann das Netzwerk-
  oder Speicherverhalten externer Module nicht erzwingen.
- clirec erbt die Berechtigungen des startenden Prozesses und fordert keine Privilegien-
  Eskalation an (unprivilegierter RunAsInvoker-Betrieb).
- Das Kernpaket deklariert keine zwingenden Laufzeitabhängigkeiten. Optionale Extras sind
  in `pyproject.toml` spezifiziert.
- Gesetzlicher Haftungshinweis: Gemäß § 521 BGB (Recht der unentgeltlichen Zuwendung /
  Gefälligkeit) ist die Haftung für Sach- und Rechtsmängel auf Vorsatz und grobe
  Fahrlässigkeit beschränkt.
- Sicherheitsmeldungen werden im Rahmen der personellen Kapazitäten innerhalb von 48 Stunden
  erstbeantwortet (SLA-Ziel gemäß SECURITY.md).

Die Quelltextversion bleibt während dieses Wartungszyklus auf 0.3.0 eingefroren.

## Lokale Entwicklungsumgebung (Plan D)

Die Entwicklung erfolgt im kanonischen lokalen Repository (`C:\_Local_DEV\repos\clirec`):

```powershell
git clone https://github.com/ellmos-ai/clirec.git
cd clirec
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[all,dev]"
pytest
ruff check .
```

## Pull-Request-Richtlinien

- Erstelle Feature-Branches stets auf Basis des aktuellen `main`.
- Ergänze Vertragstests (`tests/test_metadata.py`) und Regressionstests für alle Änderungen.
- Halte Änderungen in `CHANGELOG.md` unter `## Unreleased` fest.
- Führe `ruff check clirec tests`, `pytest`, `python -m compileall clirec tests` und `git diff --check` aus.
