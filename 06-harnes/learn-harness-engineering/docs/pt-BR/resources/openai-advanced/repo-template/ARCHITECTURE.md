# ARCHITECTURE.md

Este arquivo é o mapa de alto nível do sistema. Ele deve permanecer conciso e apontar para documentos mais profundos quando necessário.

## Formato do Sistema (System Shape)

- Produto: `[substitua pelo nome do produto]`
- Fluxo de trabalho principal do usuário: `[substitua pelo fluxo de trabalho principal]`
- Superfícies de runtime: `[desktop / web / cli / serviços / workers]`
- Fonte da verdade para o comportamento do produto: `docs/product-specs/`

## Mapa de Domínio

| Domínio | Propósito | Principais Pontos de Entrada | Especificação Relacionada |
|--------|---------|----------------------|--------------|
| `[dominio-a]` | `[o que ele possui]` | `[módulos / rotas / comandos]` | `[caminho da especificação]` |
| `[dominio-b]` | `[o que ele possui]` | `[módulos / rotas / comandos]` | `[caminho da especificação]` |

## Modelo de Camadas

Use um modelo direcional fixo para que os agentes não inventem arquiteturas ad hoc:

`Tipos -> Configuração -> Repositório -> Serviço -> Runtime -> UI`

Preocupações transversais (cross-cutting concerns) devem entrar por meio de limites explícitos de provedores ou adaptadores, em vez de acessar as camadas diretamente.

## Regras de Dependência Rígidas

- Camadas inferiores não devem depender de camadas superiores.
- A UI não deve ignorar os contratos de runtime ou de serviço.
- O acesso a dados deve entrar por meio de repositórios ou adaptadores equivalentes.
- Utilitários compartilhados devem permanecer genéricos e não devem acumular lógica de domínio.
- Novas dependências devem ser justificadas no plano correspondente ou no documento de design.

## Interfaces Transversais

| Preocupação | Limite Aprovado | Notas |
|--------|-------------------|-------|
| Logging e tracing | `[caminho do provedor / utilitário]` | `[apenas estruturado, sem uso ad hoc de console]` |
| Autenticação | `[caminho do provedor]` | `[regras de token/sessão]` |
| APIs Externas | `[caminho do cliente ou provedor]` | `[orientação de limite de taxa / retentativa]` |
| Feature flags | `[limite da flag]` | `[propriedade]` |

## Pontos Críticos Atuais (Hot Spots)

- `[área mais difícil para os agentes alterarem com segurança]`
- `[área com limites fracos ou testes frágeis]`

## Checklist de Mudança

Ao tocar em código relevante para a arquitetura:

1. Atualize este arquivo se o mapa de domínio ou os limites permitidos mudarem.
2. Atualize o documento de design relacionado em `docs/design-docs/` se a justificativa mudar.
3. Adicione ou atualize uma verificação executável se a regra deve ser aplicada mecanicamente.
