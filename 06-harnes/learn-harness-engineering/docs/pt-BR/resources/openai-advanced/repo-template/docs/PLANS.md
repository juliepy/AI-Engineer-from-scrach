# PLANS.md

Este arquivo define como os planos de execução são criados, atualizados, concluídos e arquivados.

## Quando um Plano é Necessário

Crie um plano de execução quando o trabalho:

- abranger mais de uma sessão.
- alterar mais de um subsistema.
- tiver verificação não trivial ou risco de lançamento.
- depender de decisões em aberto que devem ser registradas.

## Locais dos Planos

- `docs/exec-plans/active/`: planos que atualmente orientam o trabalho.
- `docs/exec-plans/completed/`: planos finalizados mantidos para contexto futuro do agente.
- `docs/exec-plans/tech-debt-tracker.md`: trabalho adiado e acompanhamentos (follow-ups).

## Seções Mínimas do Plano

- objetivo.
- escopo e fora de escopo.
- caminho de verificação.
- riscos e bloqueios.
- log de progresso.
- decisões em aberto.

## Regras Operacionais

- Um plano ativo deve ter uma etapa atual claramente definida e de responsabilidade única.
- Atualize o plano conforme o trabalho progride; não o trate como um texto estático.
- Se uma decisão alterar a direção da implementação, registre-a no plano.
- Mova os planos finalizados para `completed/` para que os agentes ainda possam descobrir o contexto anterior.
