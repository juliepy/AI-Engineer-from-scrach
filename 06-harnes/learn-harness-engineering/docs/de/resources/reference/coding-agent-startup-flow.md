# Coding-Agent-Startflow

Verwenden Sie dies zu Beginn jeder Session, nachdem die Initialisierung abgeschlossen ist.

## Feste Startvorlage

1. `pwd` ausführen und das Repository-Root bestätigen.
2. `claude-progress.md` lesen.
3. `feature_list.json` lesen.
4. Letzte Commits mit `git log --oneline -5` überprüfen.
5. `./init.sh` ausführen.
6. Einen Baseline-Smoke- oder End-to-End-Pfad ausführen.
7. Wenn die Baseline kaputt ist, diese zuerst beheben.
8. Das Feature mit höchster unvollständiger Priorität auswählen.
9. Nur an diesem Feature arbeiten, bis es verifiziert oder explizit blockiert ist.

## Warum diese Reihenfolge wichtig ist

- `pwd` verhindert versehentliche Arbeit im falschen Verzeichnis.
- Fortschritts- und Feature-Dateien stellen dauerhaften Zustand wieder her, bevor neue Edits beginnen.
- Letzte Commits erklären, was sich kürzlich geändert hat.
- `init.sh` standardisiert den Start anstatt sich auf Erinnerung zu verlassen.
- Baseline-Verifikation fängt kaputte Startzustände ab, bevor neue Arbeit sie verbirgt.

## Session-Ende-Spiegel

Die gleiche Session sollte beenden mit:

1. Fortschritt dokumentieren
2. Feature-Status aktualisieren
3. Einen Handoff schreiben falls nötig
4. Sichere Arbeit committen
5. Einen sauberen Neustart-Pfad hinterlassen
