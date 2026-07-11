# RELIABILITY.md

Este archivo define cómo el sistema demuestra que está saludable y es reiniciable.

## Rutas Estándar

- Arranque: `[command]`
- Verificación: `[command]`
- Iniciar aplicación o servicio: `[command]`
- Depurar o inspeccionar tiempo de ejecución: `[command]`

## Señales Requeridas en Tiempo de Ejecución

- logs estructurados para inicio y flujos críticos
- verificaciones de salud para servicios clave
- datos de traza o tiempo para rutas lentas cuando estén disponibles
- estados de error visibles para el usuario para fallos recuperables

## Recorridos Dorados

- `[journey 1]`
- `[journey 2]`
- `[journey 3]`

Cada recorrido dorado debe tener una ruta de verificación repetible y señales de fallo claras.

## Reglas de Fiabilidad

- Ninguna característica está completa si el sistema no puede reiniciarse limpiamente después.
- Los fallos en tiempo de ejecución deben ser diagnosticables desde señales locales del repositorio.
- Si aparece un modo de fallo repetido, añade un benchmark o barrera de protección para él.
- La limpieza es parte de la fiabilidad, no una preocupación separada.
