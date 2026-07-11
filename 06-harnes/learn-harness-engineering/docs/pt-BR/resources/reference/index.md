# Referência em Português

Estas notas explicam como usar os modelos como um harness de trabalho, em vez de apenas uma pilha de arquivos soltos.

## Notas de Referência Interna

- [`method-map.md`](./method-map.md): mapeia modos de falha comuns em execuções de longa duração para o artefato ou política que os aborda primeiro.
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md): o que o inicializador deve deixar preparado antes do início do trabalho no recurso.
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md): fluxo fixo de início de sessão para execuções de codificação posteriores.
- [`prompt-calibration.md`](./prompt-calibration.md): como manter as instruções de raiz afiadas sem torná-las inchadas e frágeis.

## Artigos Principais

Esta lista é intencionalmente restrita. Um harness significa o sistema de execução em torno do modelo: o loop do agente, execução de ferramentas, sandboxing, estado, contexto, verificação, terminação, orquestração e observabilidade. Artigos gerais de engenharia de prompt ou de frameworks amplos de agentes não pertencem à lista principal.

Os três artigos originais continuam sendo a espinha dorsal do curso:

- [OpenAI: Engenharia de Harness: alavancando o Codex em um mundo focado em agentes](https://openai.com/index/harness-engineering/) (11-02-2026): repositórios focados em agentes, contexto local do repositório, linting personalizado e salvaguardas estruturais.
- [Anthropic: Harnesses eficazes para agentes de longa duração](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (26-11-2025): agente inicializador, agente de codificação, lista de recursos, log de progresso e entrega (handoff) entre janelas de contexto.
- [Anthropic: Design de Harness para desenvolvimento de aplicações de longa duração](https://www.anthropic.com/engineering/harness-design-long-running-apps) (24-03-2026): papéis de planejador / gerador / avaliador, resets de contexto, simplificação de harness e suposições obsoletas.

Apenas alguns artigos altamente relevantes de 2026 foram adicionados:

- [OpenAI: Desenrolando o loop do agente Codex](https://openai.com/index/unrolling-the-codex-agent-loop/) (23-01-2026): o harness de runtime do Codex, chamadas de ferramentas, crescimento de contexto e terminação do loop.
- [Anthropic: Desmistificando avaliações para agentes de IA](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (09-01-2026): avaliando o modelo e o harness juntos, e distinguindo harnesses de avaliação de harnesses de agentes.
- [LangChain: Melhorando Agentes Profundos com engenharia de harness](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (17-02-2026): mantendo o modelo fixo enquanto melhora prompts do sistema, ferramentas, middleware, rastreamento e autoverificação para mover um agente de codificação do Top 30 para o Top 5 no Terminal Bench 2.0.
- [Thoughtworks / Martin Fowler: Engenharia de harness para usuários de agentes de codificação](https://martinfowler.com/articles/harness-engineering.html) (02-04-2026): harnesses de usuários de agentes de codificação como guias de feedforward e sensores de feedback, com controles determinísticos e inferenciais.
- [Cursor: Melhorando continuamente nosso harness de agente](https://cursor.com/blog/continually-improving-agent-harness) (30-04-2026): tratando o harness como um sistema de produto continuamente aprimorado com avaliações offline, métricas online, taxonomia de erros de ferramentas, ajuste específico do modelo e troca de modelo durante o chat.

## Referências Estendidas de 2026

Estas não são fontes centrais do curso, mas são úteis ao projetar módulos específicos de harness. Esta seção mantém apenas fontes cujo corpo cobre diretamente o loop do agente, execução de ferramentas, gerenciamento de contexto, verificação, sandboxing, camadas de controle ou governança de regressão. Produtos puros de agentes, anúncios de plataformas, estudos de caso de equipes e benchmarks estão excluídos.

- [OpenAI: Desbloqueando o harness do Codex: como construímos o App Server](https://openai.com/index/unlocking-the-codex-harness/) (04-02-2026): o harness como um protocolo de App Server reutilizável com ciclo de vida de threads, retomada, fork, diffs e integrações de clientes.
- [OpenAI Developers: Execute tarefas de longo horizonte com o Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) (23-02-2026): memória durável do projeto, validação de marcos e exemplos de "quando está pronto" para tarefas de longa duração.
- [OpenAI: A próxima evolução do SDK de Agentes](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (15-04-2026): harnesses nativos do modelo, execução em sandbox e execução de arquivos/comandos.
- [OpenAI: Uma especificação de código aberto para orquestração do Codex: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/) (27-04-2026): transformando um rastreador de problemas ou quadro do Linear em um plano de controle multi-agente.
- [Anthropic: Construindo um compilador C com uma equipe de Claudes paralelos](https://www.anthropic.com/engineering/building-c-compiler) (05-02-2026): equipes de agentes paralelas, bloqueios de tarefas, sincronização git, isolamento de contêineres e loops autônomos.
- [Anthropic: Escalonando Agentes Gerenciados: Desacoplando o cérebro das mãos](https://www.anthropic.com/engineering/managed-agents) (08-04-2026): uma visão de meta-harness que separa sessão, harness e sandbox como interfaces intercambiáveis.
- [Anthropic: Uma atualização sobre relatórios recentes de qualidade do Claude Code](https://www.anthropic.com/engineering/april-23-postmortem) (23-04-2026): esforço de raciocínio, poda de contexto e prompts do sistema como mudanças de harness que precisam de governança de regressão.
- [LangChain: Gerenciamento de Contexto para Agentes Profundos](https://www.langchain.com/blog/context-management-for-deepagents) (28-01-2026): descarregamento do sistema de arquivos, truncamento de chamadas de ferramentas, sumarização e avaliações direcionadas para harnesses de gerenciamento de contexto.
- [LangChain: Ajustando Agentes Profundos para Funcionarem Bem com Diferentes Modelos](https://www.langchain.com/blog/tuning-deep-agents-different-models) (29-04-2026): perfis de harness específicos do modelo para prompts, nomes de ferramentas, middleware e configuração de subagentes.
- [LangChain: Aprendizado contínuo para agentes de IA](https://www.langchain.com/blog/continual-learning-for-ai-agents) (05-04-2026): dividindo a melhoria do agente em camadas de modelo, harness e contexto, alimentadas por rastreamentos.
- [Microsoft: Agent Harness no Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/) (12-03-2026): harnesses de shell/sistema de arquivos, fluxo de aprovação, execução de shell hospedada e compactação de contexto.
- [Google: Anunciando ADK para Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/) (30-03-2026): plugins, compactação de eventos, HITL, serviços de sessão/memória e A2A como primitivas de harness reutilizáveis.
- [GitHub: Automatize tarefas de repositório com GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/) (13-02-2026): GitHub Actions como um executor de fluxo de trabalho agentic com saídas seguras, sandboxing, permissões e revisão.
- [AWS: Agentes de IA em empresas: Melhores práticas com Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/) (03-02-2026): camadas de harness empresariais em Runtime, Memória, Gateway, Identidade/Política, Observabilidade e Avaliações.
- [Stripe: Minions: agentes de codificação de ponta a ponta da Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) (09-02-2026) e [Parte 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) (19-02-2026): isolamento de devbox, harnesses de agentes personalizados, máquinas de estado de blueprint, arquivos de regras, curadoria de ferramentas MCP, controles de segurança e loops de feedback pré-push/CI.
- [Cognition: O que aprendemos construindo Agentes em Nuvem](https://cognition.ai/blog/what-we-learned-building-cloud-agents) (23-04-2026): isolamento de VM, instantâneo/retomada de sessão, orquestração, governança, registro de auditoria e integrações para runtimes de agentes em nuvem.
- [Cognition: Multi-Agentes: O que realmente está funcionando](https://cognition.ai/blog/multi-agents-working) (22-04-2026): loops de gerador-verificador, revisores de contexto limpo, roteamento de "amigo inteligente", coordenação gerente-filho e limites de comunicação entre agentes.
- [Replit: Orientação em tempo de decisão: Mantendo o Agente Replit confiável](https://blog.replit.com/decision-time-guidance) (20-01-2026, atualizado em 23-01-2026): um classificador leve injeta orientação situacional curta no ponto de decisão em vez de colocar todas as regras no prompt do sistema.
- [Vercel: Como tornamos o v0 um agente de codificação eficaz](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) (07-01-2026): prompts de sistema dinâmicos, uma camada de reescrita em streaming e autofixadores determinísticos/orientados por modelo.
- [Vercel: Apresentando deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base) (04-05-2026): um harness de agente de codificação focado em segurança com etapas de varredura, investigação, revalidação, enriquecimento, exportação, plugin e verificador de recusa.
- [Sourcegraph: CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks) (03-03-2026): uma referência de harness de avaliação/ferramentas cobrindo adoção de ferramentas MCP, transcrições de uso de ferramentas, QA de benchmark, portões de verificador/reprodutibilidade e iteração de prompt/preâmbulo.

Referências gerais estritamente de 2025 foram excluídas da lista principal. O artigo original de harness da Anthropic de 2025 permanece porque é uma fonte fundamental para o curso.

## Ordem de Leitura Sugerida

1. `method-map.md`
2. `initializer-agent-playbook.md`
3. `coding-agent-startup-flow.md`
4. `prompt-calibration.md`
5. OpenAI Engenharia de Harness
6. Anthropic Harnesses eficazes
7. Anthropic Design de Harness para desenvolvimento de aplicações de longa duração
8. OpenAI Loop do agente Codex
9. Anthropic Avaliações de agentes
10. LangChain Melhorando Agentes Profundos
11. Thoughtworks / Martin Fowler Engenharia de harness para usuários de agentes de codificação
12. Cursor Melhorando continuamente nosso harness de agente
