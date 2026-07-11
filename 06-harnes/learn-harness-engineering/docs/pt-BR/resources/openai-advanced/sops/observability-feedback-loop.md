# SOP: Loop de Feedback de Observabilidade (Observability Feedback Loop)

Use este SOP quando a depuração for lenta, os agentes continuarem alegando sucesso sem evidências ou quando o comportamento em tempo de execução for mais difícil de inspecionar do que o próprio código.

## Objetivo

Fornecer ao agente um loop de feedback local sobre logs, métricas, rastreamentos e cargas de trabalho executáveis, para que ele possa raciocinar a partir da execução, e não apenas da inspeção do código.

## Pilha Mínima (Minimum Stack)

- a aplicação emite logs estruturados.
- a aplicação emite métricas e rastreamentos quando viável.
- camada local de distribuição (fan-out) ou coleta.
- interfaces de consulta para logs, métricas e rastreamentos.
- carga de trabalho ou jornada do usuário repetível para reexecutar após cada mudança.

## SOP de Execução

1. Defina as jornadas críticas (golden journeys) de tempo de execução que mais importam.
2. Adicione logs estruturados à inicialização e ao caminho crítico.
3. Adicione métricas para latência, contagem de falhas ou profundidade de fila onde for útil.
4. Adicione rastreamentos ou marcadores de tempo para fluxos lentos ou de várias etapas.
5. Torne os sinais consultáveis a partir do ambiente de desenvolvimento local.
6. Forneça ao agente uma carga de trabalho ou cenário repetível para reexecutar.
7. Exija o loop: consultar -> correlacionar -> raciocinar -> implementar -> reiniciar -> reexecutar -> verificar.

## Checklist de Sessão de Depuração

- O que falhou?
- Qual sinal prova a falha?
- Qual camada é proprietária da falha?
- O que mudou após a correção?
- O aplicativo reiniciou de forma limpa?
- A mesma carga de trabalho passou após a reexecução?

## Definição de Concluído (Definition Of Done)

- O agente pode explicar um modo de falha a partir de evidências em tempo de execução.
- A mesma carga de trabalho pode ser reexecutada após cada mudança.
- Reiniciar e reexecutar fazem parte do loop normal da tarefa.
- Os sinais de confiabilidade estão documentados em `docs/RELIABILITY.md`.
