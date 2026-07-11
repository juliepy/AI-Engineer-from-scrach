# SOP: Chrome DevTools-Validierungsschleife

Verwenden Sie diese SOP, wenn UI-Arbeit von tatsächlicher Laufzeit-Interaktion abhängt
und Screenshots, DOM-Zustand und Konsolenausgabe wichtiger sind als reine Code-Inspektion.

## Ziel

UI-Validierung in eine wiederholbare Interaktionsschleife verwandeln, die der Agent
ausführen kann, bis die Journey fehlerfrei ist.

## Kern-Schleife

1. Zielseite oder App-Instanz auswählen.
2. Veralteten Konsolenlärm bereinigen.
3. Den VORHER-Zustand erfassen.
4. Den UI-Pfad auslösen.
5. Laufzeitereignisse während der Interaktion beobachten.
6. Den NACHHER-Zustand erfassen.
7. Den Fix anwenden und die App bei Bedarf neustarten.
8. Validierung erneut ausführen, bis die Journey fehlerfrei ist.

## Erforderliche Eingaben

- ein stabiler Startbefehl
- eine reproduzierbare UI-Journey
- eine Methode zum Erstellen von Snapshots von DOM, Konsole oder Screenshots
- eine Regel, was als "fehlerfrei" gilt

## Ausführungs-SOP

1. Die Ziel-Journey im aktiven Plan aufschreiben.
2. Erfolg in beobachtbaren Begriffen definieren: Text vorhanden, Button aktiviert,
   Fehler verschwunden, Konsole sauber, Anfrage erfolgreich.
3. Snapshot des Anfangszustands vor der Interaktion erstellen.
4. Genau einen Pfad gleichzeitig auslösen.
5. Laufzeitereignisse, DOM-Änderungen und sichtbare Ausgabe aufzeichnen.
6. Wenn die Journey fehlschlägt, die kleinste verantwortliche Schicht reparieren und neustarten.
7. Denselben Pfad erneut ausführen und VORHER/NACHHER-Nachweise vergleichen.

## Fehlerfreiheitskriterien

- beabsichtigter sichtbarer Zustand ist vorhanden
- unerwartete Fehler sind abwesend
- Konsolenlärm ist verstanden oder bereinigt
- erneutes Ausführen desselben Pfads liefert dasselbe Ergebnis

## Zu aktualisierende Repo-Artefakte

- aktiver Ausführungsplan
- `docs/RELIABILITY.md`, wenn die Journey zu einer Golden Path wird
- Produktspezifikation, wenn sich das sichtbare Verhalten geändert hat
