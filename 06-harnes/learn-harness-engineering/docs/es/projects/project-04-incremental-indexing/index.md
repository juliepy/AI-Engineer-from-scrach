[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Lecciones relacionadas: [Lección 07. Define límites claros de tarea para los agentes](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Lección 08. Usa listas de funciones para restringir lo que hace el agente](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Archivos de plantilla: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/es/resources/templates/)

# Proyecto 04. Usa feedback de runtime para corregir el comportamiento del agente

## Qué harás

Añade observabilidad de runtime, como logs de arranque, logs de importación/indexación y estados de error, además de restricciones arquitectónicas para evitar violaciones entre capas. Introduce un bug de runtime para que el agente lo corrija.

Lo ejecutarás dos veces: primero sin logs ni restricciones, después con herramientas y reglas adecuadas.

## Usa el proyecto incluido

Ruta en el repositorio: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Directorio | Qué contiene | Qué comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Código de Project 03 con diagnósticos débiles. El defecto sembrado de indexación puede romper el chunking de archivos grandes, y no hay script de arquitectura. | Cuánto tarda el agente en encontrar la causa raíz sin señales de runtime. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Logger estructurado, documentación y script de límites arquitectónicos, lógica de chunking corregida y [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Si logs y checks de límites hacen la corrección más rápida y menos invasiva. |

Archivos clave: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## Herramientas

- Claude Code o Codex
- Git
- Node.js + Electron

## Mecanismo de harness

Feedback de runtime + control de alcance + indexación incremental
