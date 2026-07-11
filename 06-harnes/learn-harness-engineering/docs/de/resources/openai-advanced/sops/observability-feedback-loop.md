# SOP: Observability-Feedback-Schleife

Verwenden Sie diese SOP, wenn Debugging langsam ist, Agenten ständig Erfolg ohne
Nachweise behaupten oder das Laufzeitverhalten schwerer zu inspizieren ist als der
Code selbst.

## Ziel

Dem Agenten eine lokale Feedback-Schleife über Logs, Metriken, Traces und ausführbare
Workloads geben, damit er aus der Ausführung heraus argumentieren kann, nicht nur aus
der Code-Inspektion.

## Minimaler Stack

- Anwendung sendet strukturierte Logs
- Anwendung sendet Metriken und Traces, wenn machbar
- lokaler Fan-out- oder Sammelschicht
- Abfrageschnittstellen für Logs, Metriken und Traces
- wiederholbarer Workload oder Benutzer-Journey, um nach jeder Änderung erneut auszuführen

## Ausführungs-SOP

1. Die Golden Runtime-Journeys definieren, die am wichtigsten sind.
2. Strukturierte Logs zum Start und zum kritischen Pfad hinzufügen.
3. Metriken für Latenz, Fehleranzahlen oder Warteschlangentiefe hinzufügen, wo nützlich.
4. Traces oder Timing-Marker für langsame oder mehrstufige Abläufe hinzufügen.
5. Die Signale aus der lokalen Entwicklungsumgebung abfragbar machen.
6. Dem Agenten einen wiederholbaren Workload oder ein Szenario zum erneuten Ausführen geben.
7. Die Schleife einfordern: abfragen -> korrelieren -> argumentieren -> implementieren ->
   neustarten -> erneut ausführen -> verifizieren.

## Debug-Sitzungs-Checkliste

- Was ist fehlgeschlagen?
- Welches Signal beweist den Fehler?
- Welche Schicht ist für den Fehler verantwortlich?
- Was hat sich nach dem Fix geändert?
- Ist die App sauber neugestartet?
- Hat derselbe Workload nach erneutem Ausfahren bestanden?

## Definition von Fertig

- Der Agent kann einen Fehlermodus aus Laufzeitnachweisen erklären.
- Derselbe Workload kann nach jeder Änderung erneut ausgeführt werden.
- Neustart und erneutes Ausführen sind Teil der normalen Aufgaben-Schleife.
- Zuverlässigkeitssignale sind in `docs/RELIABILITY.md` dokumentiert.
