# DESIGN.md

Este archivo es el punto de entrada de diseño. Mantenlo breve y úsalo para enrutar hacia los
archivos más detallados en `docs/design-docs/`.

## Propósito

Registrar decisiones duraderas de diseño de producto y sistema que deberían sobrevivir más allá de
una sola conversación, sprint o memoria de revisor.

## Lee esto cuando

- necesites la filosofía de diseño actual
- estés a punto de introducir un nuevo patrón
- necesites saber qué decisiones de diseño están resueltas frente a las que aún están abiertas

## Documentos de diseño canónicos

- `docs/design-docs/index.md`: índice de documentos aceptados, propuestos y deprecados
- `docs/design-docs/core-beliefs.md`: creencias agent-first a nivel de proyecto

## Reglas de diseño

- Mantén los documentos de diseño pequeños y actualizados.
- Prefiere un documento por área de decisión.
- Vincula los documentos de diseño desde planes y especificaciones cuando un cambio depende de ellos.
- Si una regla de diseño se vuelve operativamente crítica, promuévela a una verificación
  automatizada o actualiza `ARCHITECTURE.md`.
