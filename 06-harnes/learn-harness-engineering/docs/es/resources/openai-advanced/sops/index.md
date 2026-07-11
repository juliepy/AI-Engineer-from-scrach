# SOPs Avanzados de OpenAI

Estos SOPs traducen los patrones operacionales del artículo en playbooks de ejecución concretos
que puedes seguir o adaptar.

## SOPs Incluidos

- [`layered-domain-architecture.md`](./layered-domain-architecture.md):
  establece capas explícitas y límites transversales
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md):
  mueve el conocimiento invisible desde chat, docs y memoria a archivos locales del repositorio
- [`observability-feedback-loop.md`](./observability-feedback-loop.md):
  proporciona a los agentes logs, métricas, trazas y un bucle de depuración repetible
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md):
  usa automatización del navegador y capturas para validar el comportamiento de UI hasta que esté limpio

## Cómo Usarlos

1. Elige el SOP que coincida con tu cuello de botella actual.
2. Usa la lista de verificación para configurar los artefactos o herramientas faltantes.
3. Codifica las reglas resultantes en los docs de tu copia de `repo-template/`.
4. Convierte los comentarios de revisión repetidos en verificaciones, scripts o barreras de protección.

Estos no están pensados para seguirse a ciegas. Están pensados para hacer el harness
más legible, enforcementable y repetible.
