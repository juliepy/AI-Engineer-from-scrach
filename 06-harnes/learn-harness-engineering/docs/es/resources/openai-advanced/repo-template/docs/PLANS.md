# PLANS.md

Este archivo define cómo se crean, actualizan, completan y archivan los planes de ejecución.

## Cuándo Se Requiere Un Plan

Crea un plan de ejecución cuando el trabajo:

- abarca más de una sesión
- modifica más de un subsistema
- tiene riesgos no triviales de verificación o despliegue
- depende de decisiones abiertas que deben registrarse

## Ubicaciones de Planes

- `docs/exec-plans/active/`: planes que actualmente dirigen el trabajo
- `docs/exec-plans/completed/`: planes finalizados conservados para contexto futuro del agente
- `docs/exec-plans/tech-debt-tracker.md`: trabajo pospuesto y seguimientos

## Secciones Mínimas del Plan

- objetivo
- alcance y fuera de alcance
- ruta de verificación
- riesgos y bloqueos
- registro de progreso
- decisiones abiertas

## Reglas de Operación

- Un plan activo debe tener un paso actual claramente asignado.
- Actualiza el plan a medida que avanza el trabajo; no lo trates como texto estático.
- Si una decisión cambia la dirección de implementación, regístrala en el plan.
- Mueve los planes finalizados a `completed/` para que los agentes puedan descubrir el contexto previo.
