# FRONTEND.md

Este archivo define expectativas estables del frontend para que los agentes no inventen
patrones de UI de forma impredecible.

## Principios de UI

- Optimiza para la claridad antes que para la novedad.
- Mantén los flujos de interacción descubribles y reiniciables.
- Prefiere un pequeño número de componentes reutilizables sobre variantes de un solo uso.
- Las verificaciones de accesibilidad son parte de la verificación normal, no trabajo de pulido.

## Barreras de protección

- Documenta el sistema de diseño o la biblioteca de componentes en `docs/references/`.
- Registra los estados clave visibles para el usuario: vacío, cargando, éxito, error, reintento.
- Mantén el texto, el comportamiento del teclado y la jerarquía visual consistentes entre flujos.
- Cuando se corrija un error de UI, agrega o actualiza el paso de validación correspondiente.

## Expectativas de verificación

- Captura evidencia para los recorridos de usuario críticos.
- Registra los pasos de validación del navegador o tiempo de ejecución en el plan relevante.
- Si las regresiones visuales son comunes, estandariza las verificaciones de capturas de pantalla o DOM.
