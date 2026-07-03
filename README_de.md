# clirec

`clirec` speichert Maus-/Tastatur-Demonstrationen als menschenlesbare
`.clirec`-Dateien und spielt sie über einen injizierten Executor wieder ab.
Gedacht ist es für Agenten- und CLI-Workflows, bei denen ein kurzer Vormachpfad
zuverlässiger ist als eine lange verbale Beschreibung.

Der Kern hat keine Laufzeit-Abhängigkeiten. Unter Windows gibt es standardmäßig
einen ctypes-Capture-Backend; plattformübergreifend kann optional `pynput`
installiert werden.

```bash
pip install clirec
pip install clirec[record]
```

Bis zur Paketveröffentlichung:

```bash
pip install git+https://github.com/ellmos-ai/clirec.git
```

Kompatibilität mit `open-compute` läuft über `oc rec ...`; `open-compute` lädt
`clirec` dabei erst bei Nutzung.
