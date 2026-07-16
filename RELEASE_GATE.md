# Release Gate

## Stand

- Version: `0.2.0`
- geprüft: 2026-07-17 auf Windows 11 / Python 3.12
- Repository: `https://github.com/ellmos-ai/clirec`
- Veröffentlichung: Quell- und Wheel-Artefakte sind vorbereitet; ein PyPI-Upload
  oder Git-Tag ist nicht Teil dieses Gates.

## Verifizierte Gates

| Gate | Ergebnis | Nachweis |
|---|---|---|
| Quelltests | grün | `python -m pytest -q` |
| Lint/Format | grün | `python -m ruff check clirec tests`; `python -m ruff format --check clirec tests` |
| Bytecode | grün | `python -m compileall -q clirec tests` |
| Paketbau | grün | `python -m build` und `python -m twine check dist/*` |
| Wheel-Installation | grün | frische virtuelle Umgebung, `pip install <wheel>`, `pip check` |
| Installierte CLI | grün | `clirec --help`, `clirec validate`, `clirec list` |
| Windows Capture | grün | Per-Monitor-DPI, Hook-Start/Stop und Shift-Layout-Smoke |
| Externer Review | grün | keine verbleibenden konkreten P0/P1/P2; 87 Tests im Review-Snapshot |

## Sicherheitsgrenze

- Der sichere Standard speichert Tastatureingaben nur als `${input_N}`-Parameter.
- `--allow-unmasked-input` ist eine ausdrückliche Klartextfreigabe für die ganze
  Sitzung; solche Aufnahmen müssen vor Weitergabe geprüft werden.
- Replay bleibt backend-neutral und benötigt einen expliziten Executor.
- Frame-Belege entstehen nur bei injiziertem Frame-Grabber und werden beim
  Speichern vollständig gegen die Referenzen geprüft.

## Noch nicht live verifiziert

- physischer Capture-Smoke auf macOS/Linux mit dem optionalen `pynput`-Backend,
- vollständiger Windows-End-to-End-Lauf mit IME/Dead-Key-Eingabe und echtem
  Multi-Monitor-Mixed-DPI-Aufbau,
- realer `open-compute`-Executor gegen eine produktive GUI.

Diese Punkte blockieren den geprüften Alpha-Quellstand nicht, bleiben aber vor
einer breiteren Plattform- oder Integrationsfreigabe offen.
