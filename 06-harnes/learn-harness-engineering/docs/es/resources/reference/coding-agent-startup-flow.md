# Flujo de Inicio del Agente de Codificación

Usa esto al comienzo de cada sesión después de que la inicialización esté completa.

## Plantilla de Inicio Fija

1. Ejecuta `pwd` y confirma la raíz del repositorio.
2. Lee `claude-progress.md`.
3. Lee `feature_list.json`.
4. Revisa los commits recientes con `git log --oneline -5`.
5. Ejecuta `./init.sh`.
6. Ejecuta una ruta de smoke o end-to-end de referencia.
7. Si la referencia está rota, corrígela primero.
8. Selecciona la característica inacabada de mayor prioridad.
9. Trabaja solo en esa característica hasta que esté verificada o explícitamente bloqueada.

## Por Qué Este Orden Importa

- `pwd` previene trabajo accidental en el directorio equivocado.
- los archivos de progreso y características recuperan estado duradero antes de que comiencen nuevas ediciones.
- los commits recientes explican qué cambió más recientemente.
- `init.sh` estandariza el inicio en lugar de depender de la memoria.
- la verificación de referencia captura estados iniciales rotos antes de que el trabajo nuevo los oculte.

## Espejo de Fin de Sesión

La misma sesión debería terminar:

1. registrando el progreso
2. actualizando el estado de las características
3. escribiendo una entrega si es necesario
4. haciendo commit del trabajo seguro
5. dejando una ruta de reinicio limpia
