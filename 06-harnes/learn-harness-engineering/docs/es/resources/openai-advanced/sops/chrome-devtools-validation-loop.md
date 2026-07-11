# SOP: Bucle de Validación con Chrome DevTools

Usa este SOP cuando el trabajo de UI depende de la interacción real en tiempo de ejecución y las capturas de pantalla,
el estado del DOM y la salida de la consola importan más que la inspección del código por sí sola.

## Objetivo

Convertir la validación de UI en un bucle de interacción repetible que el agente pueda ejecutar hasta
que el recorrido esté limpio.

## Bucle Principal

1. Selecciona la página objetivo o la instancia de la aplicación.
2. Limpia el ruido obsoleto de la consola.
3. Captura el estado ANTES.
4. Dispara la ruta de UI.
5. Observa los eventos en tiempo de ejecución durante la interacción.
6. Captura el estado DESPUÉS.
7. Aplica la corrección y reinicia la aplicación si es necesario.
8. Vuelve a ejecutar la validación hasta que el recorrido esté limpio.

## Entradas Requeridas

- un comando de inicio estable
- un recorrido de UI reproducible
- una forma de capturar el DOM, la consola o capturas de pantalla
- una regla sobre qué cuenta como "limpio"

## SOP de Ejecución

1. Escribe el recorrido objetivo en el plan activo.
2. Define el éxito en términos observables: texto presente, botón habilitado, error eliminado,
   consola limpia, solicitud exitosa.
3. Captura el estado inicial antes de la interacción.
4. Dispara exactamente una ruta a la vez.
5. Registra los eventos en tiempo de ejecución, los cambios del DOM y la salida visible.
6. Si el recorrido falla, corrige la capa responsable más pequeña y reinicia.
7. Vuelve a ejecutar la misma ruta y compara la evidencia ANTES/DESPUÉS.

## Criterios de Limpieza

- el estado visible intencionado está presente
- los errores inesperados están ausentes
- el ruido de la consola está comprendido o eliminado
- volver a ejecutar la misma ruta produce el mismo resultado

## Artefactos del Repositorio A Actualizar

- plan de ejecución activo
- `docs/RELIABILITY.md` si el recorrido se convierte en una ruta dorada
- especificación de producto si el comportamiento visible cambió
