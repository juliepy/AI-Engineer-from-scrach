[中文版本 →](../../../zh/projects/project-06-runtime-observability-and-debugging/)

> Zugehörige Lektionen: [Lektion 11. Die Runtime des Agenten beobachtbar machen](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [Lektion 12. Sauberes Handoff am Ende jeder Session](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> Vorlagendateien: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/de/resources/templates/)

# Projekt 06. Einen vollständigen Agenten-harness bauen (Capstone)

## Was du tust

Dies ist das Abschlussprojekt. Setze alles zusammen, was du in den ersten fünf Projekten gelernt hast, führe einen vollständigen Benchmark aus und mache danach einen Cleanup-Pass, um zu prüfen, ob die Qualität wartbar bleibt.

Nutze ein festes Multi-Feature-Aufgabenset, das einen vollständigen Produktschnitt abdeckt: Dokumentimport, Indexierung, Q&A mit Zitaten, Runtime-Beobachtbarkeit und einen lesbaren, wiederaufnehmbaren Repository-Zustand. Führe zuerst einen schwachen harness-Baseline-Lauf aus, dann deinen stärksten harness, danach Cleanup und erneuten Lauf. Zum Schluss machst du ein harness-Ablationsexperiment: Entferne jeweils eine Komponente und beobachte, welche wirklich wichtig sind.

## Nutze das eingecheckte Projekt

Repository-Pfad: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| Verzeichnis | Inhalt | Vergleichspunkt |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | Produktcode ist weitgehend vollständig, aber die Harness-Oberfläche ist absichtlich geschwächt: nur grundlegendes [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md), kein `feature_list.json`, kein `session-handoff.md`, keine Clean-State-Checkliste und keine Benchmark/Cleanup-Skripte. | Manuelle Baseline-Beobachtungen mit schwachem Harness. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | Vollständiger Harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), Qualitäts-/Evaluator-Dokumente und Skripte. | [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) und [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh) ausführen und Qualitätsevidenz vergleichen. |

## Werkzeuge

- Claude Code oder Codex
- Git
- Node.js + Electron
- Vorlage für Qualitätsdokument
- Evaluator-Rubrik
- Alle harness-Komponenten aus den ersten fünf Projekten

## Harness-Mechanismus

Vollständiger harness: alle Mechanismen + Beobachtbarkeit + Ablationsstudie
