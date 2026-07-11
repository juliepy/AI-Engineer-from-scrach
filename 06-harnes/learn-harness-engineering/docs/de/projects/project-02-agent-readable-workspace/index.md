[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> Zugehörige Lektionen: [Lektion 03. Mache das Repository zur einzigen Quelle der Wahrheit](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [Lektion 04. Teile Anweisungen auf mehrere Dateien auf](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> Vorlagendateien: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/de/resources/templates/)

# Projekt 02. Das Projekt lesbar machen und dort weiterarbeiten, wo du aufgehört hast

## Was du tust

Füge dem Repository "Lesbarkeit" hinzu, damit ein neuer Agent die Projektstruktur schnell versteht, den aktuellen Fortschritt kennt und Arbeit aufnehmen kann. Konkret: Implementiere Dokumentimport, Detailansicht und lokale Persistenz über zwei Sessions hinweg.

Du führst es zweimal aus: zuerst ohne Hilfe, dann mit bereits abgelegten `ARCHITECTURE.md`, `PRODUCT.md` und `session-handoff.md`.

## Nutze das eingecheckte Projekt

Repository-Pfad: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| Verzeichnis | Inhalt | Vergleichspunkt |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Code aus Project 01 mit noch unvollständigem Import, Detailansicht und Persistenz. Die Dokumentation ist vorhanden, aber dünner, und `session-handoff.md` fehlt. | Wie viel Kontext eine zweite Agent-Sitzung erneut herausfinden muss. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | Derselbe Produktschnitt ist fertig, mit Übergabedokumentation unter [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) sowie [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) und [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md). | Ob eine neue Sitzung nur aus dem Repository-Zustand weiterarbeiten kann. |

Die Produktfunktionen sind Dokumentimport, vollständiges Laden von Details/Inhalt und Persistenz nach Neustart. Die Harness-Funktion ist ein gut übergebbarer Workspace.

## Werkzeuge

- Claude Code oder Codex
- Git
- Node.js + Electron

## Harness-Mechanismus

Agent-lesbarer Workspace + persistente Zustandsdateien
