# Audio-/Format-v2-Verifikation vom 2026-08-20

## Belegt

- Windows 11 / Python 3.12;
- 113 automatisierte Tests bestanden;
- Ruff-Lint, Ruff-Formatprüfung und `compileall` grün;
- synthetische deterministische PCM-Chunks für Start, Stop, Flush, Pause,
  Resume, monotone Zeitbasis, `cut_last()`, Drift und Größenlimit;
- v1-Readback sowie v2 ohne und mit Audio;
- relative SHA-256-Medien, Traversal-/Symlink-/Orphan-Abweisung;
- Rollback bei simuliertem Ausfall des finalen Commit-Markers;
- getrennte Audio-/Transkript-Purges, Retention und Recovery;
- kanonischer STT-Adapter mit nachgewiesenem `persist=False`;
- synthetischer Episoden-, Skill- und Workflow-Reviewexport.

Die Tests enthalten ausschließlich synthetische Bytes und keine echte Stimme,
personenbezogenen Daten oder Hardwarekennung.

## Noch nicht live abgenommen

Ein realer Mikrofonlauf wurde in dieser unbeaufsichtigten Sitzung aus
Datenschutzgründen nicht gestartet. Offen bleiben auf geeigneter, vom Nutzer
freigegebener Hardware:

1. Windows-Mikrofonaufnahme mit sichtbarem Status;
2. Pause/Resume und Audio-/Event-Synchronität;
3. Geräteverlust während der Aufnahme;
4. Neustart/Readback und manuelles Privacy-Review;
5. getrennte echte macOS-/Linux-Smokes.

Diese Punkte werden nicht durch synthetische Tests als live bestanden
ausgegeben.
