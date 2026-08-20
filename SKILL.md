---
name: clirec
description: Eigenständiger Aufnahmekanal für CLI- und Agenten-Workflows. Nutze diesen Skill, wenn ein Skill/Workflow durch eine konkrete Maus/Tastatur-Demonstration beschleunigt oder ein in der Vergangenheit schwerer Ablauf zuverlässig vorgemacht werden soll. Nimmt eine .clirec-Datei auf und spielt sie über eine Executor-Integration adaptiv ab.
---

# clirec — Aufnahmekanal

Eine Aufnahme (`.clirec`) ist ein **angeheftetes Demonstrations-Artefakt** zu einem
bestehenden Skill/Workflow — kein eigener Workflow. Sie ist eine **Zusatzfunktion**:
Wenn ein Skill ohne Aufnahme funktioniert, ist das besser. Aufnahme nur nutzen, wenn
ein Ablauf schwer oder oft fehlschlug.

## Wann aufnehmen
- Ein Ziel ist verbal beschrieben (Skill/Workflow existiert), aber das Modell scheitert
  an der GUI-Ausführung oder es ist langsam/fehleranfällig.
- Dann: hier lesen → aufnehmen → aus dem Ziel-Skill auf die `.clirec` verweisen.

## Aufnehmen
1. `clirec start <name>` — Tätigkeit ausführen — `Strg+C` beendet und speichert.
2. Optional kommentiert aufnehmen: `clirec start <name> --audio
   --audio-consent`. Audio ist standardmäßig aus; es läuft kein versteckter
   Hintergrund-Daemon.
3. Ergebnis: `<recordings_dir>/<name>.clirec`. Ein Host kann zusätzlich einen
   Frame-Grabber injizieren; nur dann entsteht `<name>.clirec.frames/` als Beleg.

## Referenzieren (Verweis-Konvention)
Im Ziel-Skill den **relativen Pfad** zur `.clirec` nennen und beschreiben, **wann** sie
gilt, z. B.: „Wenn der Login-Dialog erscheint, nutze `login.clirec`." Aufnahme entweder
unter `recordings/` im Modul oder direkt **neben** der referenzierenden `SKILL.md`.

## Abspielen
- `clirec replay <name>.clirec [--param k=v]` — benötigt eine Executor-Integration,
  weil clirec selbst backend-neutral bleibt.
- In `open-compute`: `oc rec replay <name>.clirec [--param k=v]` nutzt den lazy geladenen
  clirec-Adapter und spielt zuerst stumpf (Koordinaten), bei Abweichung agentengestützte
  Re-Lokalisierung; Frame-PNG dient als Beleg.

## Selbst-Verifikation (Pflicht beim Ausführen)
Nach einem Ablauf/Replay **immer selbst prüfen**: „Habe ich das Ziel erreicht?" Bei
Zweifel den Nutzer zuschauen lassen und Korrekturen aufnehmen lassen — nicht raten.

## Kontext-Referenzierung statt Auto-Export
Wird ein Skill ausgeführt, **immer überlegen, in welchem Kontext er aufgerufen wurde**,
und die passende `.clirec` referenzieren, **wenn sie funktioniert**. Kein automatischer
Export nötig — die Verknüpfung lebt im Skript-Text.

## Datenschutz
Systemweiter Mitschnitt ist sensibel. Im sicheren Standard wird jede Texteingabe,
einschließlich Passwort-Eingaben, als `${input_N}` parameterisiert und nicht im Klartext
gespeichert. Beim Replay ist
der Wert per `--param input_N=Wert` anzugeben. `--allow-unmasked-input` schaltet
diesen Schutz ausdrücklich für die ganze Sitzung ab. Audio kann gesprochene
Geheimnisse und andere Personen erfassen und hat deshalb einen eigenen
Consent-, Retention- und Purge-Vertrag. Optionale globale Pause-/Stop-Hotkeys
laufen nur im sichtbaren Vordergrundprozess (`--global-hotkeys`) und werden mit
ihm beendet. In der öffentlichen Version sind Ereignis- und Audio-Ringpuffer
standardmäßig **aus**.
