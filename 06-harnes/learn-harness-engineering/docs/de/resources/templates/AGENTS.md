# AGENTS.md

Dieses Repository ist für langfristige Coding-Agent-Arbeit konzipiert. Ziel ist nicht
die Maximierung der reinen Code-Produktion. Ziel ist es, das Repo in einem Zustand zu
hinterlassen, in dem die nächste Session ohne Raten weiterarbeiten kann.

## Start-Workflow

Bevor Code geschrieben wird:

1. Arbeitsverzeichnis mit `pwd` bestätigen.
2. `claude-progress.md` für den neuesten verifizierten Zustand und nächsten Schritt lesen.
3. `feature_list.json` lesen und das Feature mit höchster Priorität auswählen.
4. Letzte Commits mit `git log --oneline -5` überprüfen.
5. `./init.sh` ausführen.
6. Erforderlichen Smoke- oder End-to-End-Test vor neuer Arbeit ausführen.

Wenn die Baseline-Verifikation bereits fehlschlägt, diese zuerst beheben. Keine neue
Feature-Arbeit auf einen kaputten Startzustand stapeln.

## Arbeitsregeln

- Jeweils an einem Feature arbeiten.
- Ein Feature nicht als abgeschlossen markieren, nur weil Code hinzugefügt wurde.
- Änderungen im gewählten Feature-Scope belassen, es sei denn, ein Blocker erzwingt
  eine enge unterstützende Korrektur.
- Verifikationsregeln während der Implementierung nicht stillschweigend ändern.
- Dauerhafte Repo-Artefakte gegenüber Chat-Zusammenfassungen bevorzugen.

## Erforderliche Artefakte

- `feature_list.json`: Source of Truth für Feature-Status
- `claude-progress.md`: Session-Log und aktueller verifizierter Status
- `init.sh`: Standard-Start- und Verifikationspfad
- `session-handoff.md`: Optionaler kompakter Handoff für größere Sessions

## Definition of Done

Ein Feature ist erst fertig, wenn all dies zutrifft:

- das Zielverhalten ist implementiert
- die erforderliche Verifikation wurde tatsächlich ausgeführt
- der Nachweis ist in `feature_list.json` oder `claude-progress.md` dokumentiert
- das Repository bleibt über den Standard-Startpfad neustartfähig

## Session-Ende

Vor dem Beenden einer Session:

1. `claude-progress.md` aktualisieren.
2. `feature_list.json` aktualisieren.
3. Alle ungelösten Risiken oder Blocker dokumentieren.
4. Mit einer beschreibenden Nachricht committen, sobald die Arbeit in einem sicheren Zustand ist.
5. Das Repo sauber genug hinterlassen, damit die nächste Session sofort `./init.sh`
   ausführen kann.
