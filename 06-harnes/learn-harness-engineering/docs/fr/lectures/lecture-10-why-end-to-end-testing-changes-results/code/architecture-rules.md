# Règles d'Architecture Electron

- Le code du renderer ne peut pas accéder directement au système de fichiers.
- Le preload est le seul pont entre le renderer et Electron main.
- La logique de récupération et d'indexation vit dans les modules de service, pas dans les composants UI.
- La journalisation doit être structurée et émise depuis les frontières de service.
