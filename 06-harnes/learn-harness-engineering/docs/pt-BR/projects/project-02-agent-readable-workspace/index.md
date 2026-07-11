[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> Aulas relacionadas: [Aula 03. Faça do repositório sua única fonte de verdade.](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [Aula 04. Dividir instruções entre arquivos.](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> Arquivos de template: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Projeto 02. Torne o Projeto Legível e Continue de Onde Você Parou

## O Que Você Vai Fazer

Adicione “legibilidade” ao repositório para que um novo agente consiga entender rapidamente a estrutura do projeto, identificar o progresso atual e continuar o trabalho. Especificamente: implemente importação de documentos, visualização de detalhes do documento e persistência local, concluindo tudo ao longo de duas sessões.

Você executará isso duas vezes utilizando os diretórios versionados: primeiro com o workspace inicial mais simples e sem `session-handoff.md`; depois utilizando a estrutura da solução, que possui `ARCHITECTURE.md`, `PRODUCT.md` e `session-handoff.md` expandidos.

## Ferramentas

- Claude Code ou Codex
- Git
- Node.js + Electron

## Mecanismo do Harness

Workspace legível por agentes + arquivos persistentes de estado

## Utilize o Projeto Versionado

Caminho do repositório: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| Diretório | O que contém | O que comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Código do Projeto 01 com importação de documentos, visualização de detalhes e persistência ainda incompletos. A documentação existe, mas é intencionalmente mais enxuta, e não há `session-handoff.md`. | Quanto trabalho de redescoberta uma segunda sessão do agente precisa realizar. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | O mesmo recorte concluído, com documentação expandida em [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) (além de [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) e [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md)). | Verificar se uma nova sessão consegue retomar o trabalho a partir do estado do repositório sem necessidade de contexto verbal. |

As funcionalidades do produto são: importação de documentos, carregamento completo de detalhes/conteúdo do documento e persistência após reiniciar o aplicativo. A funcionalidade do harness é o workspace legível para handoff.