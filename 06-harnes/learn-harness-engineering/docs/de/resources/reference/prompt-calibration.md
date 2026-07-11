# Prompt-Kalibrierung

Root-Instruktionen sollten den Betriebsrahmen definieren, nicht jeden möglichen Zug.

## In der Root-Datei behalten

- Repository-Zweck und Scope
- Startpfad
- Verifikationspfad
- Nicht-verhandelbare Einschränkungen
- Erforderliche Zustandsartefakte
- Session-Ende-Regeln

## Aus der Root-Datei auslagern

- Lange historische Edge Cases
- Themenspezifische Implementierungsdetails
- Lokale Architektur-Notizen, die zum Code gehören
- Beispiele, die nur für ein Subsystem gelten

## Arbeitsregel

Die Root-Datei sollte einer frischen Session helfen, sich schnell zu orientieren. Wenn die
Datei zum Sammelbecken für jeden vergangenen Fehlschlag wird, das Detail in kleinere
Dokumente aufteilen und stattdessen dorthin verlinken.
