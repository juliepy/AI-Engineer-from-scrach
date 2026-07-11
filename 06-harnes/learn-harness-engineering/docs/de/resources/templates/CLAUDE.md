# CLAUDE.md

Sie arbeiten in einem Repository für langfristige Implementierungsarbeit.
Priorisieren Sie zuverlässigen Abschluss, Kontinuität über Sessions und explizite
Verifikation gegenüber Geschwindigkeit.

## Betriebsablauf

Zu Beginn jeder Session:

1. `pwd` ausführen und das erwartete Repository-Root bestätigen.
2. `claude-progress.md` lesen.
3. `feature_list.json` lesen.
4. Letzte Commits mit `git log --oneline -5` überprüfen.
5. `./init.sh` ausführen.
6. Prüfen, ob der Baseline-Smoke- oder End-to-End-Pfad bereits kaputt ist.

Dann genau ein unfertiges Feature auswählen und nur an diesem Feature arbeiten, bis
es verifiziert ist oder dokumentiert ist, warum es blockiert ist.

## Regeln

- Ein aktives Feature gleichzeitig.
- Keinen Abschluss ohne ausführbaren Nachweis behaupten.
- Die Feature-Liste nicht umschreiben, um unfertige Arbeit zu verbergen.
- Tests nicht entfernen oder schwächen, nur damit die Aufgabe fertig aussieht.
- Repo-Artefakte als System of Record verwenden.

## Erforderliche Dateien

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- `session-handoff.md` wenn ein kompakter Handoff nützlich ist

## Abschluss-Gate

Ein Feature kann nur zu `passing` wechseln, nachdem die erforderliche Verifikation
erfolgreich war und das Ergebnis dokumentiert ist.

## Vor dem Stoppen

1. Das Fortschrittslog aktualisieren.
2. Den Feature-Status aktualisieren.
3. Was noch kaputt oder unverifiziert ist, dokumentieren.
4. Committen, sobald das Repository sicher fortgesetzt werden kann.
5. Einen sauberen Neustart-Pfad für die nächste Session hinterlassen.
