# TODO

## STATUS

| Category | Status | Hinweis |
|---|---|---|
| Paketkern | grün | Kernpaket ohne Laufzeitabhängigkeiten; Tests decken Format, Recorder, Replay, Capture und CLI ab. |
| Release-Gate | grün | Final Gate Check ist nach Ergänzung der Mindest-Ignore-Regeln und dieses TODOs bestanden. |
| Datenschutz | beobachtet | Aufnahmen können sensible UI-Inhalte enthalten; Passwortfelder werden maskiert, aber Review vor Veröffentlichung bleibt Pflicht. |
| Integration | beobachtet | `open-compute` lädt `clirec` lazy; echte Executor-Replay-Smokes bleiben integrationsseitig zu prüfen. |
| Veröffentlichung | offen | Paketveröffentlichung und Plattform-Smokes noch nicht dokumentiert abgeschlossen. |

## Nächste sinnvolle Schritte

- Vor der ersten Paketveröffentlichung `python -m pip wheel . --no-deps --wheel-dir <temp>` und einen installierten `clirec --help`-Smoke dokumentieren.
- Optionalen `pynput`-Record-Pfad auf einer Nicht-Windows-Plattform prüfen.
- `open-compute`-Replay mit einem realen Executor als Integrations-Smoke nachziehen.
- Entscheiden, ob ein globaler Pause-Hotkey oder Daemon-Trigger vor dem nächsten Alpha-Tag umgesetzt wird.
