# SOPs Avançados da OpenAI (OpenAI Advanced SOPs)

Estes SOPs (Procedimentos Operacionais Padrão) traduzem os padrões operacionais do artigo em guias de execução concretos que você pode seguir ou adaptar.

## SOPs Incluídos

- [`layered-domain-architecture.md`](./layered-domain-architecture.md): estabelece camadas explícitas e limites transversais.
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md): move o conhecimento invisível de chats, documentos e memória para arquivos locais do repositório.
- [`observability-feedback-loop.md`](./observability-feedback-loop.md): fornece aos agentes logs, métricas, rastreamentos e um loop de depuração repetível.
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md): utiliza automação de navegador e instantâneos para validar o comportamento da UI até que esteja limpo.

## Como Usá-los

1. Escolha o SOP que corresponde ao seu gargalo atual.
2. Use o checklist para configurar os artefatos ou ferramentas que faltam.
3. Codifique as regras resultantes em seus documentos copiados do `repo-template/`.
4. Converta comentários de revisão repetidos em verificações, scripts ou salvaguardas.

Estes documentos não devem ser seguidos cegamente. Eles servem para tornar o harness mais legível, aplicável e repetível.
