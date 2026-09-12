# Offene Befunde — clirec

**Erfasst am:** 2026-07-28  
**Rolle:** MAINTAINER (TaskMaster Loop)

---

### Befund 1: Noch nicht live verifizierte Platform- & Executor-Smokes

- **Fundort:** `RELEASE_GATE.md` (Zeilen 33-41)
- **Beleg:**  
  - Physischer Capture-Smoke auf macOS/Linux mit `pynput`-Backend steht noch aus.
  - End-to-End-Lauf mit IME/Dead-Key und Multi-Monitor-Mixed-DPI steht noch aus.
  - Reallauf von `open-compute`-Replay gegen produktive GUI steht noch aus.
- **Status:** In `RELEASE_GATE.md` sauber dokumentiert; blockiert Alpha-Quellstand (0.2.0) nicht.

---

### Befund 2: Instandhaltung Steuerdatei `llms.txt` (Behoben)

- **Fundort:** `llms.txt`
- **Beleg:**  
  Dateikopf hatte Stand `2026-07-27`. Testsuiten-Angabe präzisiert.
- **Maßnahme:**  
  `llms.txt` im MAINTAINER-Lauf vom 2026-07-28 auf `80+7` -> `87 Pytest-Tests` und `Last-checked: 2026-07-28` aktualisiert.
