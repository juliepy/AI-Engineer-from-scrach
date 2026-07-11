# SOP: Geschichtete Domänenarchitektur

Verwenden Sie diese SOP, wenn der Agent ständig Grenzen verletzt, Logik über Schichten
hinweg dupliziert oder Code erzeugt, der nach wenigen Sitzungen schwer zu reviewen ist.

## Ziel

Domänengrenzen so explizit machen, dass Agenten schnell arbeiten können, ohne
unsichtbar die Struktur zu beeinträchtigen.

## Zielmodell

Bevorzugen Sie innerhalb einer Geschäftsdomäne diesen gerichteten Fluss:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Produktübergreifende Concerns sollten durch explizite Provider oder Adapter eintreten.
Gemeinsame Utils bleiben außerhalb der Domäne und sollten keine Domänenlogik ansammeln.

## Einrichtungs-Checkliste

- Die aktuellen Domänen in `ARCHITECTURE.md` definieren.
- Erlaubte Abhängigkeitsrichtungen in `ARCHITECTURE.md` dokumentieren.
- Produktübergreifende Schnittstellen wie Auth, Telemetrie und externe APIs erfassen.
- Eine kurze Notiz für die aktuell schwerste Grenzverletzung hinzufügen.
- Entscheiden, was mechanisch durch Lint, Tests oder Skripte durchgesetzt werden soll.

## Ausführungs-SOP

1. Die Codebasis in Domänen aufteilen, bevor der Implementierungsstil angefasst wird.
2. Für jede Domäne die erlaubte Schichtenfolge identifizieren.
3. Alle produktübergreifenden Concerns identifizieren und durch Provider oder Adapter routen.
4. Mehrdeutige gemeinsame Logik entweder in die besitzende Domäne oder in wirklich
   generische Utils verschieben.
5. Die Regeln in `ARCHITECTURE.md` dokumentieren.
6. Eine ausführbare Leitplanke für die teuerste Verletzung hinzufügen.
7. Qualitätsbewertung nach der Änderung aktualisieren.

## Definition von Fertig

- Ein neuer Agent kann erkennen, welche Schicht eine Änderung besitzt.
- UI-Code greift nicht mehr direkt auf Repo oder externe Seiteneffekte zu.
- Produktübergreifende Concerns haben benannte Einstiegspunkte.
- Mindestens eine wichtige Grenze wird mechanisch durchgesetzt.

## Zu aktualisierende Repo-Artefakte

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- `docs/design-docs/`, wenn sich die Begründung geändert hat
- `docs/PLANS.md` oder der aktive Ausführungsplan
