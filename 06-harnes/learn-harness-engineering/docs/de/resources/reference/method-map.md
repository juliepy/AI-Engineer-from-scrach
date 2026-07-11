# Methoden-Map

Diese Tabelle ordnet die häufigsten Fehlermodi von langlaufenden Coding-Agenten dem
Artefakt oder der Betriebsregel zu, die sie normalerweise zuerst behebt.

| Fehlermodus | Wie es in der Praxis aussieht | Primäre Lösung | Unterstützendes Artefakt |
| --- | --- | --- | --- |
| Kaltstart-Verwirrung | Eine neue Session verbringt die meiste Zeit damit, Setup und Status neu zu entdecken | Das Repository zum System of Record machen | `claude-progress.md` |
| Scope-Ausdehnung | Der Agent startet mehrere Features und schließt keines sauber ab | Aktiven Scope einschränken | `feature_list.json` |
| Vorzeitiger Abschluss | Der Agent behauptet Fertig nach Code-Edits, aber vor ausführbarem Nachweis | Abschluss an Nachweis binden | `clean-state-checklist.md` |
| Fragiler Start | Jede Session lernt neu, wie das Projekt bootet | Setup und Verifikation standardisieren | `init.sh` |
| Schwacher Handoff | Die nächste Session kann nicht erkennen, was verifiziert, kaputt oder als nächstes dran ist | Mit einem expliziten Handoff beenden | `session-handoff.md` |
| Subjektives Review | Review-Qualität hängt von Geschmack oder Erinnerung ab | Output mit festen Kategorien bewerten | `evaluator-rubric.md` |

## Betriebsprinzip

Das kleinste Artefakt hinzufügen, das den beobachteten Fehlermodus direkt adressiert.
Vermeiden Sie, jedes Zuverlässigkeitsproblem durch das Einfügen von mehr Text in eine
globale Instruktionsdatei zu lösen.
