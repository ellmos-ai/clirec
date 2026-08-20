# TODO

## STATUS

| Category | Status | Hinweis |
|---|---|---|
| Paketkern | grün | Kernpaket ohne Laufzeitabhängigkeiten; Tests decken Format, Recorder, Replay, Capture und CLI ab. |
| Release-Gate | grün | Quell-, Paket-, Wheel-Installations- und CLI-Smokes sind in `RELEASE_GATE.md` dokumentiert. |
| Datenschutz | grün/beobachtet | Tastatureingaben werden parameterisiert; Audio ist getrenntes Opt-in mit Purge/Retention, reale Sitzungen erfordern Review. |
| Integration | beobachtet | `open-compute` lädt `clirec` lazy; echte Executor-Replay-Smokes bleiben integrationsseitig zu prüfen. |
| Veröffentlichung | offen | Paketveröffentlichung und Plattform-Smokes noch nicht dokumentiert abgeschlossen. |

## Nächste sinnvolle Schritte

- Optionalen `pynput`-Record-Pfad auf einer Nicht-Windows-Plattform prüfen.
- `open-compute`-Replay mit einem realen Executor als Integrations-Smoke nachziehen.
- Realen Windows-Mikrofon-Smoke mit Nutzerfreigabe durchführen: Pause/Resume,
  Synchronität, Geräteverlust, Neustart-Readback und Privacy-Review.
- Mikrofon-Smokes auf macOS und Linux getrennt nachholen; bis dahin keine
  plattformübergreifende Audiofreigabe behaupten.
