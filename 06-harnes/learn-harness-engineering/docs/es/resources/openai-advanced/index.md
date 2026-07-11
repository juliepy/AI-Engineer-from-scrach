# Pack Avanzado de OpenAI

Esta carpeta empaqueta la estructura de repositorio más opinionada descrita en
el artículo de OpenAI "Harness engineering: leveraging Codex in an agent-first world"
en archivos de inicio listos para copiar.

Usa este pack cuando el harness mínimo ya no sea suficiente y tu repositorio
ahora necesite:

- un `AGENTS.md` corto estilo enrutador
- docs duraderos de sistema de registro dentro del repositorio
- planes de ejecución activos y completados
- archivos explícitos de políticas de producto, fiabilidad, seguridad y frontend
- puntuación de calidad por dominio de producto y capa arquitectónica
- carpetas de material de referencia amigable para modelos
- procedimientos operativos estándar para arquitectura, captura de conocimiento y validación en runtime

## Diseño de Inicio Incluido

El pack de inicio en [`repo-template/`](./repo-template/index.md) refleja la
siguiente estructura:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Cómo Adoptarlo

1. Comienza con el pack mínimo si tu repositorio aún es pequeño.
2. Copia los archivos en [`repo-template/`](./repo-template/index.md) a tu
   propio repositorio cuando necesites una estructura más fuerte.
3. Mantén `AGENTS.md` corto. Trátalo como un enrutador hacia los docs más profundos, no como una enciclopedia.
4. Actualiza los docs de calidad, fiabilidad y planes como parte del trabajo normal, no como un día de limpieza separado.
5. Mantén los artefactos generados y las referencias externas explícitos para que los agentes puedan encontrarlos sin depender del historial de chat.

## Biblioteca de SOPs

La carpeta [`sops/`](./sops/index.md) convierte los diagramas del artículo en
procedimientos operativos paso a paso:

- configuración de arquitectura de dominios por capas
- codificación de conocimiento no visto en el repositorio
- stack de observabilidad local y flujo de trabajo de bucle de retroalimentación
- bucle de validación con Chrome DevTools para trabajo de UI

## Principios de Diseño

- Punto de entrada corto, docs más profundos enlazados
- Repositorio como sistema de registro
- Verificaciones mecánicas sobre reglas memorizadas
- Planes e historial de calidad viven junto al código
- Limpieza y simplificación son responsabilidades de primera clase

Este pack es intencionalmente opinionado, pero debe adaptarse a tu proyecto en lugar de copiarse a ciegas.
