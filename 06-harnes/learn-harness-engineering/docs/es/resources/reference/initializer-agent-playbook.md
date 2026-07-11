# Playbook del Agente Inicializador

Usa este playbook para la primera sesión seria en un repositorio, antes de
que comience el trabajo incremental de características.

## Objetivo

Crear una superficie operacional estable para que las sesiones posteriores puedan implementar
comportamiento sin redescubrir comandos de inicio, estado actual o límites de tareas.

## Salidas Requeridas

El inicializador debería dejar atrás al menos estos artefactos:

- un archivo de instrucciones raíz como `AGENTS.md` o `CLAUDE.md`
- una superficie de características legible por máquina como `feature_list.json`
- un artefacto de progreso duradero como `claude-progress.md`
- un ayudante de inicio estándar como `init.sh`
- un commit seguro inicial que capture el scaffold de referencia

## Lista de Verificación

1. Define la ruta de inicio estándar.
2. Define la ruta de verificación estándar.
3. Crea el registro de progreso y registra el estado inicial.
4. Descompone el trabajo en características explícitas con estados.
5. Crea el primer commit de referencia limpio.

## Test de Éxito

Una sesión nueva sin contexto de chat previo debería poder responder:

- qué hace este repositorio
- cómo iniciarlo
- cómo verificarlo
- qué está inacabado
- cuál es el mejor próximo paso
