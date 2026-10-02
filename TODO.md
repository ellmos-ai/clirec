# TODO

## STATUS

| Category | Status | Hinweis |
|---|---|---|
| Paketkern | entwickelt | Der Kern hat keine deklarierten Laufzeitabhängigkeiten; die vorhandenen Tests decken ausgewählte Format-, Recorder-, Replay-, Capture- und CLI-Pfade ab. |
| Release-Gate | historisch belegt | Datierte frühere Tests und Smokes stehen in `RELEASE_GATE.md`; die Tabelle ist keine aktuelle plattformweite Freigabe. |
| Datenschutz | begrenzte Schutzmechanismen dokumentiert | Der normale Recorder parameterisiert Tastatureingaben standardmäßig; Audioflags sind Betreiber-Opt-in und bestätigen keine Zustimmung anderer Personen. Fremde Module können eigene Speicherung oder Netzwerkzugriffe ausführen. |
| Integration | historisch beobachtet | Ein `open-compute`-Replay-Smoke vom 2026-07-28 ist in `RELEASE_GATE.md` dokumentiert; er belegt keine allgemeine Kompatibilität mit allen Versionen oder Executor-Backends. |
| Veröffentlichung | Status offen | Die GitHub-API lieferte am 2026-10-02 keine Releases oder Tags. Der aktuelle PyPI-Status konnte nicht bestätigt werden; siehe `RELEASE_GATE.md`. |
| Sprache | geprüft | Entwickler-CLI englisch; `SKILL.md` deutsch und in `llms.txt` so beschrieben. Kein App-i18n-Mechanismus; README-Fassungen EN/DE. Eine weitere CLI-Übersetzung ist derzeit nicht angezeigt; bei einer GUI für Endnutzer neu bewerten. |

## Nächste sinnvolle Schritte (Formalisiert)

### 1. open-compute Replay mit realem Executor als Integrations-Smoke durchführen
- **Imperativ:** Führe einen End-to-End-Replay-Smoke von `clirec`-Aufnahmen über `open-compute` (`oc rec`) mit einem produktiven Executor aus.
- **Quelle:** `[Quelle: TODO.md, RELEASE_GATE.md, BEFUNDE.md]`
- **Einstufung:** `effort=medium`, `scope=local`
- **Definition of Done:** Replay-Session von `open-compute` führt `clirec`-Instruktionen auf Ziel-GUI ohne Parameterverlust oder Timing-Fehler aus.
- **Prüfweg:** Integrationstest in `open-compute` mit `clirec`-Demodatei.
- **Abhängigkeiten:** `open-compute`-Integration.

### 2. Windows End-to-End Smoke für IME/Dead-Key und Multi-Monitor-Mixed-DPI durchführen
- **Imperativ:** Verifiziere das Verhalten des Windows-Recorders bei IME/Dead-Key-Eingaben und gemischten Multi-Monitor DPI-Skalierungen.
- **Quelle:** `[Quelle: RELEASE_GATE.md, BEFUNDE.md]`
- **Einstufung:** `effort=medium`, `scope=local`
- **Definition of Done:** Tastaturevents mit IME/Dead-Keys sowie Mauskoordinaten auf Multi-Monitor-Setups mit abweichender DPI-Skalierung werden korrekt aufgezeichnet und reproduziert.
- **Prüfweg:** `pytest tests/test_clirec_backends_smoke.py` für Backend-/Dead-Key-Smokes; IME und Mixed-DPI zusätzlich als manuellen Windows-Capture-Smoke prüfen.
- **Abhängigkeiten:** Multi-Monitor Windows-Setup mit DPI-Varianz.

### 3. Konzeption und Entscheidungsvorlage für globalen Pause-Hotkey / Daemon-Trigger erstellen (Erledigt)
- **Status:** Erledigt via `docs/PAUSE_HOTKEY_DAEMON_DECISION.md` und `clirec/capture/winapi.py` Hooks.
- **Quelle:** `[Quelle: TODO.md]`
- **Einstufung:** `effort=easy`, `scope=local`

### 4. Optionalen pynput-Record-Pfad auf macOS/Linux verifizieren
- **Imperativ:** Verifiziere das physische Mouse/Keyboard-Capture des optionalen `pynput`-Backends unter macOS und Linux.
- **Quelle:** `[Quelle: TODO.md, RELEASE_GATE.md, BEFUNDE.md]`
- **Einstufung:** `effort=special`, `scope=local`
- **Definition of Done:** `pynput`-Capture-Lauf auf macOS und Linux dokumentiert fehlerfrei ausgeführt.
- **Prüfweg:** `pytest tests/test_clirec_backends_smoke.py` für Backend-Smokes; den physischen Capture-Smoke auf macOS und Linux gesondert durchführen und dokumentieren.
- **Abhängigkeiten:** Externe Nicht-Windows-Testumgebung (macOS / Linux).

## Historische Befunde vom 2026-09-03: nachgeprüfter Stand 2026-10-02

- [ ] **Release-Tag-Entscheidung:** Im GitHub-API-Abruf vom 2026-10-02 wurden keine Releases oder Tags gefunden. Ob und wann ein Tag oder eine Distribution erstellt wird, bleibt eine gesonderte Freigabeentscheidung.
- [ ] **PyPI vor einer ersten Veröffentlichung erneut prüfen:** Der aktuelle PyPI-Status war in dieser Prüfung nicht verfügbar. Der am 2026-09-03 beobachtete HTTP-404 ist nur historisch und belegt nicht, dass der Name heute frei oder vergeben ist. Siehe `RELEASE_GATE.md`.
- [ ] **Datenschutz je Einsatzkontext prüfen:** Bildschirm-, Eingabe- und optionale Audioaufnahmen können personenbezogene oder urheberrechtlich geschützte Inhalte erfassen. Zweck, Rechtsgrundlage, Transparenz, Umfang, Aufbewahrung und Weitergabe müssen für den konkreten Einsatz geprüft werden; dieses TODO ordnet keine pauschale Verantwortlichenrolle oder Haushaltsausnahme zu. Erste Orientierung: `docs/AUDIO_PRIVACY.md`.
- [x] **App-Sprachumfang geprüft:** Für die aktuelle Entwickler-CLI wurde kein App-i18n-Mechanismus gefunden; eine zusätzliche CLI-Übersetzung ist derzeit nicht angezeigt. README-Fassungen gibt es auf Englisch und Deutsch. Bei einer GUI für Endnutzer neu bewerten.
- [ ] **Organisationsprofil-Rubrik prüfen:** Der clirec-Verzeichniseintrag ist vorhanden, steht im Live-Read vom 2026-10-02 aber weiterhin unter `Evaluation, templates and maintenance`. Eine Korrektur betrifft `ellmos-ai/.github` und bleibt dort separat; dieser Lauf hat das Fremd-Repository nicht geändert. Der bestehende allgemeine Organisationsprofil-Auftrag wurde als mögliche Überschneidung berücksichtigt.

### Erledigt am 2026-09-03

- [x] CodeQL-Workflow: `init` und `analyze` liefen auseinander, jede
      Dependabot-Runde erzeugte zwei für sich nicht mergebare PRs.
- [x] `clirec transcribe` zeigte auf ein nirgends veröffentlichtes Standardmodul
      und transkribierte standardmäßig deutsch.
- [x] Ausgelieferte `skills/clirec/SKILL.md` beschrieb einen Stand vor 0.3.0;
      der zugehörige Test hielt genau diesen Stand fest.
- [x] Installationsanweisung `pip install clirec` löste nicht auf.
- [x] Lizenzstatus der optionalen Extras (`pynput`, LGPL-3.0) war nirgends genannt.
- [x] Interne Komponenten- und Ordnernamen in `SECURITY.md`, `docs/` und der
      Windows-Verifikationsnotiz.
- [x] Querverweise auf `open-compute`, `open-compute-mcp`, `ellmos-voice-io`
      und `ellmos` — die Verweise liefen bisher nur in eine Richtung.
