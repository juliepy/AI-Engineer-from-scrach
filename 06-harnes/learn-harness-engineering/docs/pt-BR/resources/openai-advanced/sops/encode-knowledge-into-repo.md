# SOP: Codificar Conhecimento Não Visto no Repositório

Use este SOP quando contextos importantes ainda residirem no Google Docs, threads de chat, tickets ou na cabeça das pessoas.

## Objetivo

Tornar o conhecimento invisível para o agente detectável na base de código, para que uma nova sessão possa agir sobre ele sem depender de conversas anteriores.

## Sinais de Alerta (Trigger Signals)

- O agente continua perguntando como o sistema funciona.
- Humanos dizem "decidimos isso no Slack" ou "siga o que X disse na semana passada".
- As revisões fazem referência a regras de produto ou segurança que não estão escritas no repositório.
- Novas sessões repetem o trabalho de descoberta que já deveria estar resolvido.

## SOP de Execução

1. Liste as fontes de conhecimento invisíveis: documentos, chats, regras tácitas da equipe, decisões verbais.
2. Para cada fonte, pergunte: isso é arquitetura, comportamento de produto, política de segurança, expectativa de confiabilidade, contexto de plano ou material de referência?
3. Codifique-o no artefato de repositório correspondente:
   - arquitetura -> `ARCHITECTURE.md`
   - comportamento de produto -> `docs/product-specs/`
   - justificativa de design -> `docs/design-docs/`
   - estado de execução -> `docs/exec-plans/`
   - referências externas repetidas -> `docs/references/`
   - expectativas de qualidade ou confiabilidade -> `docs/QUALITY_SCORE.md` ou `docs/RELIABILITY.md`
4. Substitua declarações vagas por uma redação operacionalmente útil.
5. Remova ou descontinue cópias obsoletas para que o repositório mantenha uma única verdade detectável.

## Boas Regras de Codificação

- Escreva para a detectabilidade, não para a completude literária.
- Prefira documentos curtos com nomes de arquivos claros.
- Vincule artefatos relacionados entre si.
- Armazene regras duráveis, não transcrições de reuniões.
- Atualize o repositório na mesma sessão em que a decisão for tomada.

## Definição de Concluído (Definition Of Done)

- Um novo agente pode descobrir a regra relevante sem perguntar a um humano.
- O mesmo fato não está espalhado por vários arquivos contraditórios.
- O novo artefato vive próximo ao código ou fluxo de trabalho que ele governa.
