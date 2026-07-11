# QUALITY_SCORE.md

Este documento rastreia se o repositório está ficando mais forte ou mais fraco ao longo do tempo.

## Escala de Avaliação

- `A`: verificado, legível, estável, limites aplicados.
- `B`: funcionando com pequenas lacunas.
- `C`: funcionando parcialmente, confusão ou instabilidade notável.
- `D`: quebrado, inseguro ou estruturalmente obscuro.

## Domínios de Produto

| Domínio | Nota | Verificação | Legibilidade para Agente | Estabilidade de Teste | Lacunas Principais | Última Atualização |
|--------|-------|-------------|-------------------------|----------------------|-------------------|-------------------|
| `[dominio-a]` | - | - | - | - | - | - |
| `[dominio-b]` | - | - | - | - | - | - |
| `[dominio-c]` | - | - | - | - | - | - |

## Camadas Arquitetônicas

| Camada | Nota | Aplicação de Limites | Legibilidade para Agente | Lacunas Principais | Última Atualização |
|-------|-------|---------------------|-------------------------|-------------------|-------------------|
| Tipos | - | - | - | - | - |
| Serviços | - | - | - | - | - |
| Runtime | - | - | - | - | - |
| UI | - | - | - | - | - |

## Instantâneos de Benchmark (Benchmark Snapshots)

| Data | Variante do Harness | Taxa de Conclusão | Retentativas | Defeitos Antes da Revisão | Notas |
|------|-----------------|----------------|--------|-----------------------|------|
| AAAA-MM-DD | `[base / melhorado / simplificado]` | - | - | - | - |

## Log de Simplificação

| Data | Componente Removido | Resultado | Decisão |
|------|-------------------|---------|----------|
| AAAA-MM-DD | `[componente]` | `[degradado / inalterado]` | `[restaurar / manter removido]` |
