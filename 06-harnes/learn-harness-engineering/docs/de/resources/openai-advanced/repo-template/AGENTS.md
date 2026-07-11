# AGENTS.md

Dieses Repository ist für langlaufende Coding-Agent-Arbeit optimiert. Halten Sie diese Datei
kurz. Verwenden Sie sie als Routing-Schicht zu den System-of-Record-Docs, nicht als
gigantische Instruktionsablage.

## Start-Workflow

Bevor Code geändert wird:

1. Das Repo-Root mit `pwd` bestätigen.
2. `ARCHITECTURE.md` für die aktuelle Systemübersicht und harten Abhängigkeitsregeln lesen.
3. `docs/QUALITY_SCORE.md` lesen, um zu sehen, welche Domänen oder Schichten am schwächsten sind.
4. `docs/PLANS.md` lesen, dann den aktiven Plan öffnen, an dem gearbeitet wird.
5. Die relevante Produktspezifikation in `docs/product-specs/` lesen.
6. Den Standard-Bootstrap- und Verifikationspfad für dieses Repo ausführen.
7. Wenn die Baseline-Verifikation fehlschlägt, die Baseline reparieren, bevor neuer Scope hinzugefügt wird.

## Routing-Map

- `ARCHITECTURE.md`: Domänen-Map, Schichtenmodell, Abhängigkeitsregeln
- `docs/design-docs/index.md`: Designentscheidungen und Kernüberzeugungen
- `docs/product-specs/index.md`: aktuelles Produktverhalten und Abnahmeziele
- `docs/PLANS.md`: Plan-Lebenszyklus und Ausführungsplan-Policy
- `docs/QUALITY_SCORE.md`: Produktdomänen- und Schichtengesundheit
- `docs/RELIABILITY.md`: Laufzeitsignale, Benchmarks und Neustart-Erwartungen
- `docs/SECURITY.md`: Secrets, Sandbox, Daten und externe Aktionsregeln
- `docs/FRONTEND.md`: UI-Einschränkungen, Designsystem-Regeln, Barrierefreiheits-Checks

## Arbeitsvertrag

- Von einem begrenzten Plan oder Feature-Slice gleichzeitig arbeiten.
- Arbeit nicht als fertig markieren nur aufgrund von Code-Inspektion; ausführbarer Nachweis ist erforderlich.
- Wenn Sie Verhalten ändern, die zugehörigen Produkt-, Plan- oder Zuverlässigkeitsdocs in derselben Session aktualisieren.
- Wenn Sie wiederholtes Review-Feedback sehen, es zu einer mechanischen Regel, einem Check oder Linter befördern, anstatt es im Chat erneut zu erklären.
- Generiertes Material in `docs/generated/` und Quellreferenzen in `docs/references/` aufbewahren.
- Kleine, aktuelle Docs hinzufügen anstatt diese Datei wachsen zu lassen.

## Definition of Done

Eine Änderung ist erst fertig, wenn all dies zutrifft:

- Zielverhalten ist implementiert
- Erforderliche Verifikation wurde tatsächlich ausgeführt
- Nachweis ist vom relevanten Plan- oder Qualitätsdokument verlinkt
- Betroffene Docs bleiben aktuell
- Das Repository kann sauber über den Standard-Startpfad neugestartet werden

## Session-Ende

Vor dem Beenden einer Session:

1. Den aktiven Ausführungsplan aktualisieren.
2. `docs/QUALITY_SCORE.md` aktualisieren, falls sich eine Domäne oder Schicht signifikant geändert hat.
3. Neue Schulden in `docs/exec-plans/tech-debt-tracker.md` dokumentieren, falls zurückgestellt.
4. Fertige Planks nach `docs/exec-plans/completed/` verschieben, wenn angemessen.
5. Das Repo in einem neustartfähigen Zustand mit klarer nächster Aktion hinterlassen.
