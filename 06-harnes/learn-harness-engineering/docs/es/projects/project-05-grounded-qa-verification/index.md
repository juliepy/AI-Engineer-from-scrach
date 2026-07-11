[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Lecciones relacionadas: [Lección 09. Evita que los agentes declaren victoria demasiado pronto](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Lección 10. Solo una ejecución de pipeline completo cuenta como verificación real](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Archivos de plantilla: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/es/resources/templates/)

# Proyecto 05. Haz que el agente verifique su propio trabajo

## Qué harás

Implementa separación de roles: un generator que implementa, un evaluator que revisa y opcionalmente un planner. Ejecuta tres veces para medir el efecto de cada rol añadido.

Elige una mejora sustancial de función, como conversación multi-turno, rediseño del panel de citas o filtrado de documentos, y mantenla igual en todas las ejecuciones.

## Usa el proyecto incluido

Ruta en el repositorio: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Directorio | Qué contiene | Qué comparar |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Aplicación basada en Project 04 antes de la mejora de historial conversacional. | Punto de partida si quieres repetir las tres variantes. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Un solo agente planifica, implementa y se autoevalúa. | Puntuación y defectos en [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md). |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Generador + evaluador con evidencia de revisión. | Puntuación y notas de revisión en [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md). |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planificador + generador + evaluador con sprint contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) y evidencia de mayor puntuación en [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md). |

## Herramientas

- Claude Code o Codex
- Git
- Node.js + Electron

## Mecanismo de harness

Autoverificación + Q&A con fundamento + finalización basada en evidencia
