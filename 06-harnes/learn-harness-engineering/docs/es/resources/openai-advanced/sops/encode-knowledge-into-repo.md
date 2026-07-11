# SOP: Codificar Conocimiento No Visible En El Repositorio

Usa este SOP cuando un contexto importante todavía reside en Google Docs, hilos de chat,
tickets o en la cabeza de las personas.

## Objetivo

Hacer que el conocimiento invisible para el agente sea descubrible en el código base para que una sesión nueva
pueda actuar sobre él sin depender de una conversación previa.

## Señales de Disparo

- El agente sigue preguntando cómo funciona el sistema.
- Las personas dicen "decidimos esto en Slack" o "sigue lo que X dijo la semana pasada."
- Las revisiones referencian reglas de producto o seguridad que no están escritas en el repositorio.
- Las sesiones nuevas repiten trabajo de descubrimiento que ya debería estar resuelto.

## SOP de Ejecución

1. Lista las fuentes de conocimiento invisible: docs, chats, reglas tácitas del equipo, decisiones verbales.
2. Para cada fuente, pregunta: ¿es esto arquitectura, comportamiento de producto, política de seguridad,
   expectativa de fiabilidad, contexto de plan o material de referencia?
3. Codifícalo en el artefacto del repositorio correspondiente:
   - arquitectura -> `ARCHITECTURE.md`
   - comportamiento de producto -> `docs/product-specs/`
   - razonamiento de diseño -> `docs/design-docs/`
   - estado de ejecución -> `docs/exec-plans/`
   - referencias externas repetidas -> `docs/references/`
   - expectativas de calidad o fiabilidad -> `docs/QUALITY_SCORE.md` o `docs/RELIABILITY.md`
4. Reemplaza declaraciones vagas con redacción operacionalmente útil.
5. Elimina o deprecia copias obsoletas para que el repositorio mantenga una única verdad descubrible.

## Buenas Reglas de Codificación

- Escribe para la descubribilidad, no para la completitud literaria.
- Prefiere documentos cortos con nombres de archivo claros.
- Enlaza artefactos relacionados entre sí.
- Almacena reglas duraderas, no transcripciones de reuniones.
- Actualiza el repositorio en la misma sesión en que se toma la decisión.

## Definición de Completado

- Un agente nuevo puede descubrir la regla relevante sin preguntar a un humano.
- El mismo hecho no está disperso en múltiples archivos contradictorios.
- El nuevo artefacto reside cerca del código o flujo de trabajo que gobierna.
