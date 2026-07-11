# Ejemplo: Convertir Feedback de Review en una Regla

Comentario de review repetido:

> No uses utilidades del sistema de archivos desde el renderer. Usa el puente preload.

Regla de harness promovida:

- añadir una regla de lint o import que prevenga el uso de `fs` en código del renderer
- añadir texto de remediación explicando la frontera de preload
