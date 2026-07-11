# CLAUDE.md

Você está trabalhando em um repositório projetado para trabalhos de implementação de longa duração. Priorize a conclusão confiável, a continuidade entre as sessões e a verificação explícita em vez da velocidade.

## Ciclo de Operação (Operating Loop)

No início de cada sessão:

1. Execute `pwd` e confirme que você está na raiz esperada do repositório.
2. Leia `claude-progress.md`.
3. Leia `feature_list.json`.
4. Revise os commits recentes com `git log --oneline -5`.
5. Execute `./init.sh`.
6. Verifique se o caminho básico de smoke test ou end-to-end já está quebrado.

Em seguida, selecione exatamente um recurso inacabado e trabalhe apenas nesse recurso até verificá-lo ou documentar por que ele está bloqueado.

## Regras

- Apenas um recurso ativo por vez.
- Não declare conclusão sem evidências executáveis.
- Não reescreva a lista de recursos para ocultar trabalho inacabado.
- Não remova ou enfraqueça testes apenas para fazer a tarefa parecer concluída.
- Use os artefatos do repositório como o sistema de registro.

## Arquivos Obrigatórios

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- `session-handoff.md` quando uma entrega compacta for útil

## Portão de Conclusão (Completion Gate)

Um recurso só pode passar para o estado `passing` após a verificação exigida ter sucesso e o resultado ser registrado.

## Antes de Parar

1. Atualize o log de progresso.
2. Atualize o estado do recurso.
3. Registre o que ainda está quebrado ou não verificado.
4. Faça o commit assim que o repositório estiver seguro para ser retomado.
5. Deixe um caminho de reinicialização limpo para a próxima sessão.
