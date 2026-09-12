# Entscheidungsvorlage: globaler Pause-Hotkey und Daemon-Trigger

## Entscheidung

Den globalen Pause-Hotkey nicht als Sonderfall in den bestehenden
`clirec start`-Prozess einbauen. Stattdessen zuerst einen lokalen,
einzelinstanzigen Recorder-Daemon mit einer kleinen Steuer-Schnittstelle
einführen. Der Hotkey ist ein optionaler Adapter dieses Daemons:

- Windows: ein eigener WinAPI-Hotkey-Adapter auf Basis der bereits verwendeten
  Low-Level-Keyboard-Hooks.
- macOS/Linux: optionaler `pynput`-Adapter, nur wenn `clirec[record]`
  installiert ist und der jeweilige Host globale Eingaben erlaubt.
- Ohne verfügbaren Adapter bleibt der Daemon bedienbar; der Start darf nicht
  wegen eines nicht registrierbaren Hotkeys scheitern.

Priorität: zuerst Daemon- und Steuervertrag; danach Windows-Hotkey; anschließend
plattformübergreifender `pynput`-Hotkey. Ein öffentlich dokumentierter
Ringpuffer-Trigger folgt erst, wenn der Daemon stabil läuft.

## Ausgangslage

- `Recorder.set_paused(bool)` delegiert bereits an den Capture-Backend und
  beide vorhandenen Backends verwerfen während einer Pause neue Events.
- `Recorder.start()` setzt den Pause-Zustand einer neuen Sitzung zurück.
- `clirec start` besitzt dagegen nur einen Prozess-lokalen Loop; `clirec stop`
  und `clirec buffer` beenden mit "require a running daemon session".
- `pause_hotkey` steht bereits in `DEFAULT_CONFIG`, wird aber noch nicht an
  CLI, Backend oder einen Listener gebunden.
- Der sichere Standard (parametrisierte Tastatureingaben) bleibt unverändert;
  ein Hotkey darf keine Rohtexte speichern oder ausgeben.

## Ziel und Nicht-Ziele

Ziel ist ein sichtbarer, verlustfreier Wechsel zwischen `recording` und
`paused` für eine laufende Sitzung sowie ein lokaler Trigger für spätere
Ringpuffer-Schnitte.

Nicht Teil dieses Schritts:

- kein systemweiter Dienst beim Login, keine Netzwerkschnittstelle und keine
  Fernsteuerung;
- kein implizites Aktivieren des Ringpuffers (er bleibt standardmäßig aus);
- kein Versuch, reservierte System-Shortcuts zu überschreiben;
- keine Zusage, dass globale Hotkeys unter Wayland, macOS-TCC oder restriktiven
  Desktop-Sessions verfügbar sind.

## Vorgeschlagener API-Vertrag

Die Laufzeitlogik gehört in ein neues, backend-neutrales Modul, etwa
`clirec.daemon`. Die CLI und Hotkey-Adapter dürfen nicht direkt auf
`Recorder`-Interna zugreifen.

```python
class RecorderDaemon:
    def start(self, name: str) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def toggle_pause(self) -> bool: ...  # True bedeutet: jetzt pausiert
    def stop_and_save(self) -> str: ...
    def cut_last_and_save(self, minutes: float, name: str) -> str: ...
    def status(self) -> str: ...  # idle | recording | paused
```

`toggle_pause()` wird serialisiert ausgeführt: Erst wird der Backend-Pausezustand
gesetzt, dann wird der Status veröffentlicht. Beim Pausieren sind gehaltene
Modifier bereits in den Backends zu löschen; beim Fortsetzen werden nur neue
Events erfasst. `stop_and_save()` muss eine Pause akzeptieren, den Capture-Thread
beenden und exakt einmal speichern. Mehrfaches `start`, `stop` oder ein Trigger
nach dem Stop liefern einen klaren Zustandsfehler statt einer zweiten Aufnahme.

Der lokale Steuerkanal soll mit einem expliziten, versionierten Befehlssatz
arbeiten (`status`, `pause`, `resume`, `toggle`, `stop`, später `cut-last`).
Für den MVP genügt ein pro Benutzer erzeugter lokaler Endpunkt; kein TCP-Port.
Die konkrete IPC-Wahl (Windows Named Pipe bzw. Unix-Domain-Socket) wird bei der
Implementierung pro Betriebssystem getestet. Eine PID-/Endpoint-Datei muss nur
nach erfolgreichem Start veröffentlicht und beim Stop entfernt werden.

Vorgeschlagene CLI nach dem Daemon-MVP:

```text
clirec daemon start <name> [--hotkey ctrl+alt+p]
clirec daemon status
clirec daemon pause|resume|toggle|stop
clirec buffer cut-last <minutes> <name>
```

`clirec start` bleibt als blockierender, daemonfreier MVP-Pfad kompatibel.
`--hotkey` überschreibt nur für diesen Daemonlauf die Konfiguration; ein leerer
Wert deaktiviert den Adapter ausdrücklich.

## Hotkey-Optionen

| Option | Eignung | Vorteile | Grenzen | Entscheidung |
|---|---|---|---|---|
| `pynput.keyboard.HotKey`/Listener | optionaler Cross-Platform-Adapter | passt zur optionalen Dependency und den bestehenden Listenern | Berechtigungen/Wayland/macOS-TCC; nicht Standardinstallation | nach Daemon, best effort |
| Windows Low-Level-Hook | Windows-Standardadapter | keine zusätzliche Laufzeitdependency; Capture-Backend nutzt bereits `WH_KEYBOARD_LL` | Windows-spezifische Shortcut-Normalisierung und Kollisionen selbst pflegen | nach Daemon, priorisiert |
| separater globaler Service | derzeit ungeeignet | auch ohne sichtbares CLI steuerbar | Start, Rechte, Lifecycle und Sicherheitsfläche wachsen stark | nicht im MVP |

Der Windows-Adapter soll den bestehenden Keyboard-Hook erweitern oder einen
koordinierten Hook besitzen; zwei konkurrierende Hook-Lebenszyklen sind zu
vermeiden. Er erkennt ausschließlich die konfigurierte Modifier+Taste-Kombination
und ruft `toggle_pause()` auf. Das auslösende Shortcut darf nicht als
Recording-Event in der Aufnahme landen. Bei einem ungültigen oder nicht
registrierbaren Hotkey: klare Warnung, Daemon bleibt ohne Hotkey nutzbar.

## Implementierungsreihenfolge und Akzeptanzkriterien

1. `RecorderDaemon` mit Mock-Backend und Zustandsautomat implementieren.
   - Test: `recording -> paused -> recording -> idle`; keine Events während
     `paused`; `stop_and_save()` speichert aus beiden laufenden Zuständen.
2. Lokale CLI-/IPC-Steuerung implementieren.
   - Test: zweiter Daemon wird abgewiesen; `status`, `toggle` und `stop` ändern
     nur die adressierte Sitzung; verwaiste Endpoint-Datei wird nicht als
     laufende Sitzung akzeptiert.
3. Windows-Hotkey-Adapter hinzufügen.
   - Test: Adapter-Normalisierung mit simulierten Key-Events; Windows-Smoke:
     Hotkey pausiert/fortsetzt, der Hotkey selbst fehlt aus der `.clirec`.
4. Optionalen `pynput`-Adapter für macOS/Linux hinzufügen.
   - Test: Unit-Test ohne installierte Dependency; manuelle Plattform-Smokes
     dokumentieren Berechtigungs- und Wayland-Grenzen.
5. Erst danach `buffer cut-last` freigeben.
   - Test: Ringpuffer ist ohne explizite Aktivierung nicht verfügbar; ein
     Schnitt enthält nur das konfigurierte Zeitfenster und gültige Frames.

## Risiken und Stop-Regeln

- Ein globaler Hotkey ist keine plattformübergreifend garantierbare Fähigkeit.
  Wenn die OS-Sitzung oder Berechtigung den Listener verhindert, nur den Adapter
  deaktivieren; den Recorder-Daemon nicht künstlich als erfolgreich markieren.
- Pause darf nie bereits gepufferte Events verwerfen. Der Backend-Aufruf filtert
  nur künftige Events; die vorhandene Queue wird anschließend regulär gepumpt.
- Der Daemon darf nicht still einen zuvor beendeten Ringpuffer aktivieren oder
  unmaskierte Eingabe zulassen. Diese Optionen bleiben explizite Config-/CLI-
  Entscheidungen.
- Keine Hotkey-Implementierung beginnen, bevor der Zustandsautomat und der
  Einzelinstanz-Lifecycle durch Tests abgesichert sind.

## Nachweisquellen im Repository

- `clirec/recorder.py`: `start`, `set_paused`, `stop`, `cut_last`.
- `clirec/capture/base.py`: `CaptureBackend.set_paused` und Backend-Auswahl.
- `clirec/capture/winapi.py`, `clirec/capture/pynput_backend.py`: vorhandene
  globale Eingabequellen und Pause-Verhalten.
- `clirec/cli.py`: aktueller blockierender CLI-Loop und abgewiesene
  `stop`/`buffer`-Befehle.
- `clirec/config.py`: vorhandener, noch nicht verdrahteter `pause_hotkey`.
