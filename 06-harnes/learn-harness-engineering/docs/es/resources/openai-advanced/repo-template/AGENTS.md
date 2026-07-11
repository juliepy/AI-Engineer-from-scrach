# AGENTS.md

Este repositorio está optimizado para trabajo de agentes de codificación de larga duración. Mantén este
archivo corto. Úsalo como la capa de enrutamiento hacia los documentos del sistema de referencia, no como un
volcado gigante de instrucciones.

## Flujo de inicio

Antes de cambiar código:

1. Confirma la raíz del repositorio con `pwd`.
2. Lee `ARCHITECTURE.md` para el mapa actual del sistema y las reglas estrictas de dependencia.
3. Lee `docs/QUALITY_SCORE.md` para ver qué dominios o capas son más débiles.
4. Lee `docs/PLANS.md`, luego abre el plan activo en el que estás trabajando.
5. Lee la especificación de producto relevante en `docs/product-specs/`.
6. Ejecuta la ruta estándar de arranque y verificación para este repositorio.
7. Si la verificación basal está fallando, repara la línea base antes de agregar alcance.

## Mapa de enrutamiento

- `ARCHITECTURE.md`: mapa de dominio, modelo de capas, reglas de dependencia
- `docs/design-docs/index.md`: decisiones de diseño y creencias fundamentales
- `docs/product-specs/index.md`: comportamientos actuales del producto y criterios de aceptación
- `docs/PLANS.md`: ciclo de vida de planes y política de planes de ejecución
- `docs/QUALITY_SCORE.md`: salud de dominios de producto y capas
- `docs/RELIABILITY.md`: señales en tiempo de ejecución, benchmarks y expectativas de reinicio
- `docs/SECURITY.md`: secretos, sandbox, datos y reglas de acciones externas
- `docs/FRONTEND.md`: restricciones de UI, reglas del sistema de diseño, verificaciones de accesibilidad

## Contrato de trabajo

- Trabaja desde un plan delimitado o una porción de funcionalidad a la vez.
- No marques el trabajo como completado solo por inspección de código; se requiere
  evidencia ejecutable.
- Si cambias un comportamiento, actualiza los documentos de producto, plan o fiabilidad
  correspondientes en la misma sesión.
- Si ves comentarios de revisión repetidos, promuévelos a una regla mecánica, verificación
  o linter en lugar de volver a explicarlo en el chat.
- Mantén el material generado en `docs/generated/` y las referencias fuente en
  `docs/references/`.
- Prefiere agregar documentos pequeños y actuales en lugar de hacer crecer este archivo.

## Definición de completado

Un cambio está completo solo cuando todas las siguientes condiciones son verdaderas:

- el comportamiento objetivo está implementado
- la verificación requerida se ejecutó realmente
- la evidencia está vinculada desde el plan o documento de calidad relevante
- los documentos afectados permanecen actualizados
- el repositorio puede reiniciarse limpiamente desde la ruta de inicio estándar

## Fin de sesión

Antes de terminar una sesión:

1. Actualiza el plan de ejecución activo.
2. Actualiza `docs/QUALITY_SCORE.md` si algún dominio o capa cambió significativamente.
3. Registra nueva deuda técnica en `docs/exec-plans/tech-debt-tracker.md` si la pospusiste.
4. Mueve los planes terminados a `docs/exec-plans/completed/` cuando sea apropiado.
5. Deja el repositorio en un estado reiniciable con una próxima acción clara.
