# SOP: Arquitetura de Domínio em Camadas (Layered Domain Architecture)

Use este SOP quando o agente continuar violando limites, duplicando lógica entre camadas ou produzindo código que se torna difícil de revisar após algumas sessões.

## Objetivo

Tornar os limites de domínio explícitos o suficiente para que os agentes possam se mover rapidamente sem degradar a estrutura silenciosamente.

## Modelo de Destino (Target Model)

Dentro de um domínio de negócio, prefira este fluxo direcional:

`Tipos -> Configuração -> Repositório -> Serviço -> Runtime -> UI`

Preocupações transversais (cross-cutting concerns) devem entrar por meio de provedores ou adaptadores explícitos. Utilitários compartilhados permanecem fora do domínio e não devem acumular lógica de domínio.

## Checklist de Configuração

- Defina os domínios atuais em `ARCHITECTURE.md`.
- Escreva as direções de dependência permitidas em `ARCHITECTURE.md`.
- Registre interfaces transversais, como autenticação, telemetria e APIs externas.
- Adicione uma nota curta para a violação de limite atual mais difícil.
- Decida o que deve ser aplicado mecanicamente por lint, testes ou scripts.

## SOP de Execução

1. Mapeie a base de código em domínios antes de tocar no estilo de implementação.
2. Para cada domínio, identifique a sequência de camadas permitida.
3. Identifique todas as preocupações transversais e roteie-as através de provedores ou adaptadores.
4. Mova a lógica compartilhada ambígua para o domínio proprietário ou para utilitários verdadeiramente genéricos.
5. Documente as regras em `ARCHITECTURE.md`.
6. Adicione uma salvaguarda executável para a violação de maior custo.
7. Atualize a pontuação de qualidade após a alteração.

## Definição de Concluído (Definition Of Done)

- Um novo agente pode dizer qual camada é proprietária de uma mudança.
- O código de UI não acessa mais o repositório ou efeitos colaterais externos diretamente.
- Preocupações transversais têm pontos de entrada nomeados.
- Pelo menos um limite importante é aplicado mecanicamente.

## Artefatos do Repositório a Atualizar

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- `docs/design-docs/` quando a justificativa mudar.
- `docs/PLANS.md` ou o plano de execução ativo.
