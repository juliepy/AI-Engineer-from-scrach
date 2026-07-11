# Ejemplo de Componentes del Harness

Para un agente de programación trabajando en un repositorio local:

- Modelo:
  el LLM en sí

- Harness:
  - system prompt
  - AGENTS.md
  - herramienta bash
  - herramientas de lectura/escritura de archivos
  - acceso a git
  - sistema de archivos local
  - scripts de inicio
  - comandos de prueba
  - stop hooks
  - verificaciones lint
  - bucle de evaluación (evaluator loop)

Si cambias cualquiera de las piezas del harness anteriores, cambias el agente efectivo.
