[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> Lecciones relacionadas: [Lección 01. Los modelos fuertes no significan ejecución fiable](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [Lección 02. Qué significa realmente harness](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Archivos de plantilla: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/es/resources/templates/)

# Proyecto 01. Solo prompt vs reglas primero: cuánta diferencia produce

## Qué harás

Construye el esqueleto mínimo de una aplicación Electron de base de conocimiento: una ventana con lista de documentos a la izquierda, panel de Q&A a la derecha y un directorio de datos local. La tarea no es compleja. Lo complejo es cómo consigues que el agente la complete.

La ejecutarás dos veces. Primera vez: solo un prompt, sin preparación. Segunda vez: con `AGENTS.md`, `init.sh` y `feature_list.json` ya colocados en el repositorio. Luego compara.

Este escenario de curso usa un intervalo breve de redescubrimiento/preparación como ejemplo, no un resultado medido fijo.

## Herramientas

- Claude Code o Codex (elige uno y úsalo en ambas ejecuciones)
- Git (gestionar ramas y comparar)
- Node.js + Electron (stack del proyecto)
- Un temporizador (registrar la duración de cada ejecución)

## Mecanismo de harness

Harness mínimo: `AGENTS.md` + `init.sh` + `feature_list.json`

## Usa el proyecto incluido

Ruta en el repositorio: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Directorio | Qué contiene | Cómo usarlo |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | Ejecución con harness débil. Solo tiene [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) como descripción de tarea y no incluye `AGENTS.md` ni `feature_list.json`. | Entrega el prompt a tu agente y mide qué completa sin estructura adicional. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | El mismo slice del producto con artefactos de harness explícitos: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json) y [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | Compara cómo las reglas y la verificación convierten la misma tarea en algo ejecutable y comprobable. |

Las cuatro funciones concretas son: lanzar la ventana, lista de documentos, panel de preguntas y respuestas, y creación del directorio de datos local. Consulta `solution/feature_list.json` para ver la evidencia esperada de cada función.
