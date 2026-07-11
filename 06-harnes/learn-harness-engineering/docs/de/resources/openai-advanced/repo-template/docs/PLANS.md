# PLANS.md

Diese Datei definiert, wie Ausführungspläne erstellt, aktualisiert, abgeschlossen
und archiviert werden.

## Wann ein Plan erforderlich ist

Erstellen Sie einen Ausführungsplan, wenn die Arbeit:

- mehr als eine Sitzung umfasst
- mehr als ein Subsystem verändert
- nicht-triviale Verifikations- oder Rollout-Risiken birgt
- von offenen Entscheidungen abhängt, die dokumentiert werden sollten

## Plan-Speicherorte

- `docs/exec-plans/active/`: Pläne, die aktuell die Arbeit steuern
- `docs/exec-plans/completed/`: abgeschlossene Pläne, die für zukünftigen Agenten-Kontext behalten werden
- `docs/exec-plans/tech-debt-tracker.md`: aufgeschobene Arbeit und Folgeaufgaben

## Mindest-Abschnitte eines Plans

- Zielsetzung
- Umfang und Nicht-Umfang
- Verifikationspfad
- Risiken und Blocker
- Fortschrittslog
- Offene Entscheidungen

## Betriebsregeln

- Ein aktiver Plan sollte einen klar verantwortlichen aktuellen Schritt haben.
- Den Plan aktualisieren, während die Arbeit voranschreitet; nicht als statischen
  Text behandeln.
- Wenn eine Entscheidung die Implementierungsrichtung ändert, im Plan dokumentieren.
- Abgeschlossene Pläne nach `completed/` verschieben, damit Agenten den bisherigen
  Kontext weiterhin finden können.
