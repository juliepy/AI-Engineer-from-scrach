# Guía de Plantillas

Estas plantillas están listas para copiar en tu propio proyecto. Cada una cumple un propósito específico en el flujo de trabajo del agente. Edita el contenido para que coincida con los comandos, rutas, nombres de características y pasos de verificación de tu proyecto.

## Cómo Comenzar

Copia estos cuatro archivos en la raíz de tu proyecto primero:

1. `AGENTS.md` o `CLAUDE.md`
2. `init.sh`
3. `claude-progress.md`
4. `feature_list.json`

Añade los archivos restantes a medida que tu proyecto crece.

---

## AGENTS.md

El archivo de instrucciones raíz. Esta es la primera cosa que el agente lee cuando inicia una sesión. Define las reglas operacionales: qué hacer antes de escribir código, cómo trabajar y cómo cerrar.

**Cómo usarlo:**

- Copia al directorio raíz de tu proyecto
- Reemplaza los pasos del flujo de inicio con las rutas y comandos reales de tu proyecto
- Ajusta las reglas de trabajo para que coincidan con las convenciones de tu equipo
- Mantén la sección de definición de completado — es la parte más importante

**Qué hace por el agente:**

- Le indica que lea el progreso y el estado de las características antes de comenzar a trabajar
- Lo obliga a trabajar en una característica a la vez
- Requiere evidencia antes de marcar algo como completado
- Define cómo se ve un fin de sesión limpio

Usa `AGENTS.md` para Codex u otros agentes. Usa `CLAUDE.md` si estás trabajando con Claude Code — la estructura es la misma, solo formateada para el estilo de instrucciones de Claude.

## init.sh

El script de inicio. Ejecuta la instalación de dependencias, verificación e imprime el comando de inicio — todo en un solo paso.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Edita estas tres variables en la parte superior:
  - `INSTALL_CMD` — tu comando de instalación de dependencias (ej. `npm install`, `pip install -r requirements.txt`)
  - `VERIFY_CMD` — tu comando de verificación básica (ej. `npm test`, `pytest`)
  - `START_CMD` — tu comando de inicio del servidor de desarrollo (ej. `npm run dev`)
- Hazlo ejecutable: `chmod +x init.sh`

**Qué hace:**

1. Imprime el directorio actual (para que puedas confirmar que se está ejecutando en el lugar correcto)
2. Instala dependencias
3. Ejecuta el comando de verificación
4. Imprime el comando de inicio (o lo ejecuta si `RUN_START_COMMAND=1` está configurado)

Si la verificación falla, el agente debe detenerse y corregir la línea base antes de hacer cualquier otra cosa.

## claude-progress.md

El registro de progreso. Cada sesión escribe en este archivo, y cada sesión nueva lo lee primero.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Rellena la sección "Estado Verificado Actual" con la información de tu proyecto
- Después de cada sesión, actualiza el registro de sesión

**Qué significa cada campo:**

- **Estado Verificado Actual** — la única fuente de verdad sobre dónde está el proyecto
  - `Repository root directory` — dónde vive el proyecto
  - `Standard startup path` — el comando para poner en marcha el proyecto
  - `Standard verification path` — el comando para ejecutar los tests
  - `Highest priority unfinished feature` — en qué debería trabajar la próxima sesión
  - `Current blocker` — cualquier cosa que esté atascada
- **Registro de Sesión** — una entrada por sesión
  - `Goal` — lo que planeabas hacer
  - `Completed` — lo que realmente se hizo
  - `Verification run` — qué tests se ejecutaron
  - `Evidence recorded` — qué prueba se capturó
  - `Commits` — qué se commiteó
  - `Known risks` — qué podría estar roto
  - `Next best action` — dónde debería empezar la próxima sesión

## feature_list.json

El rastreador de características. Una lista legible por máquina de cada característica que el agente necesita implementar, junto con su estado, pasos de verificación y evidencia.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Reemplaza las características de ejemplo con las tuyas
- Cada característica necesita:
  - `id` — un identificador único corto
  - `priority` — entero, menor = mayor prioridad
  - `area` — qué parte de la aplicación (ej. "chat", "import", "search")
  - `title` — descripción corta
  - `user_visible_behavior` — lo que el usuario debería ver cuando funciona
  - `status` — uno de `not_started`, `in_progress`, `blocked`, `passing`
  - `verification` — instrucciones paso a paso para confirmar que funciona
  - `evidence` — prueba registrada de que la verificación pasó (rellenada por el agente)
  - `notes` — cualquier contexto adicional

**Reglas de estado:**

- `not_started` — no ha sido tocada
- `in_progress` — la única característica en la que se está trabajando actualmente (solo una a la vez)
- `blocked` — no se puede proceder debido a un problema documentado
- `passing` — la verificación pasó y la evidencia está registrada

El agente solo debe tener una característica en `in_progress` en cualquier momento.

## session-handoff.md

Una nota de entrega compacta entre sesiones. Usa esto cuando una sesión termina y quieres que la próxima la retome rápidamente.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Rellénalo al final de cada sesión (o haz que el agente lo rellene)

**Qué cubre cada sección:**

- **Actualmente verificado** — qué está confirmado como funcionando y qué verificación se ejecutó
- **Cambios esta sesión** — qué código o infraestructura cambió
- **Aún roto o sin verificar** — problemas conocidos y áreas de riesgo
- **Mejor próxima acción** — qué debería hacer la próxima sesión, y qué no tocar
- **Comandos** — comandos de inicio, verificación y depuración para referencia rápida

Este archivo es opcional para sesiones pequeñas. Se vuelve importante cuando las sesiones son largas o cuando el proyecto tiene múltiples áreas activas.

## clean-state-checklist.md

Una lista de verificación para revisar antes de terminar cada sesión. Asegura que el repositorio esté en un buen estado para que la próxima sesión comience limpiamente.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Revísala antes de cerrar una sesión
- El agente también debería verificar estos elementos como parte de su rutina de fin de sesión

**Qué verifica:**

- El inicio estándar sigue funcionando
- La verificación estándar sigue ejecutándose
- El registro de progreso está actualizado
- La lista de características refleja el estado real (no hay entradas `passing` falsas)
- No hay trabajo a medio terminar sin registrar
- La próxima sesión puede continuar sin correcciones manuales

## evaluator-rubric.md

Una tarjeta de puntuación para revisar la calidad de salida del agente. Usa esto después de una sesión o en hitos del proyecto para evaluar si el trabajo cumple con el estándar.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Después de una sesión (o un conjunto de sesiones), puntúa el trabajo del agente en seis dimensiones
- Cada dimensión se puntúa de 0 a 2

**Las seis dimensiones:**

1. **Corrección** — ¿la implementación coincide con el comportamiento objetivo?
2. **Verificación** — ¿las verificaciones requeridas se ejecutaron realmente, con evidencia?
3. **Disciplina de alcance** — ¿el agente se mantuvo dentro de la característica seleccionada?
4. **Fiabilidad** — ¿el resultado sobrevive un reinicio o reejecución?
5. **Mantenibilidad** — ¿el código y la documentación son lo suficientemente claros para la próxima sesión?
6. **Preparación de entrega** — ¿puede una sesión nueva continuar usando solo artefactos del repositorio?

**Opciones de conclusión:**

- Aceptar — cumple con el estándar
- Revisar — necesita correcciones antes de aceptar
- Bloquear — problemas fundamentales que necesitan resolverse primero

**Importante: el evaluador necesita ajuste.** De fábrica, los agentes son malos autojueces — identifican problemas y luego se convencen a sí mismos de aprobar. Necesitarás iterar:

1. Ejecuta el evaluador en un sprint completado.
2. Compara sus puntuaciones con tu propio juicio humano.
3. Donde diverjan, haz la rúbrica más específica sobre los criterios de aprobación/fallo.
4. Vuelve a ejecutar y verifica la alineación.
5. Repite hasta que el evaluador coincida consistentemente con la revisión humana.

Planifica 3-5 rondas de ajuste. Registra cada cambio para que puedas rastrear qué mejoró la alineación.

## quality-document.md

Una instantánea de calidad que califica cada dominio de producto y capa arquitectónica en tu proyecto. Rastrea la salud del código base a lo largo del tiempo, no solo la salida de sesiones individuales.

**Cómo usarlo:**

- Copia a la raíz de tu proyecto
- Antes de comenzar una sesión: léelo para entender dónde el código base es más débil
- Después de una sesión: actualiza las calificaciones basándote en qué cambió
- Con el tiempo: compara instantáneas para ver qué cambios del harness realmente mejoraron la salud del código base

**Qué califica:**

- **Dominios de producto** (ej., importación de documentos, flujo de P&R, indexación): cada dominio recibe una calificación (A-D) en estado de verificación, legibilidad del agente, estabilidad de tests y brechas clave
- **Capas arquitectónicas** (ej., proceso principal, preload, renderer, servicios): cada capa recibe una calificación para enforcement de límites y legibilidad del agente

**Por qué importa:**

La rúbrica del evaluador puntúa las salidas individuales del agente. El documento de calidad puntúa el código base en sí. Responden a preguntas diferentes:

- Rúbrica del evaluador: "¿Hizo buen trabajo el agente en esta sesión?"
- Documento de calidad: "¿El proyecto se está fortaleciendo o debilitando con el tiempo?"

**Cuándo actualizar:**

- Después de cada sesión significativa
- Antes de comparaciones de benchmark
- Después de pases de limpieza o simplificación
- Al incorporar un nuevo agente o modelo al proyecto

**Conexión con la simplificación del harness:**

El documento de calidad también soporta la simplificación del harness. Cada componente del harness codifica un supuesto sobre lo que el modelo no puede hacer. A medida que los modelos mejoran, estos supuestos se vuelven obsoletos. Para verificar si un componente sigue siendo necesario:

1. Toma una instantánea del documento de calidad.
2. Elimina un componente del harness.
3. Ejecuta el conjunto de tareas de benchmark.
4. Toma otra instantánea.
5. Compara — si las calificaciones no bajaron, el componente era sobrecarga. Si bajaron, restáuralo.
