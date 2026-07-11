# CLAUDE.md

Estás trabajando en un repositorio diseñado para trabajo de implementación de larga duración.
Prioriza la completación fiable, la continuidad entre sesiones y la verificación explícita
sobre la velocidad.

## Bucle Operacional

Al comienzo de cada sesión:

1. Ejecuta `pwd` y confirma que estás en la raíz del repositorio esperada.
2. Lee `claude-progress.md`.
3. Lee `feature_list.json`.
4. Revisa los commits recientes con `git log --oneline -5`.
5. Ejecuta `./init.sh`.
6. Verifica si la ruta de smoke o end-to-end de referencia ya está rota.

Luego selecciona exactamente una característica inacabada y trabaja solo en esa característica hasta
que la verifiques o documentes por qué está bloqueada.

## Reglas

- Una característica activa a la vez.
- No afirmes completación sin evidencia ejecutable.
- No reescribas la lista de características para ocultar trabajo inacabado.
- No elimines o debilites tests solo para hacer que la tarea parezca completa.
- Usa los artefactos del repositorio como el sistema de registro.

## Archivos Requeridos

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- `session-handoff.md` cuando una entrega compacta es útil

## Puerta de Completación

Una característica puede pasar a `passing` solo después de que la verificación requerida tenga éxito
y el resultado esté registrado.

## Antes de Detenerte

1. Actualiza el registro de progreso.
2. Actualiza el estado de la característica.
3. Registra qué sigue roto o sin verificar.
4. Haz commit una vez que el repositorio sea seguro para reanudar.
5. Deja una ruta de reinicio limpia para la próxima sesión.
