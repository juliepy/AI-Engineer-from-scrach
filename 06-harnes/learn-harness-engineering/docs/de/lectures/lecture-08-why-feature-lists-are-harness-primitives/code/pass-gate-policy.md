# Pass-Gate-Richtlinie

Ein Feature darf nur von `passes: false` zu `passes: true` wechseln, wenn:

- der erwartete Workflow ausgeführt wurde
- der Erfolgsnachweis erfasst wurde
- kein blockierender Fehler im getesteten Pfad vorliegt
- die Implementierung die App nicht in einem defekten oder mehrdeutigen Zustand hinterlässt
