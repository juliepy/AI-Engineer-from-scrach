# Skills

Este directorio contiene los skills de agentes de IA incluidos con el curso. Los skills son plantillas de prompt autocontenidas que pueden cargar agentes de programación con IA, como Claude Code, Codex, Cursor o Windsurf, para realizar tareas especializadas.

## harness-creator

Un skill de harness engineering de nivel producción para agentes de programación con IA. Te ayuda a crear, evaluar y mejorar los cinco subsistemas centrales de un harness: instrucciones, estado, verificación, alcance y ciclo de vida de la sesión.

### Qué hace

- **Crear harnesses desde cero** — AGENTS.md, listas de funciones y flujos de verificación
- **Mejorar harnesses existentes** — evaluación de cinco subsistemas con mejoras priorizadas
- **Diseñar continuidad de sesión** — memoria persistente, seguimiento de progreso y procedimientos de handoff
- **Aplicar patrones de producción** — memoria, context engineering, seguridad de herramientas y coordinación multiagente

### Inicio rápido

Los archivos del skill están en el repositorio en [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Para usarlo con Claude Code, copia el directorio `harness-creator/` a la ruta de skills de tu proyecto, o apunta tu agente al archivo SKILL.md.

### Patrones de referencia

El skill incluye 7 documentos de referencia enfocados:

| Patrón | Cuándo usarlo |
|---------|-------------|
| Memory Persistence | El agente olvida entre sesiones |
| Skill Runtime | Empaquetar workflows reutilizables como skills |
| Context Engineering | Gestión del presupuesto de contexto, carga JIT |
| Tool Registry | Seguridad de herramientas, control de concurrencia |
| Multi-Agent Coordination | Paralelismo, flujos de especialización |
| Lifecycle & Bootstrap | Hooks, tareas en segundo plano, inicialización |
| Gotchas | 15 modos de fallo no obvios con correcciones |

### Plantillas

El skill incluye plantillas listas para usar:

- `agents.md` — scaffold de AGENTS.md con reglas de trabajo
- `feature-list.json` — JSON Schema y ejemplo de lista de funciones
- `init.sh` — script estándar de inicialización
- `progress.md` — plantilla de registro de progreso de sesión
- `session-handoff.md` — plantilla de handoff de sesión

### Scripts

El skill también incluye scripts de Node.js puro para scaffold, validación, informes HTML de evaluación y benchmarks estructurales.

### Cómo se construyó este skill

`harness-creator` se desarrolló usando la metodología **skill-creator**, el metaskill oficial de Anthropic para crear, probar e iterar skills de agentes. skill-creator ofrece un flujo estructurado de borrador → prueba → evaluación → iteración, con runners de evaluación, graders y un visor de benchmarks.

- **Fuente de skill-creator**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Documentación de skills de Claude Code**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
