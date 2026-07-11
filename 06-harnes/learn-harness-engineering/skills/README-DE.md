<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills

Dieses Verzeichnis enthält wiederverwendbare AI agent skills für das Projekt Learn Harness Engineering. Jeder skill ist eine eigenständige Prompt-Vorlage, die von Coding Agents wie Claude Code, Codex, Cursor oder Windsurf geladen werden kann.

## Verfügbare Skills

### harness-creator

Production-orientierter Harness-Engineering-Skill für AI coding agents. Er hilft beim Erstellen, Bewerten und Verbessern von Agent-Harness-Dateien wie AGENTS.md, Feature-Listen, Verification Workflows und Mechanismen für Session Continuity.

- **7 Referenzmuster**: Memory Persistence, Skill Runtime, Context Engineering, Tool Registry, Multi-Agent Coordination, Lifecycle & Bootstrap, Gotchas
- **Templates**: AGENTS.md/CLAUDE.md, feature-list.json, init.sh, progress.md, session-handoff.md
- **Scripts**: Scaffold, Validierung, HTML-Assessment und struktureller Benchmark
- **10 integrierte Eval-Testfälle**

Siehe [harness-creator/README.md](harness-creator/README.md) für die vollständige Dokumentation.

## Wie harness-creator erstellt wurde

`harness-creator` wurde mit der **skill-creator**-Methodik entwickelt, Anthropic's offiziellem meta-skill zum Erstellen, Testen und Iterieren von Agent Skills im Ablauf draft → test → evaluate → iterate.

## Wie Skills funktionieren

Jeder skill folgt einer Standardstruktur:

1. **SKILL.md** — Einstiegspunkt mit YAML frontmatter und Markdown-Anweisungen für den Agent.
2. **references/** — Zusätzliche Dokumentation, die bei Bedarf in den Kontext geladen wird.
3. **templates/** — Startvorlagen, die der skill erzeugen kann.

Skills verwenden progressive disclosure: Der Agent sieht zunächst nur Name und Beschreibung, lädt bei Auslösung die vollständige SKILL.md und liest gebündelte Ressourcen nur bei Bedarf.

## Sicherheit

Alle Dateien in diesem Verzeichnis wurden geprüft:

- Keine Backdoors, versteckten URLs oder codierten Payloads
- Keine Datenexfiltration oder hardcodierten Zugangsdaten
- Keine Command-Injection-Schwachstellen
- Scripts verwenden nur eingebaute Node.js-Module
- Generiertes `init.sh` führt erkannte Projekt-Verifikationsbefehle aus

## Lizenz

MIT
