# Pacote Avançado da OpenAI (OpenAI Advanced Pack)

Esta pasta empacota o formato de repositório mais opinativo descrito no artigo da OpenAI "Engenharia de Harness: alavancando o Codex em um mundo focado em agentes" em arquivos iniciais prontos para copiar.

Use este pacote quando o harness mínimo não for mais suficiente e seu repositório agora precisar de:

- um `AGENTS.md` curto no estilo de roteamento.
- documentos duráveis de sistema de registro dentro do repositório.
- planos de execução ativos e concluídos.
- arquivos de política explícitos de produto, confiabilidade, segurança e frontend.
- pontuação de qualidade por domínio de produto e camada arquitetônica.
- pastas de material de referência amigáveis para modelos.
- procedimentos operacionais padrão (SOPs) para arquitetura, captura de conhecimento e validação em tempo de execução.

## Layout Inicial Incluído

O pacote inicial em [`repo-template/`](./repo-template/index.md) espelha a estrutura abaixo:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Como Adotá-lo

1. Comece pelo pacote mínimo se o seu repositório ainda for pequeno.
2. Copie os arquivos em [`repo-template/`](./repo-template/index.md) para o seu próprio repositório assim que precisar de uma estrutura mais forte.
3. Mantenha o `AGENTS.md` curto. Trate-o como um roteador para os documentos mais profundos, não como uma enciclopédia.
4. Atualize os documentos de qualidade, confiabilidade e planos como parte do trabalho normal, não como um dia separado de limpeza.
5. Mantenha artefatos gerados e referências externas explícitos para que os agentes possam encontrá-los sem depender do histórico do chat.

## Biblioteca de SOPs (Procedimentos Operacionais Padrão)

A pasta [`sops/`](./sops/index.md) transforma os diagramas do artigo em procedimentos operacionais passo a passo:

- configuração de arquitetura de domínio em camadas.
- codificar conhecimento não visto no repositório.
- pilha de observabilidade local e fluxo de trabalho de loop de feedback.
- loop de validação do Chrome DevTools para trabalho de UI.

## Princípios de Design

- Ponto de entrada curto, documentos vinculados mais profundos.
- Repositório como sistema de registro.
- Verificações mecânicas vencem regras memorizadas.
- Planos e histórico de qualidade vivem ao lado do código.
- Limpeza e simplificação são responsabilidades de primeira classe.

Este pacote é intencionalmente opinativo, mas ainda deve ser adaptado ao seu projeto em vez de copiado cegamente.
