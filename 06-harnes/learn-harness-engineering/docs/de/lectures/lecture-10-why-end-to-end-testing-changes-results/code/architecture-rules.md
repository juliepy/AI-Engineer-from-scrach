# Electron-Architekturregeln

- Renderer-Code darf nicht direkt auf das Dateisystem zugreifen.
- Preload ist die einzige Brücke zwischen Renderer und Electron Main.
- Retrieval- und Indexierungslogik leben in Service-Modulen, nicht in UI-Komponenten.
- Logging sollte strukturiert sein und von Service-Grenzen ausgehen.
