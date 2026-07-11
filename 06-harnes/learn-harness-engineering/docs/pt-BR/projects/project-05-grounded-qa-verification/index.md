[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Aulas relacionadas: [Aula 09. Impedir que os agentes declarem vitória prematuramente.](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Aula 10. Somente uma execução completa do pipeline conta como verificação real.](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Arquivos de template: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Projeto 05. Faça o Agente Verificar o Próprio Trabalho

## O Que Você Vai Fazer

Implemente separação de papéis — um gerador que implementa, um avaliador que revisa e, opcionalmente, um planejador. Execute o processo três vezes para medir o efeito de cada papel adicional.

Escolha uma melhoria significativa de funcionalidade (conversa multi-turno, redesign do painel de citações ou filtragem de documentos) e mantenha-a consistente em todas as execuções.

## Ferramentas

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mecanismo do Harness

Autoverificação + grounded Q&A + conclusão baseada em evidências

## Utilize o Projeto Versionado

Caminho do repositório: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Diretório | O que contém | O que comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Aplicação baseada no Projeto 04 antes da melhoria de histórico de conversas. | Ponto de partida caso você queira executar novamente as três variantes por conta própria. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Um único agente planeja, implementa e faz a própria revisão. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md) com nota 1.6/5 e defeitos listados. |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Gerador mais avaliador com evidências de revisão. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md) com nota 3.3/5 e observações de revisão. |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planejador mais gerador mais avaliador. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) e [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md) com nota 4.9/5. |

A funcionalidade versionada é o histórico de conversas de perguntas e respostas multi-turno. Mantenha essa funcionalidade constante em todas as três variantes para que a única variável seja a separação de papéis.