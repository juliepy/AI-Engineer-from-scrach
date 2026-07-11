<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/EN-English-blue?style=flat-square"></a>
  <a href="docs-readme/zh-CN/README.md"><img alt="简体中文" src="https://img.shields.io/badge/ZH-简体中文-red?style=flat-square"></a>
  <a href="docs-readme/zh-TW/README.md"><img alt="繁體中文" src="https://img.shields.io/badge/ZH--TW-繁體中文-orange?style=flat-square"></a>
  <a href="docs-readme/ja-JP/README.md"><img alt="日本語" src="https://img.shields.io/badge/JA-日本語-green?style=flat-square"></a>
  <a href="docs-readme/ko-KR/README.md"><img alt="한국어" src="https://img.shields.io/badge/KO-한국어-blueviolet?style=flat-square"></a>
  <a href="docs-readme/es-ES/README.md"><img alt="Español" src="https://img.shields.io/badge/ES-Español-yellow?style=flat-square"></a>
  <a href="docs-readme/fr-FR/README.md"><img alt="Français" src="https://img.shields.io/badge/FR-Français-007EC6?style=flat-square"></a>
  <a href="docs-readme/ru-RU/README.md"><img alt="Русский" src="https://img.shields.io/badge/RU-Русский-informational?style=flat-square"></a>
  <a href="docs-readme/de-DE/README.md"><img alt="Deutsch" src="https://img.shields.io/badge/DE-Deutsch-2EA043?style=flat-square"></a>
  <a href="docs-readme/ar-SA/README.md"><img alt="العربية" src="https://img.shields.io/badge/AR-العربية-success?style=flat-square"></a>
  <a href="docs-readme/vi-VN/README.md"><img alt="Tiếng Việt" src="https://img.shields.io/badge/VI-Tiếng_Việt-cc6699?style=flat-square"></a>
  <a href="docs-readme/uz-UZ/README.md"><img alt="Oʻzbekcha" src="https://img.shields.io/badge/UZ-Oʻzbekcha-1A8BBA?style=flat-square"></a>
  <a href="docs-readme/tr-TR/README.md"><img alt="Türkçe" src="https://img.shields.io/badge/TR-Türkçe-E30A17?style=flat-square"></a>
  <a href="docs-readme/pt-BR/README.md"><img alt="Português-BR" src="https://img.shields.io/badge/PT--BR-Português-1A8BBA?style=flat-square"></a>
</p>

<h1 align="center">Aprenda Engenharia de Harness</h1>

<p align="center"><strong>Um curso baseado em projetos sobre a construção do ambiente, gerenciamento de estado, verificação e mecanismos de controle que fazem os agentes de codificação de IA funcionarem de forma confiável.</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/Aulas-12-blue?style=flat-square" alt="12 Aulas">
  <img src="https://img.shields.io/badge/Projetos-6-green?style=flat-square" alt="6 Projetos">
  <img src="https://img.shields.io/badge/Idiomas-14-yellow?style=flat-square" alt="14 Idiomas">
  <img src="https://img.shields.io/badge/Licença-MIT-lightgrey?style=flat-square" alt="Licença MIT">
</p>

> **Ícone de globo** Este curso está disponível em **14 idiomas**: Inglês, 简体中文, 繁體中文, 日本語, 한국어, Español, Français, Русский, Deutsch, العربية, Tiếng Việt, Oʻzbekcha, Türkçe e Português (BR). Escolha seu idioma nos emblemas acima.

Aprenda Engenharia de Harness é um curso dedicado à engenharia de agentes de codificação de IA. Estudamos profundamente e sintetizamos as teorias e práticas mais avançadas de Engenharia de Harness na indústria. Nossas referências principais incluem:

- [OpenAI: Engenharia de Harness: aproveitando o Codex em um mundo focado em agentes](https://openai.com/index/harness-engineering/)
- [Anthropic: Harnesses eficazes para agentes de longa duração](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Design de Harness para desenvolvimento de aplicativos de longa duração](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering)

> **Início rápido?** A skill [`skills/harness-creator/`](./skills/harness-creator/) pode ajudá-lo a estruturar um harness de nível de produção (AGENTS.md, listas de recursos, init.sh, fluxos de verificação) para seu próprio projeto em minutos.

---

## Índice

- [✨ Prévia Visual](#-visual-preview)
- [O que Realmente Significa Engenharia de Harness](#what-harness-engineering-actually-means)
- [Início Rápido: Melhore Seu Agente Hoje](#quick-start-improve-your-agent-today)
- [Projeto Final: Um Aplicativo Real](#capstone-project-a-real-app)
- [Trilha de Aprendizagem](#learning-path)
- [Ementa](#syllabus)
- [Skills](#skills)
- [Outros Cursos](#other-courses)

---

## ✨ Prévia Visual

### 🏠 Página Inicial do Curso
> Um esboço abrangente do curso e introdução às filosofias centrais, fornecendo um caminho claro para começar.

![Prévia da página inicial do curso](../../docs/public/screenshots/readme/pt-BR-home.png)

### 📖 Aulas Imersivas
> Mergulhos profundos em pontos problemáticos do mundo real e projetos práticos (como o Projeto 01) para uma experiência de aprendizado imersiva.

![Prévia da aula do curso](../../docs/public/screenshots/readme/pt-BR-lecture-01.png)

### 🗂️ Biblioteca de Recursos Pronta para Uso
> Modelos e configurações de referência projetados para resolver armadilhas comuns no desenvolvimento de agentes de IA de múltiplos turnos, como perda de contexto e conclusão prematura de tarefas.

![Prévia da biblioteca de recursos](../../docs/public/screenshots/readme/pt-BR-resources.png)

## Livros de Curso em PDF

O repositório agora inclui um pipeline de construção de PDF para o conteúdo do curso.

- Execute `npm run pdf:build` para gerar localmente os livros do curso em PDF configurados atualmente.
- Os arquivos de saída são gravados em `artifacts/pdfs/`.
- Execute `npm run screenshots:readme` se desejar atualizar as imagens de prévia do README.
- O fluxo de trabalho do GitHub Actions [`release-course-pdfs.yml`](./.github/workflows/release-course-pdfs.yml) pode construir os PDFs e publicá-los no GitHub Releases.

---

## O Modelo é Inteligente, o Harness o Torna Confiável

Existe uma verdade dura que a maioria das pessoas aprende da maneira mais difícil: **o modelo mais forte do mundo ainda falhará em tarefas de engenharia reais se você não construir um ambiente adequado ao redor dele.**

Você provavelmente já viu isso. Você dá ao Claude ou ao GPT uma tarefa em seu repositório. Ele começa bem — lê arquivos, escreve código, parece produtivo. De repente, algo dá errado. Ele pula uma etapa. Ele quebra um teste. Ele diz "concluído", mas nada realmente funciona. Você gasta mais tempo limpando a bagunça do que se tivesse feito você mesmo.

Isso não é um problema do modelo. É um problema do harness.

A evidência é clara. A Anthropic realizou um experimento controlado: mesmo modelo (Opus 4.5), mesmo prompt ("construa um editor de jogos retrô 2D"). Sem um harness, ele gastou US$ 9 em 20 minutos e produziu algo que não funcionava. Com um harness completo (planejador + gerador + avaliador), ele gastou US$ 200 em 6 horas e construiu um jogo que você realmente podia jogar. O modelo não mudou. O harness mudou.

A OpenAI relatou a mesma coisa com o Codex: em um repositório bem estruturado com um harness, o mesmo modelo passa de "não confiável" para "confiável". Não é uma melhoria marginal — é uma mudança qualitativa.

**Este curso ensina como construir esse ambiente.**

```text
                    O PADRÃO DO HARNESS
                    ====================

    Você --> dá a tarefa --> Agente lê os arquivos do harness --> Agente executa
                                                                 |
                                              o harness governa cada etapa:
                                              |
                                              +--> Instruções: o que fazer, em que ordem
                                              +--> Escopo:     um recurso por vez, sem excessos
                                              +--> Estado:     log de progresso, lista de recursos, histórico do git
                                              +--> Verificação: testes, lint, verificação de tipos, smoke runs
                                              +--> Ciclo de vida: inicialização no início, estado limpo no fim
                                              |
                                              v
                                         Agente para apenas quando a
                                         verificação é aprovada
```

---

## O que Realmente Significa Engenharia de Harness

Engenharia de harness trata de construir um ambiente de trabalho completo ao redor do modelo para que ele produza resultados confiáveis. Não se trata de escrever prompts melhores. Trata-se de projetar o sistema dentro do qual o modelo opera.

Um harness possui cinco subsistemas:

```text
    ┌────────────────────────────────────────────────────────────────┐
    │                          O HARNESS                             │
    │                                                                │
    │   ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
    │   │ Instruções   │  │    Estado    │  │   Verificação      │   │
    │   │              │  │              │  │                    │   │
    │   │ AGENTS.md    │  │ progress.md  │  │ testes + lint      │   │
    │   │ CLAUDE.md    │  │ feature_list │  │ verificação tipos  │   │
    │   │ feature_list │  │ git log      │  │ smoke runs         │   │
    │   │ docs/        │  │ session hand │  │ pipeline e2e       │   │
    │   └──────────────┘  └──────────────┘  └────────────────────┘   │
    │                                                                │
    │   ┌──────────────┐  ┌──────────────────────────────────────┐   │
    │   │   Escopo     │  │         Ciclo de Vida da Sessão      │   │
    │   │              │  │                                      │   │
    │   │ um recurso   │  │ init.sh no início                    │   │
    │   │ por vez      │  │ checklist de estado limpo no fim     │   │
    │   │ definição de │  │ nota de entrega para a próxima sessão │   │
    │   │ concluído    │  │ commit apenas quando seguro retomar   │   │
    │   └──────────────┘  └──────────────────────────────────────┘   │
    │                                                                │
    └────────────────────────────────────────────────────────────────┘

    O MODELO decide qual código escrever.
    O HARNESS governa quando, onde e como ele o escreve.
    O harness não torna o modelo mais inteligente.
    Ele torna a saída do modelo confiável.
```

Cada subsistema tem uma função:

- **Instruções** — Dizem ao agente o que fazer, em que ordem e o que ler antes de começar. Não é um único arquivo gigante; é uma estrutura de divulgação progressiva pela qual o agente navega sob demanda.
- **Estado** — Rastreia o que foi feito, o que está em andamento e o que vem a seguir. Persistido no disco para que a próxima sessão recomece exatamente de onde a última parou.
- **Verificação** — Apenas uma suíte de testes aprovada conta como evidência. O agente não pode declarar vitória sem uma prova executável.
- **Escopo** — Restringe o agente a um recurso por vez. Sem excessos. Sem deixar três coisas pela metade. Sem reescrever a lista de recursos para esconder trabalho inacabado.
- **Ciclo de Vida da Sessão** — Inicializa no início. Limpa no fim. Deixa um caminho de reinicialização limpo para a próxima sessão.

---

## Por que Este Curso Existe

A questão não é "os modelos podem escrever código?". Eles podem. A questão é: **eles podem concluir de forma confiável tarefas de engenharia reais dentro de repositórios reais, ao longo de múltiplas sessões, sem supervisão humana constante?**

No momento, a resposta é: não sem um harness.

```text
    SEM HARNESS                                COM HARNESS
    ===========                                ===========

    Sessão 1: agente escreve código            Sessão 1: agente lê instruções
               agente quebra testes                       agente executa init.sh
               agente trabalha em um recurso
               você corrige manualmente                   agente verifica antes de concluir
                                                          agente atualiza log de progresso
    Sessão 2: agente começa do zero                       agente commita estado limpo
               agente não tem memória
               do que aconteceu antes          Sessão 2: agente lê log de progresso
               agente refaz o trabalho                    agente recomeça de onde parou
               ou faz algo totalmente diferente           agente continua o recurso inacabado
               você corrige novamente                     você revisa, não resgata

    Resultado: você gasta mais tempo           Resultado: o agente faz o trabalho,
               limpando do que se                         você verifica o resultado
               tivesse feito você mesmo
```

As perguntas com as quais este curso realmente se preocupa:

- Quais designs de harness melhoram as taxas de conclusão de tarefas?
- Quais designs reduzem o retrabalho e as conclusões incorretas?
- Quais mecanismos mantêm as tarefas de longa duração progredindo de forma constante?
- Quais estruturas mantêm o sistema sustentável após múltiplas execuções do agente?

---

## Currículo do Curso e Documentação

Para os materiais completos do curso, visite o **[Site de Documentação](https://walkinglabs.github.io/learn-harness-engineering/)**.

O currículo está dividido em três partes:

1. **Aulas**: 12 unidades conceituais explicando a teoria por trás da engenharia de harness.
2. **Projetos**: 6 projetos práticos onde você constrói um espaço de trabalho agentic do zero.
3. **Biblioteca de Recursos**: Modelos prontos para copiar (`AGENTS.md`, `feature_list.json`, `init.sh`, etc.) para usar em seus próprios repositórios hoje.

---

## Início Rápido: Melhore Seu Agente Hoje

Você não precisa ler todas as 12 aulas antes de começar a obter valor. Se você já está usando um agente de codificação em um projeto real, veja como melhorá-lo agora mesmo.

A ideia é simples: em vez de apenas escrever prompts, dê ao seu agente um conjunto de arquivos estruturados que definem o que fazer, o que foi feito e como verificar o trabalho. Esses arquivos vivem dentro do seu repositório, para que cada sessão comece do mesmo estado.

```text
    RAIZ DO SEU PROJETO
    ├── AGENTS.md              <-- o manual de operação do agente
    ├── CLAUDE.md              <-- (alternativa, se usar Claude Code)
    ├── init.sh                <-- executa install + verify + start
    ├── feature_list.json      <-- quais recursos existem, quais estão prontos
    ├── claude-progress.md     <-- o que aconteceu em cada sessão
    └── src/                   <-- seu código real
```

Pegue os modelos iniciais da [Biblioteca de Recursos](https://walkinglabs.github.io/learn-harness-engineering/pt-BR/resources/) e coloque-os em seu projeto. É isso. Quatro arquivos, e suas sessões de agente já serão significativamente mais estáveis do que rodando apenas com prompts.

---

## Projeto Final: Um Aplicativo Real

Todos os seis projetos do curso giram em torno do mesmo produto: **um aplicativo de desktop de base de conhecimento pessoal baseado em Electron**.

---

## Referências Principais

Primárias:

- [OpenAI: Engenharia de Harness: aproveitando o Codex em um mundo focado em agentes](https://openai.com/index/harness-engineering/)
- [Anthropic: Harnesses eficazes para agentes de longa duração](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Design de Harness para desenvolvimento de aplicativos de longa duração](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [OpenAI: Desdobrando o loop do agente Codex](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [Anthropic: Desmistificando avaliações (evals) para agentes de IA](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [LangChain: Melhorando agentes avançados com harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
- [Thoughtworks / Martin Fowler: Harness engineering para usuários de agentes de programação](https://martinfowler.com/articles/harness-engineering.html)
- [Cursor: Melhorando continuamente nosso harness de agentes](https://cursor.com/blog/continually-improving-agent-harness)

Veja a lista completa de referências em camadas em [`docs/pt-BR/resources/reference/`](../../docs/pt-BR/resources/reference/index.md).

---

## Estrutura do Repositório

```text
learn-harness-engineering/
├── docs/                          # Site de documentação VitePress
│   ├── lectures/                  # 12 aulas (index.md + exemplos de código)
│   │   ├── lecture-01-*/
│   │   └── ... (12 no total)
│   ├── projects/                  # Descrições de 6 projetos
│   │   ├── project-01-*/
│   │   └── ... (6 no total)
│   └── resources/                 # Modelos e referências multilíngues (14 idiomas)
│       ├── en/
│       └── ... (14 no total)
├── projects/
│   ├── shared/                    # Base compartilhada Electron + TypeScript + React
│   └── project-NN/                # Diretórios starter/ e solution/ por projeto
├── skills/                        # Skills reutilizáveis de agentes de IA
│   └── harness-creator/           # Skill de engenharia de harness
├── package.json                   # VitePress + ferramentas de desenvolvimento
└── CLAUDE.md                      # Instruções do Claude Code para este repositório
```

---

## Como o Curso está Organizado

- Cada aula foca em uma pergunta.
- O curso inclui 6 projetos.
- Cada projeto exige que o agente faça um trabalho real.
- Cada projeto compara os resultados de um harness fraco vs. forte.
- O que importa é a diferença medida, não quantos documentos foram escritos.

---

## Skills

Este repositório também inclui skills reutilizáveis de agentes de IA que você pode instalar diretamente em seu IDE ou espaço de trabalho de agente.

- [**harness-creator**](../../skills/harness-creator/): Uma skill que ajuda você a estruturar um harness de nível de produção para seu próprio projeto em minutos.

---

## Outros Cursos

Nossa equipe também criou outros cursos! Confira-os:

[![Hands-on Modern RL](https://img.shields.io/badge/HANDS--ON_MODERN_RL-0052cc?style=for-the-badge)](https://github.com/walkinglabs/hands-on-modern-rl)

**Hands-on Modern RL**: Um currículo prático de código aberto que preenche a lacuna entre os conceitos básicos de RL e o alinhamento de LLM, RLVR e sistemas Agentic avançados.

[![Modern LLM Notebook](https://img.shields.io/badge/MODERN_LLM_NOTEBOOK-0052cc?style=for-the-badge)](https://github.com/walkinglabs/modern-llm-notebook)

**Modern LLM Notebook**: Um curso prático para construir LLMs modernos do zero em PyTorch, com 23 Jupyter Notebooks executáveis cobrindo tokenizadores, atenção, MoE, RLHF, inferência, avaliação e destilação.

---

## Agradecimentos

Este curso foi inspirado e extrai ideias de [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) — um guia progressivo para construir um agente do zero, de um único loop à execução autônoma isolada.
