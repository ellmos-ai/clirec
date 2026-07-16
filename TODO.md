# TODO

## STATUS

| Category | Status | Hinweis |
|---|---|---|
| Paketkern | grün | Kernpaket ohne Laufzeitabhängigkeiten; Tests decken Format, Recorder, Replay, Capture und CLI ab. |
| Release-Gate | grün | Quell-, Paket-, Wheel-Installations- und CLI-Smokes sind in `RELEASE_GATE.md` dokumentiert. |
| Datenschutz | grün/beobachtet | Tastatureingaben werden standardmäßig vollständig parameterisiert; UI-Metadaten und explizit unmaskierte Sitzungen erfordern weiterhin Review. |
| Integration | beobachtet | `open-compute` lädt `clirec` lazy; echte Executor-Replay-Smokes bleiben integrationsseitig zu prüfen. |
| Veröffentlichung | offen | Paketveröffentlichung und Plattform-Smokes noch nicht dokumentiert abgeschlossen. |

## Nächste sinnvolle Schritte

- Optionalen `pynput`-Record-Pfad auf einer Nicht-Windows-Plattform prüfen.
- `open-compute`-Replay mit einem realen Executor als Integrations-Smoke nachziehen.
- Entscheiden, ob ein globaler Pause-Hotkey oder Daemon-Trigger vor dem nächsten Alpha-Tag umgesetzt wird.
