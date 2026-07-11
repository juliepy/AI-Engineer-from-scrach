# Referencia

Estas notas explican cómo usar las plantillas como un harness funcional en lugar de una
colección suelta de archivos.

## Notas de Referencia Interna

- [`method-map.md`](./method-map.md): mapea los modos de fallo comunes de larga duración al
  artefacto o política que los aborda primero
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md): qué debe dejar atrás el
  inicializador antes de que comience el trabajo de características
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md): flujo fijo de inicio de
  sesión para ejecuciones de codificación posteriores
- [`prompt-calibration.md`](./prompt-calibration.md): cómo mantener las instrucciones raíz
  precisas sin hacerlas hinchadas y frágiles

## Artículos Principales

Esta lista es intencionalmente estrecha. Un harness significa el sistema de ejecución alrededor
del modelo: el bucle del agente, ejecución de herramientas, sandboxing, estado, contexto,
verificación, terminación, orquestación y observabilidad. Artículos generales de ingeniería
de prompts o de frameworks amplios de agentes no pertenecen a la lista principal.

Los tres artículos originales siguen siendo la columna vertebral del curso:

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11): repositorios agent-first, contexto repo-local, linting personalizado y barreras de protección estructurales.
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26): agente inicializador, agente de codificación, lista de características, registro de progreso y entrega a través de ventanas de contexto.
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24): roles de planificador / generador / evaluador, reinicios de contexto, simplificación del harness y supuestos obsoletos.

Solo se añaden algunos artículos altamente relevantes de 2026:

- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/) (2026-01-23): el harness de tiempo de ejecución de Codex, llamadas de herramientas, crecimiento de contexto y terminación del bucle.
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2026-01-09): evaluando el modelo y el harness juntos, y distinguiendo harnesses de evaluación de harnesses de agentes.
- [LangChain: Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026-02-17): manteniendo el modelo fijo mientras se mejoran los prompts del sistema, herramientas, middleware, trazabilidad y auto-verificación para mover un agente de codificación del Top 30 al Top 5 en Terminal Bench 2.0.
- [Thoughtworks / Martin Fowler: Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) (2026-04-02): harnesses de usuario de agentes de codificación como guías de feedforward y sensores de feedback, con controles deterministas e inferenciales.
- [Cursor: Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) (2026-04-30): tratando el harness como un sistema de producto continuamente mejorado con evals offline, métricas online, taxonomía de errores de herramientas, ajuste específico del modelo y cambio de modelo en medio del chat.

## Referencias Extendidas de 2026

Estas no son fuentes centrales del curso, pero son útiles al diseñar módulos específicos
del harness. Esta sección solo mantiene fuentes cuyo contenido cubre directamente el
bucle del agente, ejecución de herramientas, gestión de contexto, verificación, sandboxing,
capas de control o gobernanza de regresión. Productos puros de agentes, anuncios de plataforma,
casos de estudio de equipos y benchmarks están excluidos.

- [OpenAI: Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (2026-02-04): el harness como un protocolo reutilizable de App Server con ciclo de vida de hilos, resume, fork, diffs e integraciones de cliente.
- [OpenAI Developers: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) (2026-02-23): memoria durable de proyecto, validación de hitos y ejemplos de done-when para tareas de larga duración.
- [OpenAI: The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) (2026-04-15): harnesses nativos del modelo, ejecución en sandbox y ejecución de archivos/comandos.
- [OpenAI: An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/) (2026-04-27): convirtiendo un issue tracker o tablero de Linear en un plano de control multi-agente.
- [Anthropic: Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05): equipos de agentes paralelos, locks de tareas, sincronización de git, aislamiento en contenedores y bucles autónomos.
- [Anthropic: Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (2026-04-08): una vista de meta-harness que separa sesión, harness y sandbox como interfaces intercambiables.
- [Anthropic: An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) (2026-04-23): esfuerzo de razonamiento, poda de contexto y prompts del sistema como cambios del harness que necesitan gobernanza de regresión.
- [LangChain: Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents) (2026-01-28): descarga al sistema de archivos, truncamiento de llamadas de herramientas, resumen y evals dirigidos para harnesses de gestión de contexto.
- [LangChain: Tuning Deep Agents to Work Well with Different Models](https://www.langchain.com/blog/tuning-deep-agents-different-models) (2026-04-29): perfiles de harness específicos del modelo para prompts, nombres de herramientas, middleware y configuración de subagentes.
- [LangChain: Continual learning for AI agents](https://www.langchain.com/blog/continual-learning-for-ai-agents) (2026-04-05): dividiendo la mejora del agente en capas de modelo, harness y contexto, impulsado por trazas.
- [Microsoft: Agent Harness in Agent Framework](https://devblogs.microsoft.com/agent-framework/agent-harness-in-agent-framework/) (2026-03-12): harnesses de shell/sistema de archivos, flujo de aprobación, ejecución de shell alojada y compactación de contexto.
- [Google: Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/) (2026-03-30): plugins, compactación de eventos, HITL, servicios de sesión/memoria y A2A como primitivas de harness reutilizables.
- [GitHub: Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/) (2026-02-13): GitHub Actions como un ejecutor de flujos de trabajo agentic con salidas seguras, sandboxing, permisos y revisión.
- [AWS: AI agents in enterprises: Best practices with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/) (2026-02-03): capas de harness empresarial a través de Runtime, Memory, Gateway, Identity/Policy, Observability y Evaluations.
- [Stripe: Minions: Stripe's one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) (2026-02-09) y [Parte 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) (2026-02-19): aislamiento en devbox, harnesses de agente personalizados, máquinas de estado de blueprint, archivos de reglas, curación de herramientas MCP, controles de seguridad y bucles de feedback pre-push/CI.
- [Cognition: What We Learned Building Cloud Agents](https://cognition.ai/blog/what-we-learned-building-cloud-agents) (2026-04-23): aislamiento en VM, snapshot/resume de sesión, orquestación, gobernanza, logging de auditoría e integraciones para tiempos de ejecución de agentes en la nube.
- [Cognition: Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working) (2026-04-22): bucles generador-verificador, revisores de contexto limpio, enrutamiento smart-friend, coordinación manager-child y límites de comunicación entre agentes.
- [Replit: Decision-Time Guidance: Keeping Replit Agent Reliable](https://blog.replit.com/decision-time-guidance) (2026-01-20, actualizado 2026-01-23): un clasificador ligero inyecta guía situacional corta en el punto de decisión en lugar de meter todas las reglas en el prompt del sistema.
- [Vercel: How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) (2026-01-07): prompts de sistema dinámicos, una capa de reescritura en streaming y autocorrectores deterministas/basados en modelo.
- [Vercel: Introducing deepsec](https://vercel.com/blog/introducing-deepsec-find-and-fix-vulnerabilities-in-your-code-base) (2026-05-04): un harness de agente de codificación enfocado en seguridad con pasos de escaneo, investigación, revalidación, enriquecimiento, exportación, plugin y verificación de rechazos.
- [Sourcegraph: CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks) (2026-03-03): una referencia de harness de eval/herramientas que cubre adopción de herramientas MCP, transcripciones de uso de herramientas, QA de benchmark, puertas de verificador/reproducibilidad e iteración de prompt/prefacio.

Las referencias generales exclusivamente de 2025 están excluidas de la lista principal. El
artículo original de 2025 de Anthropic sobre harnesses permanece porque es una fuente
fundacional del curso.

## Orden de Lectura Sugerido

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
