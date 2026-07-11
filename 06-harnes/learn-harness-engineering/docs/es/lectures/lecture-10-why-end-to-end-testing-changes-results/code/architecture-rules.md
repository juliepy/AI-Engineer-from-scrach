# Reglas de Arquitectura de Electron

- El código del renderer no puede acceder directamente al sistema de archivos.
- Preload es el único puente entre el renderer y Electron main.
- La lógica de recuperación e indexación vive en módulos de servicio, no en componentes UI.
- El logging debe ser estructurado y emitido desde los límites de servicio.
