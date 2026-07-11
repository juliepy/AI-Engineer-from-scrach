# FRONTEND.md

Diese Datei definiert stabile Frontend-Erwartungen, damit Agenten nicht unvorhersehbar
UI-Muster erfinden.

## UI-Prinzipien

- Optimieren Sie auf Klarheit vor Neuheit.
- Halten Sie Interaktionsabläufe auffindbar und neustartbar.
- Bevorzugen Sie eine kleine Anzahl wiederverwendbarer Komponenten gegenüber einmaligen Varianten.
- Barrierefreiheitsprüfungen sind Teil der normalen Verifikation, keine Polierarbeit.

## Leitplanken

- Dokumentieren Sie das Design-System oder die Komponentenbibliothek in `docs/references/`.
- Erfassen Sie wichtige benutzerseitige Zustände: leer, laden, Erfolg, Fehler, erneut versuchen.
- Halten Sie Text, Tastaturverhalten und visuelle Hierarchie über alle Abläufe hinweg konsistent.
- Wenn ein UI-Fehler behoben wird, den zugehörigen Validierungsschritt hinzufügen oder aktualisieren.

## Verifikationserwartungen

- Beweise für kritische Benutzer-Journeys erfassen.
- Browser- oder Laufzeit-Validierungsschritte im entsprechenden Plan dokumentieren.
- Wenn visuelle Regressionen häufig auftreten, Screenshot- oder DOM-Prüfungen standardisieren.
