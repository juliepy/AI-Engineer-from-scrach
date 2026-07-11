[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> Aulas relacionadas: [Aula 05. Mantenha o contexto ativo ao longo das sessões.](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Aula 06. Inicializar antes de cada sessão do agente.](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Arquivos de template: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Projeto 03. Mantenha o Agente Trabalhando Entre Reinicializações de Sessão

## O Que Você Vai Fazer

Adicione controle de escopo e gates de verificação ao agente. Implemente fragmentação de documentos (chunking), extração de metadados, exibição do progresso de indexação e fluxo de perguntas e respostas baseado em citações. Utilize `feature_list.json` para acompanhar o status das funcionalidades — uma funcionalidade por vez, sem marcar como "pass" sem evidências de verificação.

Você irá comparar o starter e a solution versionados: o starter possui apenas a superfície inicial de rastreamento, enquanto a solution adiciona artefatos mais rigorosos de reinicialização e handoff em torno da mesma lista de funcionalidades.

## Ferramentas

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mecanismo do Harness

Log de progresso + handoff de sessão + continuidade entre múltiplas sessões + verificação de uma funcionalidade por vez

## Utilize o Projeto Versionado

Caminho do repositório: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Diretório | O que contém | O que comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Código do Projeto 02 com indexação e grounded QA ainda incompletos. Possui um [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json) inicial, mas não contém os artefatos finais de reinicialização/handoff. | Verificar se o agente se desvia entre múltiplas funcionalidades ou perde estado após uma reinicialização. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Implementação concluída de chunking, metadados, status de indexação e QA baseado em citações, além de [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md) e [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | Verificar se cada funcionalidade possui evidências concretas de verificação antes de ser marcada como concluída. |

Este projeto não é um exercício genérico de “múltiplas sessões”. A solução versionada corresponde a quatro funcionalidades específicas do produto: fragmentação de documentos, extração de metadados, interface de status de indexação e perguntas e respostas baseadas em contexto com citações.