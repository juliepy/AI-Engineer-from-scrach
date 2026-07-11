[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Zugehörige Lektionen: [Lektion 09. Agenten daran hindern, zu früh Erfolg zu melden](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Lektion 10. Nur ein vollständiger Pipeline-Lauf zählt als echte Verifikation](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Vorlagendateien: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/de/resources/templates/)

# Projekt 05. Den Agenten seine eigene Arbeit verifizieren lassen

## Was du tust

Implementiere Rollentrennung: einen generator für die Umsetzung, einen evaluator für die Prüfung und optional einen planner. Führe drei Läufe durch, um den Effekt jeder zusätzlichen Rolle zu messen.

Wähle eine substanzielle Feature-Erweiterung, etwa Multi-Turn-Konversation, Neugestaltung des Zitat-Panels oder Dokumentfilterung, und halte sie über alle Läufe hinweg konstant.

## Nutze das eingecheckte Projekt

Repository-Pfad: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Verzeichnis | Inhalt | Vergleichspunkt |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Project-04-basierte App vor dem Upgrade für Gesprächshistorie. | Ausgangspunkt, wenn du die drei Varianten selbst erneut ausführen willst. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Ein Agent plant, implementiert und bewertet sich selbst. | Bewertung und Defektliste in [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md). |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Generator + Evaluator mit Revisionsnachweis. | Bewertung und Revisionsnotizen in [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md). |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planner + Generator + Evaluator mit Sprint Contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) und höhere Bewertungsnachweise in [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md). |

## Werkzeuge

- Claude Code oder Codex
- Git
- Node.js + Electron

## Harness-Mechanismus

Selbstverifikation + begründete Q&A + evidenzbasierter Abschluss
