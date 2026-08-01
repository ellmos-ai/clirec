# Release Gate

## Stand

- Version: `0.2.1`
- geprüft: 2026-08-01 auf Windows 11 / Python 3.12.10
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
| Windows Capture | grün/beobachtet | Per-Monitor-DPI, Hook-Start/Stop, Shift-Layout-Smoke und realer deutscher Dead-Key-Capture-/Replay-Smoke |
| `open-compute`-Integration | grün | realer `oc rec replay` gegen Notepad mit produktivem `LocalExecutor`, Parameter- und Unicode-Rückleseprüfung |
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
- Windows-IME-Capture mit einem tatsächlich installierten und aktivierten IME,
- echter Multi-Monitor-Mixed-DPI-Aufbau.

Diese Punkte blockieren den geprüften Alpha-Quellstand nicht, bleiben aber vor
einer breiteren Plattform- oder Integrationsfreigabe offen.

## Live-Nachweis 2026-07-28

Der reale Windows-Lauf und die Umgebungsgrenzen sind unter
[`docs/verification/2026-07-28-windows-e2e.md`](docs/verification/2026-07-28-windows-e2e.md)
protokolliert. Der aktuelle RDP-Host stellt nur einen Monitor mit 1920×1080 bei
96 DPI und ausschließlich das deutsche Tastaturlayout bereit. IME und
Multi-Monitor-Mixed-DPI bleiben deshalb ausdrücklich offen.
