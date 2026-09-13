# TODO

## STATUS

| Category | Status | Hinweis |
|---|---|---|
| Paketkern | grün | Kernpaket ohne Laufzeitabhängigkeiten; Tests decken Format, Recorder, Replay, Capture und CLI ab. |
| Release-Gate | grün | Quell-, Paket-, Wheel-Installations- und CLI-Smokes sind in `RELEASE_GATE.md` dokumentiert. |
| Datenschutz | grün/beobachtet | Tastatureingaben werden parameterisiert; Audio ist getrenntes Opt-in mit Purge/Retention, reale Sitzungen erfordern Review. |
| Integration | beobachtet | `open-compute` lädt `clirec` lazy; echte Executor-Replay-Smokes bleiben integrationsseitig zu prüfen. |
| Veröffentlichung | offen | Kein Tag im Repository, kein PyPI-Paket; der Name `clirec` ist auf PyPI unbelegt (404, geprüft 2026-09-03). |
| Sprache | offen | Das Repo tritt englisch auf, `SKILL.md`, `TODO.md` und die beiden `docs/verification/`-Notizen sind deutsch. Kein i18n-Mechanismus vorhanden — bewusst entscheiden statt weiter mischen. |

## Nächste sinnvolle Schritte

- [Task 158] Optionalen `pynput`-Record-Pfad auf einer Nicht-Windows-Plattform prüfen.
- [Task 157] `open-compute`-Replay mit einem realen Executor als Integrations-Smoke nachziehen.
- [Task 159] Realen Windows-Mikrofon-Smoke mit Nutzerfreigabe durchführen: Pause/Resume,
  Synchronität, Geräteverlust, Neustart-Readback und Privacy-Review.
- [Task 159] Mikrofon-Smokes auf macOS und Linux getrennt nachholen; bis dahin keine
  plattformübergreifende Audiofreigabe behaupten.

## Befunde des Pflegelaufs 2026-09-03

- [ ] **Task 156 — Release-Tags fehlen vollständig.** `CHANGELOG.md` führt 0.1.0, 0.2.0 und
      0.2.1, das Repository trägt **keinen einzigen** Tag. Damit gibt es keinen
      benannten Stand zum Zurückkehren oder Pinnen. Entscheiden: rückwirkend
      taggen oder erst ab dem nächsten Release beginnen — und dann konsequent.
- [ ] **Task 156 — PyPI-Name `clirec` sichern oder bewusst freigeben.** Am 2026-09-03
      unbelegt (HTTP 404). Solange er frei ist, kann ihn jeder besetzen; die
      README verwies bis zu diesem Lauf auf genau diesen Namen.
- [ ] **Task 160 — DSGVO-Rollenklärung in die Dokumentation.** Wer außerhalb rein privater
      Zwecke aufzeichnet, wird selbst Verantwortlicher (Haushaltsausnahme
      Art. 2 Abs. 2 lit. c DSGVO greift dann nicht). Der Nutzen der Klarstellung
      ist gegen die Gefahr abzuwägen, mit einer Aussage über die Rolle des
      Lesers in die Nähe einer Rechtsdienstleistung zu geraten. Bewusst
      entscheiden, nicht nebenbei formulieren.
- [ ] **Task 161 — Sprachentscheidung für `SKILL.md`.** Die Datei ist agentengerichtet und
      deutsch, das Produkt englisch. Entweder englisch übersetzen (dann fällt
      die Umlautprüfung im Test weg) oder die deutsche Fassung ausdrücklich als
      solche deklarieren. Aktuell ist beides halb.
- [ ] **Task 162 — Eintrag im Organisationsprofil steht in der falschen Rubrik.**
      `ellmos-ai/.github` führt clirec unter „Evaluation, templates and
      maintenance"; sachlich gehört es neben `open-compute` unter „Agent modules
      and orchestration". Im Lauf vom 2026-09-03 nicht geändert: der dortige
      Klon hatte uncommittete Fremdänderungen **in genau dieser Datei**.
- [ ] **Task 163 — StGB in der law-checker-Registry aktivieren.** Für den Rechtscheck
      dieses Repos musste das Strafgesetzbuch on demand beschafft werden, weil
      es dort deaktiviert ist. Für jedes Werkzeug, das aufzeichnet, ist es die
      einschlägigste Norm — der Schalter gehört umgelegt.

- [ ] **Task 164 — After-care-PR #18 maintainerseitig entscheiden.** Der offene
      Branch `after-care/full-2026-09-03` ist laut Live-Inventar mergeable und
      die aktuellen CodeQL-, Matrix- und Package-Checks sind grün; Merge oder
      Zurückstellung bleibt eine Maintainerentscheidung.

## TASKWRITER-REVIEW-LOG 2026-09-05

- Präsentation `2b2e96ec-2a39-4bdf-8f44-865ef90faafe` wurde unter dem aktiven
  Lease verarbeitet. Der Checkout `after-care/full-2026-09-03` war sauber und
  zu seinem Remote-Branch synchron; `origin/main` ist der Zielzweig des offenen
  PR #18 und daher kein lokaler Divergenz-Blocker.
- Read-only-Verifikation: `119 passed`, Ruff-Check und -Formatprüfung grün,
  `compileall` grün, Paketbau für 0.3.0 erzeugt Wheel und sdist. `twine` fehlt
  im aktuellen Interpreter; die CI-Package-Job installiert es über `.[dev]`.
- Es wurden die Tasks 156–164 mit Quelle, Herleitung, Abnahme, Verifikation,
  Abhängigkeiten, Aufwand und Scope angelegt. Veröffentlichungen, Merges,
  Mikrofon-Smokes und zentrale Registry-Änderungen wurden nicht ausgeführt.

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
