# clirec

[![clirec tests](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/tests.yml)
[![CodeQL](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml/badge.svg)](https://github.com/ellmos-ai/clirec/actions/workflows/codeql.yml)

`clirec` speichert Maus-/Tastatur-Demonstrationen als menschenlesbare
`.clirec`-Dateien und spielt sie über einen injizierten Executor wieder ab.
Gedacht ist es für Agenten- und CLI-Workflows, bei denen ein kurzer Vormachpfad
zuverlässiger ist als eine lange verbale Beschreibung.

Der Kern hat keine Laufzeitabhängigkeiten. Unter Windows gibt es standardmäßig
ein ctypes-Capture-Backend; plattformübergreifend kann optional `pynput`
installiert werden. Windows-UIA-Metadaten sind ein separates optionales Extra.

```bash
pip install clirec
pip install clirec[record]
pip install clirec[uia]
```

Bis zur Paketveröffentlichung:

```bash
pip install git+https://github.com/ellmos-ai/clirec.git
```

Kompatibilität mit `open-compute` läuft über `oc rec ...`; `open-compute` lädt
`clirec` dabei erst bei Nutzung.

Im sicheren Standard wird eingegebener Text nie im Klartext gespeichert. Jeder
Textabschnitt wird zu einem Parameter wie `${input_1}` und beim Replay mit
`--param input_1=Wert` befüllt. `--allow-unmasked-input` ist eine ausdrückliche
unsichere Freigabe; solche Aufnahmen müssen vor dem Teilen geprüft werden.

## CLI

```bash
clirec start login-flow
clirec validate recordings/login-flow.clirec
clirec list --dir recordings
clirec replay recordings/login-flow.clirec --param input_1=Wert
```

Replay ist backend-neutral. Aus Python mit einem Executor-Objekt oder über eine
Integration wie `open-compute`:

```bash
oc rec replay recordings/login-flow.clirec
```

## Tests

```bash
python -m pytest -q
python -m ruff check clirec tests
python -m ruff format --check clirec tests
python -m compileall -q clirec tests
```

Die aktuelle Paket- und Plattformgrenze steht in [RELEASE_GATE.md](RELEASE_GATE.md).
