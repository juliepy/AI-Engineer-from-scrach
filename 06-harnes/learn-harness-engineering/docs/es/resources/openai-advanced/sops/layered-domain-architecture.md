# SOP: Arquitectura de Dominio en Capas

Usa este SOP cuando el agente sigue violando límites, duplicando lógica entre capas,
o produciendo código que se vuelve difícil de revisar después de algunas sesiones.

## Objetivo

Hacer que los límites del dominio sean lo suficientemente explícitos para que los agentes
puedan moverse rápidamente sin degradar silenciosamente la estructura.

## Modelo Objetivo

Dentro de un dominio de negocio, prefiere este flujo direccional:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Las preocupaciones transversales deben entrar a través de proveedores o adaptadores explícitos.
Las utilidades compartidas permanecen fuera del dominio y no deben acumular lógica de dominio.

## Lista de Verificación de Configuración

- Define los dominios actuales en `ARCHITECTURE.md`.
- Escribe las direcciones de dependencia permitidas en `ARCHITECTURE.md`.
- Registra las interfaces transversales como auth, telemetría y APIs externas.
- Añade una nota breve para la violación de límite más difícil actualmente.
- Decide qué debe ser enforcementado mecánicamente por lint, tests o scripts.

## SOP de Ejecución

1. Mapea el código base en dominios antes de tocar el estilo de implementación.
2. Para cada dominio, identifica la secuencia de capas permitida.
3. Identifica todas las preocupaciones transversales y enrútalas a través de proveedores o adaptadores.
4. Mueve la lógica compartida ambigua al dominio propietario o a utilidades verdaderamente genéricas.
5. Documenta las reglas en `ARCHITECTURE.md`.
6. Añade una barrera de protección ejecutable para la violación de mayor costo.
7. Actualiza la puntuación de calidad después del cambio.

## Definición de Completado

- Un agente nuevo puede decir qué capa es propietaria de un cambio.
- El código de UI ya no accede directamente al repositorio o efectos secundarios externos.
- Las preocupaciones transversales tienen puntos de entrada nombrados.
- Al menos un límite importante es enforcementado mecánicamente.

## Artefactos del Repositorio A Actualizar

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- `docs/design-docs/` cuando el razonamiento cambió
- `docs/PLANS.md` o el plan de ejecución activo
