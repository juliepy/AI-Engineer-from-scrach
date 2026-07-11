# ARCHITECTURE.md

Este archivo es el mapa de nivel superior del sistema. Debe mantenerse conciso y apuntar
a documentos más profundos cuando sea necesario.

## Forma del sistema

- Producto: `[replace with product name]`
- Flujo de usuario principal: `[replace with main workflow]`
- Superficies de ejecución: `[desktop / web / cli / services / workers]`
- Fuente de verdad para el comportamiento del producto: `docs/product-specs/`

## Mapa de dominios

| Dominio | Propósito | Puntos de entrada principales | Spec relacionada |
|---------|-----------|-------------------------------|------------------|
| `[domain-a]` | `[what it owns]` | `[modules / routes / commands]` | `[spec path]` |
| `[domain-b]` | `[what it owns]` | `[modules / routes / commands]` | `[spec path]` |

## Modelo de capas

Usa un modelo direccional fijo para que los agentes no inventen arquitectura ad hoc:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Las preocupaciones transversales deben entrar a través de límites explícitos de proveedor o
adaptador en lugar de alcanzar directamente a través de las capas.

## Reglas estrictas de dependencia

- Las capas inferiores no deben depender de las capas superiores.
- La UI no debe evadir los contratos de tiempo de ejecución o de servicio.
- El acceso a datos debe ingresar a través de repositorios o adaptadores equivalentes.
- Las utilidades compartidas deben permanecer genéricas y no deben acumular lógica de dominio.
- Las nuevas dependencias deben justificarse en el plan o documento de diseño correspondiente.

## Interfaces transversales

| Preocupación | Límite aprobado | Notas |
|-------------|-----------------|-------|
| Logging y trazabilidad | `[provider / utility path]` | `[structured only, no ad hoc console use]` |
| Autenticación | `[provider path]` | `[token/session rules]` |
| APIs externas | `[client or provider path]` | `[rate limit / retry guidance]` |
| Feature flags | `[flag boundary]` | `[ownership]` |

## Puntos calientes actuales

- `[area that is hardest for agents to change safely]`
- `[area with weak boundaries or fragile tests]`

## Lista de verificación de cambios

Cuando modifiques código relevante para la arquitectura:

1. Actualiza este archivo si el mapa de dominios o los límites permitidos cambiaron.
2. Actualiza el documento de diseño relacionado en `docs/design-docs/` si el razonamiento cambió.
3. Agrega o actualiza una verificación ejecutable si la regla debe aplicarse mecánicamente.
