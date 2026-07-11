[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> Zugehörige Lektionen: [Lektion 01. Starke Modelle bedeuten keine zuverlässige Ausführung](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [Lektion 02. Was harness wirklich bedeutet](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Vorlagendateien: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/de/resources/templates/)

# Projekt 01. Nur Prompt vs Regeln zuerst: Wie groß ist der Unterschied?

## Was du tust

Baue das minimale Gerüst einer Electron-Wissensdatenbank-App: ein Fenster mit Dokumentliste links, Q&A-Panel rechts und lokalem Datenverzeichnis. Die Aufgabe selbst ist nicht komplex. Komplex ist, wie du den Agenten dazu bringst, sie zuverlässig abzuschließen.

Du führst sie zweimal aus. Beim ersten Mal: nur ein Prompt, keine Vorbereitung. Beim zweiten Mal: `AGENTS.md`, `init.sh` und `feature_list.json` liegen bereits im Repository. Danach vergleichst du.

Dieses Kursbeispiel nutzt eine kurze Wiederentdeckungs-/Vorbereitungsphase als Beispiel, nicht als fest gemessenes Ergebnis.

## Werkzeuge

- Claude Code oder Codex (wähle eines und nutze es für beide Läufe)
- Git (Branches verwalten und vergleichen)
- Node.js + Electron (Projektstack)
- Ein Timer (Dauer jedes Laufs erfassen)

## Harness-Mechanismus

Minimaler harness: `AGENTS.md` + `init.sh` + `feature_list.json`

## Nutze das eingecheckte Projekt

Repository-Pfad: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Verzeichnis | Inhalt | Nutzung/Vergleich |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | Weak-Harness-Lauf. Enthält nur [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) als Aufgabenbeschreibung und keine `AGENTS.md` oder `feature_list.json`. | Gib den Prompt an deinen Agenten und miss, was ohne zusätzliche Struktur fertig wird. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | Gleicher Produktslice mit expliziten Harness-Artefakten: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json) und [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | Vergleiche, wie Regeln und Verifikation die gleiche Aufgabe konkret und überprüfbar machen. |

Die vier konkreten Features sind Fensterstart, Dokumentliste, Frage-Panel und das lokale Datenverzeichnis. Schau in `solution/feature_list.json` für die erwartete Evidence pro Feature.
