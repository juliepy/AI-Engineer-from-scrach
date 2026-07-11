# SOP: Unsichtbares Wissen im Repo codieren

Verwenden Sie diese SOP, wenn wichtiger Kontext noch in Google Docs, Chat-Threads,
Tickets oder in den Köpfen von Menschen lebt.

## Ziel

Agenten-unsichtbares Wissen in der Codebasis auffindbar machen, damit eine neue
Sitzung darauf reagieren kann, ohne sich auf vorherige Gespräche zu verlassen.

## Auslösesignale

- Der Agent fragt ständig, wie das System funktioniert.
- Menschen sagen "wir haben das in Slack entschieden" oder "folgen Sie dem, was X letzte Woche gesagt hat."
- Reviews verweisen auf Produkt- oder Sicherheitsregeln, die nicht im Repo dokumentiert sind.
- Neue Sitzungen wiederholen Entdeckungsarbeit, die bereits geklärt sein sollte.

## Ausführungs-SOP

1. Die unsichtbaren Wissensquellen auflisten: Docs, Chats, unausgesprochene Teamregeln, mündliche Entscheidungen.
2. Für jede Quelle fragen: Ist das Architektur, Produktverhalten, Sicherheitsrichtlinie,
   Zuverlässigkeitserwartung, Plankontext oder Referenzmaterial?
3. Im entsprechenden Repo-Artefakt codieren:
   - Architektur -> `ARCHITECTURE.md`
   - Produktverhalten -> `docs/product-specs/`
   - Designbegründung -> `docs/design-docs/`
   - Ausführungszustand -> `docs/exec-plans/`
   - wiederholte externe Referenzen -> `docs/references/`
   - Qualitäts- oder Zuverlässigkeitserwartungen -> `docs/QUALITY_SCORE.md` oder `docs/RELIABILITY.md`
4. Vage Aussagen durch operationell nützliche Formulierungen ersetzen.
5. Veraltete Kopien entfernen oder als veraltet markieren, damit das Repo eine auffindbare Wahrheit behält.

## Gute Codierungsregeln

- Für Auffindbarkeit schreiben, nicht für literarische Vollständigkeit.
- Kurze Dokumente mit klaren Dateinamen bevorzugen.
- Verwandte Artefakte miteinander verknüpfen.
- Dauerhafte Regeln speichern, keine Meeting-Protokolle.
- Das Repo in derselben Sitzung aktualisieren, in der die Entscheidung getroffen wird.

## Definition von Fertig

- Ein neuer Agent kann die relevante Regel finden, ohne einen Menschen zu fragen.
- Dieselbe Tatsache ist nicht über mehrere widersprüchliche Dateien verstreut.
- Das neue Artefakt liegt nahe am Code oder Workflow, den es steuert.
