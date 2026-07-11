[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> Lecciones relacionadas: [Lección 05. Mantén vivo el contexto entre sesiones](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Lección 06. Inicializa antes de cada sesión del agente](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Archivos de plantilla: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/es/resources/templates/)

# Proyecto 03. Mantén al agente trabajando tras reiniciar sesiones

## Qué harás

Añade control de alcance y gates de verificación al agente. Implementa particionado de documentos, extracción de metadatos, visualización del progreso de indexación y flujo de Q&A con citas. Usa `feature_list.json` para seguir el estado de las funciones: una función a la vez, sin marcar `pass` sin evidencia de verificación.

Lo ejecutarás dos veces: primero sin restricciones, luego con aplicación estricta de reglas.

## Usa el proyecto incluido

Ruta en el repositorio: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Directorio | Qué contiene | Qué comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Código de Project 02 con indexación y Q&A fundamentado todavía incompletos. Incluye un [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json) inicial, pero no los artefactos finales de reinicio y handoff. | Si el agente se desvía entre varias funciones o pierde estado al reiniciar. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Chunking, metadatos, estado de indexación y Q&A con citas completados, además de [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md) y [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | Si cada función tiene evidencia concreta antes de marcarse como aprobada. |

## Herramientas

- Claude Code o Codex
- Git
- Node.js + Electron

## Mecanismo de harness

Registro de progreso + handoff de sesión + continuidad multi-sesión
