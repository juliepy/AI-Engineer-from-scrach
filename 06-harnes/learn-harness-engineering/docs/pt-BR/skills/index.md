# Skills (Habilidades)

Este diretório contém as habilidades (skills) integradas para agentes de IA que acompanham este curso. As habilidades são modelos de prompts autocontidos que podem ser carregados por agentes de codificação de IA (Claude Code, Codex, Cursor, Windsurf, etc.) para realizar tarefas especializadas.

## harness-creator

Uma habilidade de engenharia de harness de nível de produção para agentes de codificação de IA. Ela ajuda você a criar, avaliar e melhorar os cinco subsistemas principais do harness: instruções, estado, verificação, escopo e ciclo de vida da sessão.

### O Que Ela Faz

- **Cria harnesses do zero** — AGENTS.md, listas de recursos, fluxos de trabalho de verificação
- **Melhora harnesses existentes** — Avaliação de cinco subsistemas com melhorias priorizadas
- **Projeta continuidade de sessão** — Persistência de memória, rastreamento de progresso, procedimentos de entrega (handoff)
- **Aplica padrões de produção** — Memória, engenharia de contexto, segurança de ferramentas, coordenação multi-agente

### Início Rápido

Os arquivos da habilidade residem no repositório em [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Para usá-la com o Claude Code, copie o diretório `harness-creator/` para o caminho de habilidades do seu projeto ou aponte seu agente para o arquivo SKILL.md.

### Padrões de Referência

A habilidade inclui 7 documentos de referência focados:

| Padrão | Quando Usar |
|---------|-------------|
| Persistência de Memória | O agente esquece entre as sessões |
| Runtime de Habilidade | Empacotar fluxos de trabalho reutilizáveis como habilidades |
| Engenharia de Contexto | Gerenciamento de orçamento de contexto, carregamento JIT |
| Registro de Ferramentas | Segurança de ferramentas, controle de concorrência |
| Coordenação Multi-Agente | Paralelismo, fluxos de trabalho de especialização |
| Ciclo de Vida & Bootstrap | Hooks, tarefas em segundo plano, inicialização |
| Armadilhas (Gotchas) | 15 modos de falha não óbvios com correções |

### Modelos (Templates)

A habilidade agrupa modelos prontos para uso:

- `agents.md` — Estrutura AGENTS.md com regras de trabalho
- `feature-list.json` — Esquema JSON + exemplo de lista de recursos
- `init.sh` — Script de inicialização padrão
- `progress.md` — Modelo de log de progresso da sessão
- `session-handoff.md` — Modelo de entrega de sessão

### Scripts

A habilidade também inclui scripts Node.js simples para estruturação, validação, relatórios de avaliação em HTML e relatórios de benchmark estrutural.

### Como Esta Habilidade Foi Construída

O `harness-creator` foi desenvolvido usando a metodologia **skill-creator** — a meta-habilidade oficial da Anthropic para criar, testar e iterar em habilidades de agentes. O skill-creator fornece um fluxo de trabalho estruturado (rascunho → teste → avaliação → iteração) com executores de avaliação integrados, avaliadores e um visualizador de benchmark.

- **Fonte do skill-creator**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Documentação de habilidades do Claude Code**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
