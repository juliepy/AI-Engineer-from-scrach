# Skills

Dieses Verzeichnis enthält die mit dem Kurs ausgelieferten KI-Agenten-Skills. Skills sind eigenständige Prompt-Vorlagen, die KI-Coding-Agenten wie Claude Code, Codex, Cursor oder Windsurf laden können, um spezialisierte Aufgaben zu erledigen.

## harness-creator

Ein produktionsreifer harness-engineering-Skill für KI-Coding-Agenten. Er hilft beim Erstellen, Bewerten und Verbessern der fünf zentralen harness-Subsysteme: Anweisungen, Zustand, Verifikation, Scope und Session-Lebenszyklus.

### Was er tut

- **Harnesses von Grund auf erstellen** — AGENTS.md, Feature-Listen, Verifikations-Workflows
- **Bestehende Harnesses verbessern** — Bewertung der fünf Subsysteme mit priorisierten Verbesserungen
- **Session-Kontinuität entwerfen** — persistente Erinnerung, Fortschrittsverfolgung, Handoff-Prozeduren
- **Produktionsmuster anwenden** — Memory, Context Engineering, Tool-Sicherheit, Multi-Agent-Koordination

### Schnellstart

Die Skill-Dateien liegen im Repository unter [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Um ihn mit Claude Code zu verwenden, kopiere das Verzeichnis `harness-creator/` in den Skill-Pfad deines Projekts oder zeige deinen Agenten direkt auf die Datei SKILL.md.

### Referenzmuster

Der Skill enthält 7 fokussierte Referenzdokumente:

| Muster | Wann verwenden |
|---------|----------------|
| Memory Persistence | Der Agent vergisst zwischen Sessions |
| Skill Runtime | Wiederverwendbare Workflows als Skills paketieren |
| Context Engineering | Kontextbudget, JIT-Laden |
| Tool Registry | Tool-Sicherheit, Nebenläufigkeitskontrolle |
| Multi-Agent Coordination | Parallelität, Spezialisierungs-Workflows |
| Lifecycle & Bootstrap | Hooks, Hintergrundaufgaben, Initialisierung |
| Gotchas | 15 nicht offensichtliche Fehlermodi mit Lösungen |

### Vorlagen

Der Skill enthält sofort nutzbare Vorlagen:

- `agents.md` — AGENTS.md-Gerüst mit Arbeitsregeln
- `feature-list.json` — JSON Schema und Beispiel-Feature-Liste
- `init.sh` — Standard-Initialisierungsskript
- `progress.md` — Vorlage für Session-Fortschrittslogs
- `session-handoff.md` — Session-Handoff-Vorlage

### Scripts

Der Skill enthält außerdem reine Node.js-Scripts für Scaffold, Validierung, HTML-Assessment-Berichte und strukturelle Benchmark-Berichte.

### Wie dieser Skill gebaut wurde

`harness-creator` wurde mit der **skill-creator**-Methodik entwickelt, Anthropics offiziellem Meta-Skill zum Erstellen, Testen und Iterieren von Agenten-Skills. skill-creator bietet einen strukturierten Workflow aus Entwurf → Test → Bewertung → Iteration mit Eval-Runnern, Gradern und Benchmark-Viewer.

- **skill-creator Quelle**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Claude Code Skills Docs**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
