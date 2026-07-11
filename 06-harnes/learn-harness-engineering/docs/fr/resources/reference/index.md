# Référence

Ces notes expliquent comment utiliser les modèles comme un harnais fonctionnel
plutôt que comme un simple ensemble de fichiers épars.

## Notes de référence internes

- [`method-map.md`](./method-map.md) : faire correspondre les modes d'échec
  courants des exécutions longues à l'artefact ou à la politique qui les
  traite en premier
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md) : ce que
  l'initialiseur doit laisser en place avant que le travail sur les fonctionnalités
  ne commence
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md) : flux fixe
  de début de session pour les sessions de codage ultérieures
- [`prompt-calibration.md`](./prompt-calibration.md) : comment garder les
  instructions racines précises sans les rendre gonflées et fragiles

## Articles principaux

Cette liste est intentionnellement restreinte. Un harnais désigne le système
d'exécution autour du modèle : la boucle de l'agent, l'exécution des outils,
le sandboxing, l'état, le contexte, la vérification, la terminaison,
l'orchestration et l'observabilité. Les articles généraux d'ingénierie de prompt
ou de cadres d'agents larges n'appartiennent pas à la liste principale.

Les trois articles originaux restent la colonne vertébrale du cours :

- [OpenAI : Harness engineering : leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11) : dépôts agent-first, contexte local au dépôt, linting personnalisé et garde-fous structurels.
- [Anthropic : Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26) : agent initialiseur, agent de codage, liste de fonctionnalités, journal de progression et passation à travers les fenêtres de contexte.
- [Anthropic : Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24) : rôles de planificateur / générateur / évaluateur, réinitialisations de contexte, simplification du harnais et hypothèses obsolètes.

Quelques articles 2026 très pertinents sont ajoutés :

- [OpenAI : Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/) (2026-01-23) : le harnais d'exécution Codex, les appels d'outils, la croissance du contexte et la terminaison de boucle.
- [Anthropic : Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2026-01-09) : évaluer le modèle et le harnais ensemble, et distinguer les harnais d'évaluation des harnais d'agents.
- [LangChain : Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026-02-17) : maintenir le modèle fixe tout en améliorant les prompts système, les outils, le middleware, le traçage et l'auto-vérification pour faire passer un agent de codage du Top 30 au Top 5 sur Terminal Bench 2.0.
- [Thoughtworks / Martin Fowler : Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) (2026-04-02) : harnais utilisateurs d'agents de codage comme guides anticipatifs et capteurs de rétroaction, avec des contrôles déterministes et inférentiels.
- [Cursor : Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) (2026-04-30) : traiter le harnais comme un système produit en amélioration continue avec évaluations hors ligne, métriques en ligne, taxonomie des erreurs d'outils, réglage spécifique au modèle et changement de modèle en cours de conversation.

## Références étendues 2026

Ce ne sont pas des sources principales du cours, mais elles sont utiles lors de la
conception de modules de harnais spécifiques. Cette section ne conserve que les sources
dont le contenu couvre directement la boucle de l'agent, l'exécution des outils, la
gestion du contexte, la vérification, le sandboxing, les couches de contrôle ou la
gouvernance des régressions. Les produits d'agents purs, les annonces de plateforme,
les études de cas d'équipe et les benchmarks sont exclus.

- [OpenAI : Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (2026-02-04) : le harnais comme protocole réutilisable d'App Server avec cycle de vie des threads, reprise, fork, diffs et intégrations clientes.
- [OpenAI Developers : Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) (2026-02-23) : mémoire de projet durable, validation des jalons et exemples de critères de complétion pour les tâches longues.
- [OpenAI : The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (2026-04-15) : harnais natifs au modèle, exécution en sandbox et exécution de fichiers/commandes.
- [OpenAI : An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/) (2026-04-27) : transformer un traqueur de tickets ou un tableau Linear en plan de contrôle multi-agents.
- [Anthropic : Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05) : équipes d'agents parallèles, verrous de tâches, synchronisation git, isolation par conteneurs et boucles autonomes.
- [Anthropic : Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (2026-04-08) : une vue méta-harnais qui sépare session, harnais et sandbox en tant qu'interfaces interchangeables.
- [Anthropic : An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) (2026-04-23) : niveau de raisonnement, élagage du contexte et prompts système comme changements de harnais nécessitant une gouvernance des régressions.
- [LangChain : Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents) (2026-01-28) : déchargement sur système de fichiers, troncature des appels d'outils, résumé et évaluations ciblées pour les harnais de gestion du contexte.
- [LangChain : Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models) (2026-04-29) : profils de harnais spécifiques au modèle pour les prompts, noms d'outils, middleware et configuration de sous-agents.
- [LangChain : Continual learning for AI agents](https://www.langchain.com/blog/continual-learning-for-ai-agents) (2026-04-05) : diviser l'amélioration des agents en couches de modèle, de harnais et de contexte, alimentée par les traces.
- [Microsoft : Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/) (2026-03-12) : harnais shell/système de fichiers, flux d'approbation, exécution shell hébergée et compactage du contexte.
- [Google : Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/) (2026-03-30) : plugins, compactage d'événements, HITL, services de session/mémoire et A2A comme primitives de harnais réutilisables.
- [GitHub : Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/) (2026-02-13) : GitHub Actions comme exécuteur de flux de travail agentique avec sorties sûres, sandboxing, permissions et revue.
- [AWS : AI agents in enterprises: Best practices with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/) (2026-02-03) : couches de harnais d'entreprise couvrant Runtime, Memory, Gateway, Identity/Policy, Observability et Evaluations.
- [Stripe : Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) (2026-02-09) et [Partie 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) (2026-02-19) : isolation devbox, harnais d'agents personnalisés, machines à états blueprint, fichiers de règles, curation d'outils MCP, contrôles de sécurité et boucles de rétroaction pre-push/CI.
- [Cognition : What We Learned Building Cloud Agents](https://cognition.ai/blog/what-we-learned-building-cloud-agents) (2026-04-23) : isolation par VM, capture/reprise de session, orchestration, gouvernance, journalisation d'audit et intégrations pour les runtimes d'agents cloud.
- [Cognition : Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working) (2026-04-22) : boucles générateur-vérificateur, réviseurs à contexte propre, routage smart-friend, coordination manager-enfant et limites de communication inter-agents.
- [Replit : Decision-Time Guidance: Keeping Replit Agent Reliable](https://blog.replit.com/decision-time-guidance) (2026-01-20, mis à jour 2026-01-23) : un classificateur léger injecte des conseils situationnels courts au point de décision au lieu de fourrer toutes les règles dans le prompt système.
- [Vercel : How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) (2026-01-07) : prompts système dynamiques, une couche de réécriture en streaming et des autocorrections déterministes/basées sur le modèle.
- [Vercel : Introducing deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base) (2026-05-04) : un harnais d'agent de codage axé sur la sécurité avec étapes de scan, investigation, revalidation, enrichissement, export, plugin et vérificateur de refus.
- [Sourcegraph : CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks) (2026-03-03) : une référence de harnais d'évaluation/outillage couvrant l'adoption d'outils MCP, les transcriptions d'utilisation d'outils, l'assurance qualité de benchmarks, les portes de vérificateur/reproductibilité et l'itération prompt/préambule.

Les références générales strictement limitées à 2025 sont exclues de la liste principale.
L'article original Anthropic de 2025 sur les harnais reste car c'est une source
fondamentale du cours.

## Ordre de lecture suggéré

1. `method-map.md`
2. `initializer-agent-playbook.md`
3. `coding-agent-startup-flow.md`
4. `prompt-calibration.md`
5. OpenAI Harness engineering
6. Anthropic Effective harnesses
7. Anthropic Harness design for long-running application development
8. OpenAI Codex agent loop
9. Anthropic agent evals
10. LangChain Improving Deep Agents
11. Thoughtworks / Martin Fowler Harness engineering for coding agent users
12. Cursor Continually improving our agent harness
