[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> Aulas relacionadas: [Aula 01. Modelos robustos não garantem execução confiável.](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [Aula 02. O que significa, de fato, arnês.](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Arquivos de template: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Projeto 01. Apenas Prompt vs. Regras Primeiro: Quanta Diferença Isso Faz

## O Que Você Vai Fazer

Construa um shell mínimo de aplicativo Electron para base de conhecimento — uma janela com uma lista de documentos à esquerda, um painel de perguntas e respostas à direita e um diretório local de dados. A tarefa em si não é complexa. O que é complexo é como você faz o agente concluí-la.

Você executará isso duas vezes. Na primeira vez: apenas um prompt, sem preparação. Na segunda vez: `AGENTS.md`, `init.sh` e `feature_list.json` previamente adicionados ao repositório. Depois, compare os resultados.

O cenário deste curso utiliza um curto intervalo de redescoberta/preparação como exemplo, não como um resultado fixo e mensurável.

## Ferramentas

- Claude Code ou Codex (escolha um e utilize o mesmo nas duas execuções)
- Git (para gerenciar branches e comparar resultados)
- Node.js + Electron (stack do projeto)
- Um cronômetro (registre a duração de cada execução)

## Mecanismo do Harness

Harness mínimo: `AGENTS.md` + `init.sh` + `feature_list.json`

## Utilize o Projeto Versionado

Caminho do repositório: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Diretório | O que contém | Como utilizar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | A execução com harness fraco. Contém apenas [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) como descrição da tarefa e não possui `AGENTS.md` nem `feature_list.json`. | Entregue o prompt ao seu agente de programação e meça o que ele consegue concluir sem estrutura adicional. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | O mesmo recorte de produto com artefatos explícitos de harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json) e [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | Compare como a mesma tarefa se torna concreta através de regras e evidências de verificação. |

As quatro funcionalidades concretas são: abertura da janela, lista de documentos, painel de perguntas e respostas, e criação do diretório local de dados. Inspecione `solution/feature_list.json` para entender as evidências esperadas para cada funcionalidade.