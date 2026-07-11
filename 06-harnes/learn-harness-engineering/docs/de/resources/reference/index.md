# Deutsche Referenz

Diese Notizen erklären, wie man die Templates als funktionierenden Harness statt als
lose Dateisammlung verwendet.

## Interne Referenznotizen

- [`method-map.md`](./method-map.md): ordnet häufige langlaufende Fehlermodi dem
  Artefakt oder der Policy zu, die sie zuerst adressiert
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md): was der
  Initializer hinterlassen sollte, bevor Feature-Arbeit beginnt
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md): fester
  Session-Start-Flow für spätere Coding-Läufe
- [`prompt-calibration.md`](./prompt-calibration.md): wie man Root-Instruktionen
  scharf hält, ohne sie aufzublähen und brüchig zu machen

## Primäre Artikel

Diese Liste ist bewusst eng. Ein Harness bedeutet das Ausführungssystem rund um
das Modell: die Agent-Schleife, Tool-Ausführung, Sandboxing, Zustand, Kontext,
Verifikation, Terminierung, Orchestrierung und Observabilität. Allgemeine Prompt-
Engineering- oder breite Agent-Framework-Artikel gehören nicht in die primäre Liste.

Die ursprünglichen drei Artikel bleiben das Rückgrat des Kurses:

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11): agent-first Repositories, repo-lokaler Kontext, Custom-Linting und strukturelle Guardrails.
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26): Initializer-Agent, Coding-Agent, Feature-Liste, Fortschrittslog und Handoff über Kontextfenster.
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24): Planner-/Generator-/Evaluator-Rollen, Kontext-Resets, Harness-Vereinfachung und veraltete Annahmen.

## 2026 Erweiterte Referenzen

Dies sind keine Kernquellen des Kurses, aber nützlich beim Entwurf spezifischer
Harness-Module.

- [OpenAI: Unlocking the Codex harness](https://openai.com/index/unlocking-the-codex-harness/) (2026-02-04)
- [OpenAI Developers: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) (2026-02-23)
- [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (2026-04-15)
- [OpenAI: An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/) (2026-04-27)
- [Anthropic: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05)
- [Anthropic: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents) (2026-04-08)
- [Anthropic: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) (2026-04-23)
- [LangChain: Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents) (2026-01-28)
- [LangChain: Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models) (2026-04-29)
- [Microsoft: Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/) (2026-03-12)

## Empfohlene Lesereihenfolge

1. `method-map.md`
2. `initializer-agent-playbook.md`
3. `coding-agent-startup-flow.md`
4. `prompt-calibration.md`
5. OpenAI Harness Engineering
6. Anthropic Effective Harnesses
7. Anthropic Harness Design
