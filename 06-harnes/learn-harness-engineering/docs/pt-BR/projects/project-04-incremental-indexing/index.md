[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Aulas relacionadas: [Aula 07. Defina limites de tarefas claros para os agentes.](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Aula 08. Use listas de características para restringir o que o agente faz.](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Arquivos de template: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Projeto 04. Utilize Feedback em Runtime para Corrigir o Comportamento do Agente

## O Que Você Vai Fazer

Adicione observabilidade em runtime (logs de inicialização, logs de importação/indexação e estados de erro) e restrições arquiteturais para evitar violações entre camadas. Insira um bug em runtime para que o agente o corrija.

Você irá comparar o starter e a solution versionados: o starter possui diagnósticos fracos e não possui script de verificação arquitetural, enquanto a solution adiciona logs estruturados, verificações de limites arquiteturais e a correção do bug.

## Ferramentas

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mecanismo do Harness

Feedback em runtime + controle de escopo + indexação incremental

## Utilize o Projeto Versionado

Caminho do repositório: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Diretório | O que contém | O que comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Código do Projeto 03 com diagnósticos fracos. Um defeito proposital na indexação pode fazer o chunking de arquivos grandes falhar, e não existe script de verificação arquitetural. | Quanto tempo o agente leva para encontrar a causa raiz sem sinais de runtime. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Logger estruturado, documentação e script de limites arquiteturais, lógica de chunking corrigida e [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Verificar se logs e verificações arquiteturais tornam a correção mais rápida e menos invasiva. |

Os arquivos concretos para inspecionar são [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts),
[`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh),
[`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md) e
[`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).