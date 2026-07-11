# Mapa de Métodos

Esta tabla mapea los modos de fallo más comunes de agentes de codificación de larga duración
al artefacto o regla operacional que usualmente los corrige primero.

| Modo de fallo | Cómo se ve en la práctica | Corrección principal | Artefacto de soporte |
| --- | --- | --- | --- |
| Confusión de inicio en frío | Una sesión nueva pasa la mayor parte de su tiempo redescubriendo la configuración y el estado | Hacer del repositorio el sistema de registro | `claude-progress.md` |
| Expansión de alcance | El agente comienza varias características y no termina ninguna limpiamente | Restringir el alcance activo | `feature_list.json` |
| Completación prematura | El agente afirma haber terminado después de ediciones de código pero antes de una prueba ejecutable | Vincular la completación a la evidencia | `clean-state-checklist.md` |
| Inicio frágil | Cada sesión reaprende cómo arrancar el proyecto | Estandarizar la configuración y verificación | `init.sh` |
| Entrega débil | La siguiente sesión no puede decir qué está verificado, roto o pendiente | Terminar con una entrega explícita | `session-handoff.md` |
| Revisión subjetiva | La calidad de la revisión depende del gusto o la memoria | Puntuar la salida con categorías fijas | `evaluator-rubric.md` |

## Principio Operacional

Añade el artefacto más pequeño que aborde directamente el modo de fallo observado.
Evita resolver cada problema de fiabilidad volcando más texto en un archivo de instrucciones
global único.
