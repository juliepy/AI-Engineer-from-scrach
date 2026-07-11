# AGENTS.md

Este repositório é otimizado para trabalhos de agentes de codificação de longa duração. Mantenha este arquivo curto. Use-o como a camada de roteamento para os documentos de sistema de registro, não como um depósito gigante de instruções.

## Fluxo de Trabalho de Inicialização (Startup Workflow)

Antes de alterar o código:

1. Confirme a raiz do repositório com `pwd`.
2. Leia `ARCHITECTURE.md` para conhecer o mapa atual do sistema e as regras de dependência rígidas.
3. Leia `docs/QUALITY_SCORE.md` para ver quais domínios ou camadas estão mais fracos.
4. Leia `docs/PLANS.md` e, em seguida, abra o plano ativo no qual você está trabalhando.
5. Leia a especificação de produto relevante em `docs/product-specs/`.
6. Execute o caminho padrão de inicialização e verificação para este repositório.
7. Se a verificação básica estiver falhando, repare a base antes de adicionar escopo.

## Mapa de Roteamento

- `ARCHITECTURE.md`: mapa de domínio, modelo de camadas, regras de dependência.
- `docs/design-docs/index.md`: decisões de design e crenças fundamentais.
- `docs/product-specs/index.md`: comportamentos atuais do produto e metas de aceitação.
- `docs/PLANS.md`: ciclo de vida do plano e política do plano de execução.
- `docs/QUALITY_SCORE.md`: saúde do domínio de produto e da camada.
- `docs/RELIABILITY.md`: sinais de runtime, benchmarks e expectativas de reinicialização.
- `docs/SECURITY.md`: segredos, sandbox, dados e regras de ações externas.
- `docs/FRONTEND.md`: restrições de UI, regras do design system, verificações de acessibilidade.

## Contrato de Trabalho

- Trabalhe em um plano delimitado ou fatia de recurso por vez.
- Não marque o trabalho como concluído apenas pela inspeção do código; evidências executáveis são obrigatórias.
- Se você alterar o comportamento, atualize os documentos de produto, plano ou confiabilidade correspondentes na mesma sessão.
- Se você vir feedbacks de revisão repetidos, promova-os para uma regra mecânica, verificação ou linter, em vez de reexplicá-los no chat.
- Mantenha o material gerado em `docs/generated/` e as referências de origem em `docs/references/`.
- Prefira adicionar documentos pequenos e atuais em vez de aumentar este arquivo.

## Definição de Concluído (Definition Of Done)

Uma alteração só é considerada concluída quando todos os itens a seguir forem verdadeiros:

- o comportamento pretendido foi implementado.
- a verificação exigida foi realmente executada.
- a evidência está vinculada ao plano relevante ou documento de qualidade.
- os documentos afetados permanecem atualizados.
- o repositório pode ser reiniciado de forma limpa a partir do caminho de inicialização padrão.

## Fim de Sessão

Antes de encerrar uma sessão:

1. Atualize o plano de execução ativo.
2. Atualize `docs/QUALITY_SCORE.md` se algum domínio ou camada mudar significativamente.
3. Registre novas dívidas técnicas em `docs/exec-plans/tech-debt-tracker.md` se você as adiou.
4. Mova os planos finalizados para `docs/exec-plans/completed/` quando apropriado.
5. Deixe o repositório em um estado reinicializável com uma próxima ação clara.
