[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Zugehörige Lektionen: [Lektion 07. Klare Aufgabengrenzen für Agenten ziehen](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Lektion 08. Feature-Listen nutzen, um Agentenarbeit zu begrenzen](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Vorlagendateien: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/de/resources/templates/)

# Projekt 04. Runtime-Feedback nutzen, um Agentenverhalten zu korrigieren

## Was du tust

Füge Runtime-Beobachtbarkeit hinzu, etwa Startlogs, Import-/Indexierungslogs und Fehlerzustände, sowie Architekturregeln, um Verstöße zwischen Schichten zu verhindern. Baue einen Runtime-Bug ein, den der Agent beheben soll.

Du führst es zweimal aus: zuerst ohne Logs oder Regeln, dann mit passenden Werkzeugen und Regeln.

## Nutze das eingecheckte Projekt

Repository-Pfad: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Verzeichnis | Inhalt | Vergleichspunkt |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Project-03-Code mit schwachen Diagnosesignalen. Der eingebaute Indexierungsfehler kann Chunking bei großen Dateien brechen, und es gibt kein Architekturprüfskript. | Wie lange der Agent ohne Runtime-Signale bis zur Ursache braucht. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Strukturierter Logger, Architekturgrenzendokumentation und Prüfsktipt, korrigierte Chunking-Logik und [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Ob Logs und Grenzprüfungen die Korrektur schneller und weniger invasiv machen. |

Wichtige Dateien: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## Werkzeuge

- Claude Code oder Codex
- Git
- Node.js + Electron

## Harness-Mechanismus

Runtime-Feedback + Scope-Kontrolle + inkrementelle Indexierung
