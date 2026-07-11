[中文版本 →](../../../zh/projects/project-06-runtime-observability-and-debugging/)

> Aulas relacionadas: [Aula 11. Tornar o tempo de execução do agente observável.](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [Aula 12. Transição de informações clara e objetiva ao final de cada sessão.](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> Arquivos de template: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Projeto 06. Construa um Harness Completo para Agentes (Capstone)

## O Que Você Vai Fazer

Este é o projeto final (capstone). Reúna tudo o que foi aprendido nos cinco primeiros projetos, execute um benchmark completo e depois faça uma etapa de limpeza para verificar se a qualidade é sustentável ao longo do tempo.

Utilize um conjunto fixo de tarefas com múltiplas funcionalidades cobrindo todo o recorte do produto: importação de documentos, indexação, perguntas e respostas baseadas em citações, observabilidade em runtime e um estado de repositório legível e reinicializável. Primeiro execute com um harness fraco como baseline, depois com seu harness mais robusto e, por fim, faça uma limpeza e uma nova execução. Depois disso, realize um experimento de ablação do harness — remova um componente por vez para descobrir quais realmente fazem diferença.

## Ferramentas

- Claude Code ou Codex
- Git
- Node.js + Electron
- Template de documento de qualidade
- Rubrica de avaliação
- Todos os componentes de harness acumulados nos cinco primeiros projetos

## Mecanismo do Harness

Harness completo: todos os mecanismos + observabilidade + estudo de ablação

## Utilize o Projeto Versionado

Caminho do repositório: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| Diretório | O que contém | O que comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | Código do produto praticamente completo, mas com uma superfície de harness intencionalmente fraca: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md) básico, sem `feature_list.json`, sem `session-handoff.md` e sem checklist de estado limpo. | Observações manuais da baseline com harness fraco. O starter intencionalmente não inclui scripts de benchmark. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | Superfície completa de harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), documentos de qualidade/avaliação, além de scripts de benchmark e limpeza. | Execute [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) e [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh), depois compare as evidências documentadas de qualidade. |

Diferente dos projetos anteriores, o starter do capstone não possui principalmente funcionalidades do produto faltando. A principal lacuna está no harness operacional ao redor da aplicação.