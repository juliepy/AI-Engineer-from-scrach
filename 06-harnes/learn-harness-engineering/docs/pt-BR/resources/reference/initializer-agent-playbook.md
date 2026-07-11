# Guia do Agente Inicializador (Initializer Agent Playbook)

Use este guia para a primeira sessão séria em um repositório, antes do início do trabalho incremental nos recursos.

## Objetivo

Criar uma superfície operacional estável para que as sessões posteriores possam implementar o comportamento sem precisar redescobrir comandos de inicialização, o status atual ou os limites das tarefas.

## Entregas Obrigatórias

O inicializador deve deixar para trás pelo menos estes artefatos:

- um arquivo de instrução de raiz, como `AGENTS.md` ou `CLAUDE.md`.
- uma superfície de recursos legível por máquina, como `feature_list.json`.
- um artefato de progresso durável, como `claude-progress.md`.
- um auxiliar de inicialização padrão, como `init.sh`.
- um commit inicial seguro que capture a estrutura base.

## Checklist

1. Definir o caminho de inicialização padrão.
2. Definir o caminho de verificação padrão.
3. Criar o log de progresso e registrar o estado inicial.
4. Decompor o trabalho em recursos explícitos com status.
5. Criar o primeiro commit de base limpa.

## Teste de Sucesso

Uma nova sessão sem contexto de chat anterior deve ser capaz de responder:

- o que este repositório faz.
- como iniciá-lo.
- como verificá-lo.
- o que está inacabado.
- qual é o próximo melhor passo.
