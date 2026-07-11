# Fluxo de Inicialização do Agente de Codificação (Coding Agent Startup Flow)

Use isto no início de cada sessão após a conclusão da inicialização.

## Modelo de Inicialização Fixo

1. Execute `pwd` e confirme a raiz do repositório.
2. Leia `claude-progress.md`.
3. Leia `feature_list.json`.
4. Revise os commits recentes com `git log --oneline -5`.
5. Execute `./init.sh`.
6. Execute um caminho básico de smoke test ou de ponta a ponta (end-to-end).
7. Se a base estiver quebrada, corrija isso primeiro.
8. Selecione o recurso inacabado de maior prioridade.
9. Trabalhe apenas nesse recurso até que ele seja verificado ou explicitamente bloqueado.

## Por que esta ordem importa

- `pwd` evita o trabalho acidental no diretório errado.
- Os arquivos de progresso e recursos recuperam o estado durável antes que novas edições comecem.
- Commits recentes explicam o que mudou mais recentemente.
- `init.sh` padroniza a inicialização em vez de depender da memória.
- A verificação básica captura estados iniciais quebrados antes que o novo trabalho os esconda.

## Espelhamento de Fim de Sessão

A mesma sessão deve terminar:

1. Registrando o progresso.
2. Atualizando o estado do recurso.
3. Escrevendo uma entrega (handoff), se necessário.
4. Commitando o trabalho seguro.
5. Deixando um caminho de reinicialização limpo.
