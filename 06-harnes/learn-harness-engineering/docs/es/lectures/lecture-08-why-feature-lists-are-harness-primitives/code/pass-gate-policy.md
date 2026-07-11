# Política de Puerta de Aprobación

Un feature solo puede pasar de `passes: false` a `passes: true` cuando:

- el flujo de trabajo esperado ha sido ejecutado
- la evidencia de éxito está registrada
- no hay errores bloqueantes en la ruta probada
- la implementación no deja la app en un estado roto o ambiguo
