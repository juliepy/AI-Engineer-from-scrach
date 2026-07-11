# Calibración de Prompts

Las instrucciones raíz deben definir el marco operacional, no cada movimiento posible.

## Mantener En El Archivo Raíz

- propósito y alcance del repositorio
- ruta de inicio
- ruta de verificación
- restricciones no negociables
- artefactos de estado requeridos
- reglas de fin de sesión

## Sacar Del Archivo Raíz

- casos límite históricos largos
- detalles de implementación específicos de un tema
- notas de arquitectura local que pertenecen cerca del código
- ejemplos que solo aplican a un subsistema

## Regla de Trabajo

El archivo raíz debería ayudar a una sesión nueva a orientarse rápidamente. Si el archivo
se está convirtiendo en un depósito para cada fallo pasado, divide el detalle en documentos
más pequeños y enlázalos en su lugar.
