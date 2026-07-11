# AGENTS.md

Este repositório foi projetado para trabalhos de agentes de codificação de longa duração. O objetivo não é maximizar a produção bruta de código. O objetivo é deixar o repositório em um estado onde a próxima sessão possa continuar sem adivinhações.

## Fluxo de Trabalho de Inicialização (Startup Workflow)

Antes de escrever o código:

1. Confirme o diretório de trabalho com `pwd`.
2. Leia `claude-progress.md` para saber o estado verificado mais recente e o próximo passo.
3. Leia `feature_list.json` e escolha o recurso inacabado de maior prioridade.
4. Revise os commits recentes com `git log --oneline -5`.
5. Execute `./init.sh`.
6. Execute a verificação básica (smoke test) ou de ponta a ponta (end-to-end) exigida antes de iniciar um novo trabalho.

Se a verificação básica já estiver falhando, corrija isso primeiro. Não acumule trabalho de novos recursos sobre um estado inicial quebrado.

## Regras de Trabalho

- Trabalhe em um recurso de cada vez.
- Não marque um recurso como concluído apenas porque o código foi adicionado.
- Mantenha as alterações dentro do escopo do recurso selecionado, a menos que um bloqueio force uma correção de suporte pontual.
- Não altere silenciosamente as regras de verificação durante a implementação.
- Prefira artefatos duráveis no repositório em vez de resumos de chat.

## Artefatos Obrigatórios

- `feature_list.json`: fonte da verdade para o estado do recurso.
- `claude-progress.md`: log da sessão e status verificado atual.
- `init.sh`: caminho padrão de inicialização e verificação.
- `session-handoff.md`: entrega compacta opcional para sessões maiores.

## Definição de Concluído (Definition Of Done)

Um recurso só é considerado concluído quando todos os itens a seguir forem verdadeiros:

- o comportamento pretendido foi implementado.
- a verificação exigida foi realmente executada.
- a evidência foi registrada em `feature_list.json` ou `claude-progress.md`.
- o repositório permanece reinicializável a partir do caminho de inicialização padrão.

## Fim de Sessão

Antes de encerrar uma sessão:

1. Atualize `claude-progress.md`.
2. Atualize `feature_list.json`.
3. Registre qualquer risco ou bloqueio não resolvido.
4. Faça o commit com uma mensagem descritiva assim que o trabalho estiver em um estado seguro.
5. Deixe o repositório limpo o suficiente para que a próxima sessão possa executar `./init.sh` imediatamente.
