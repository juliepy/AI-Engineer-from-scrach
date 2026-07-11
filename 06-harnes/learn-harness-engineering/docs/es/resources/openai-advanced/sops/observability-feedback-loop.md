# SOP: Bucle de Retroalimentación de Observabilidad

Usa este SOP cuando la depuración es lenta, los agentes siguen afirmando éxito sin
evidencia, o el comportamiento en tiempo de ejecución es más difícil de inspeccionar que el código en sí.

## Objetivo

Proporcionar al agente un bucle de retroalimentación local sobre logs, métricas, trazas y cargas de
trabajo ejecutables para que pueda razonar desde la ejecución, no solo desde la inspección del código.

## Stack Mínimo

- la aplicación emite logs estructurados
- la aplicación emite métricas y trazas cuando sea factible
- capa local de distribución o recopilación
- interfaces de consulta para logs, métricas y trazas
- carga de trabajo repetible o recorrido de usuario para volver a ejecutar después de cada cambio

## SOP de Ejecución

1. Define los recorridos dorados en tiempo de ejecución que más importan.
2. Añade logs estructurados al inicio y a la ruta crítica.
3. Añade métricas para latencia, conteos de fallos o profundidad de cola donde sea útil.
4. Añade trazas o marcadores de tiempo para flujos lentos o de múltiples pasos.
5. Haz que las señales sean consultables desde el entorno de desarrollo local.
6. Proporciona al agente una carga de trabajo o escenario repetible para volver a ejecutar.
7. Requiere el bucle: consultar -> correlacionar -> razonar -> implementar -> reiniciar ->
   volver a ejecutar -> verificar.

## Lista de Verificación de Sesión de Depuración

- ¿Qué falló?
- ¿Qué señal prueba el fallo?
- ¿Qué capa es propietaria del fallo?
- ¿Qué cambió después de la corrección?
- ¿La aplicación se reinició limpiamente?
- ¿La misma carga de trabajo pasó después de volver a ejecutar?

## Definición de Completado

- El agente puede explicar un modo de fallo a partir de evidencia en tiempo de ejecución.
- La misma carga de trabajo puede volver a ejecutarse después de cada cambio.
- Reiniciar y volver a ejecutar son parte del bucle de tareas normal.
- Las señales de fiabilidad están documentadas en `docs/RELIABILITY.md`.
