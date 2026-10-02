# Release Gate

## Stand

- Quellversion: `0.3.0`; im GitHub-API-Abruf vom 2026-10-02 wurde kein Release und kein Tag gefunden.
- Historische Nachweise: Tests und Lint wurden am 2026-08-20 unter Windows 11 / Python 3.12 ausgeführt; Suite und Lint wurden am 2026-09-03 erneut gezählt. Diese Daten bezeichnen historische Läufe.
- Repository: `https://github.com/ellmos-ai/clirec`
- Distributionsstand (API-Abruf 2026-10-02): Die GitHub-[Releases-API](https://api.github.com/repos/ellmos-ai/clirec/releases) und die [Tag-Refs-API](https://api.github.com/repos/ellmos-ai/clirec/git/matching-refs/tags/) lieferten leere Ergebnisse. Der aktuelle Status auf PyPI konnte in dieser Prüfung nicht bestätigt werden, weil der direkte Zugriff auf den [PyPI-JSON-Endpunkt](https://pypi.org/pypi/clirec/json) nicht verfügbar war. Ein dort am 2026-09-03 dokumentierter HTTP-404 ist nur ein historischer Befund und belegt weder den heutigen Veröffentlichungs- noch Reservierungsstatus. Die README beschreibt die Installation aus dem Git-Repository.

## Historisch verifizierte Gates

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
| Audio-/Format-v2-Suite | grün/synthetisch | 119 Tests unter Windows, 118 + 1 Skip sonst (2026-08-20: 113); deterministische PCM-Daten, kein echtes Audio |
| Privacy/Sidecars | grün/synthetisch | Consent, Hash, Traversal, Orphans, Purge, Retention, Recovery |
| Episoden-/Reviewexport | grün/synthetisch | Skill-/Workflow-Routing, Outcome-, Dedup- und Review-Gates |

## Sicherheitsgrenze

- Der sichere Standard speichert Tastatureingaben nur als `${input_N}`-Parameter.
- `--allow-unmasked-input` ist eine ausdrückliche Klartextfreigabe für die ganze
  Sitzung; solche Aufnahmen müssen vor Weitergabe geprüft werden.
- Replay bleibt backend-neutral und benötigt einen expliziten Executor.
- Frame-Belege entstehen nur bei injiziertem Frame-Grabber und werden beim
  Speichern vollständig gegen die Referenzen geprüft.
- Mikrofonaufnahme ist standardmäßig aus und braucht eine getrennte sichtbare
  Freigabe. Audio und Transkript sind getrennt löschbar und werden nicht
  automatisch geteilt oder abgespielt.

## Noch nicht live verifiziert

- physischer Capture-Smoke auf macOS/Linux mit dem optionalen `pynput`-Backend,
- Windows-IME-Capture mit einem tatsächlich installierten und aktivierten IME,
- echter Multi-Monitor-Mixed-DPI-Aufbau.
- reale Windows-Mikrofonaufnahme einschließlich Pause/Resume, Synchronität,
  Geräteverlust, Neustart-Readback und manuellem Privacy-Review,
- reale Mikrofon-Smokes auf macOS und Linux.

Diese Punkte blockieren den geprüften Alpha-Quellstand nicht, bleiben aber vor
einer breiteren Plattform- oder Integrationsfreigabe offen.

Der synthetische Audio-/Formatnachweis steht unter
[`docs/verification/2026-08-20-audio-synthetic.md`](docs/verification/2026-08-20-audio-synthetic.md).

## Live-Nachweis 2026-07-28

Der reale Windows-Lauf und die Umgebungsgrenzen sind unter
[`docs/verification/2026-07-28-windows-e2e.md`](docs/verification/2026-07-28-windows-e2e.md)
protokolliert. Der aktuelle RDP-Host stellt nur einen Monitor mit 1920×1080 bei
96 DPI und ausschließlich das deutsche Tastaturlayout bereit. IME und
Multi-Monitor-Mixed-DPI bleiben deshalb ausdrücklich offen.
