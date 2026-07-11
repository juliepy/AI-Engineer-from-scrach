# PRODUCT_SENSE.md

Este archivo captura el criterio de producto duradero que los agentes no pueden inferir
confiablemente solo desde el código.

## Núcleo del Producto

- Usuario principal: `[reemplazar]`
- Trabajo por hacer: `[reemplazar]`
- Frustración principal a eliminar: `[reemplazar]`
- Nivel de calidad para aceptación: `[reemplazar]`

## Reglas de Producto

- Favorecer la fiabilidad visible para el usuario sobre la cantidad de funcionalidades.
- Tratar el comportamiento ambiguo como un vacío de especificación, no como permiso para adivinar.
- Si la implementación cambia lo que los usuarios ven o confían, actualizar la spec correspondiente.
- Usar specs de producto para flujos concretos, y usar este archivo para prioridades de producto transversales.

## Patrones de No-Acción

- Acciones destructivas ocultas
- Fallo silencioso sin retroalimentación al usuario
- Fuente de verdad poco clara para estado visible
- Funcionalidades que no se pueden explicar en una sola frase
