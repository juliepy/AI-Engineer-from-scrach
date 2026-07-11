# Architecture -- Knowledge Base Electron App

## System Overview

The Knowledge Base is an Electron desktop application built with TypeScript and React. It provides document import, text indexing with chunking, and grounded question answering with citations.

## Layer Diagram

```
+-----------------------------------------------------------+
|                     Renderer (React)                       |
|  App.tsx -> DocumentList, DocumentDetail, QuestionPanel,  |
|             StatusBar, ImportPanel                         |
+-----------------------------------------------------------+
         |  window.knowledgeBase.* (typed IPC bridge)
+-----------------------------------------------------------+
|                     Preload Script                         |
|  contextBridge.exposeInMainWorld -> documents, indexing, qa|
+-----------------------------------------------------------+
         |  ipcRenderer.invoke(IPC_CHANNELS.*)
+-----------------------------------------------------------+
|                     Main Process                           |
|  main.ts -> createWindow(), initializeServices()          |
|  ipc-handlers.ts -> registerIpcHandlers()                  |
+-----------------------------------------------------------+
         |  Service method calls
+-----------------------------------------------------------+
|                     Services Layer                         |
|  DocumentService | IndexingService | QaService             |
|  PersistenceService (filesystem I/O)                       |
+-----------------------------------------------------------+
```

## Electron Layers

### Main Process (`src/main/`)

The main process is the Node.js process that manages the application lifecycle. Responsibilities:

- **Window management**: Creates `BrowserWindow` instances with secure web preferences (`contextIsolation: true`, `nodeIntegration: false`).
- **IPC registration**: Maps IPC channel names to service methods via `registerIpcHandlers()`.
- **Service initialization**: Constructs `PersistenceService`, `DocumentService`, `IndexingService`, and `QaService` with dependency injection.

**Key invariant**: The main process never imports React or renderer code.

### Preload (`src/preload/`)

The preload script runs in the renderer context before any page scripts load. It uses Electron's `contextBridge` to expose a limited, typed API:

```typescript
window.knowledgeBase = {
  documents: { list, import, get, delete },
  indexing:   { start, status, chunks },
  qa:         { ask, history },
}
```

**Key invariant**: The preload bridge is the only communication channel between renderer and main. No Node.js modules are accessible from the renderer.

### Renderer (`src/renderer/`)

The renderer is a React 18 application bundled by Vite. Components:

- `App.tsx` -- Root layout with header, sidebar, main panel, and status bar.
- `DocumentList` -- Sidebar listing of imported documents.
- `DocumentDetail` -- Shows document metadata, chunks, and indexing controls.
- `ImportPanel` -- File input for importing .txt and .md documents.
- `QuestionPanel` -- Text input for asking questions.
- `StatusBar` -- Shows index status and document count.

**Key invariant**: Renderer code never imports `fs`, `path`, `electron`, or any Node.js module.

### Services (`src/services/`)

Business logic classes running in the main process:

- `PersistenceService` -- Low-level JSON/text file I/O with atomic writes.
- `DocumentService` -- Document CRUD operations (import, list, get, update, delete).
- `IndexingService` -- Paragraph-aware chunking (~500 chars per chunk) and index management.
- `QaService` -- Mock question answering with keyword-based retrieval and citation generation.

**Key invariant**: Services may import shared types but never renderer code.

## Data Flow

1. User interacts with a React component (e.g., clicks "Ask").
2. Component calls `window.knowledgeBase.qa.ask(question)`.
3. Preload bridge invokes `ipcRenderer.invoke('qa:ask', question)`.
4. Main process IPC handler delegates to `QaService.ask()`.
5. QaService retrieves chunks, scores by keyword overlap, generates answer.
6. Response flows back through IPC to the renderer.
7. React component updates state and re-renders.

## Build Pipeline

1. `tsc -p tsconfig.node.json` compiles main, preload, shared, and services to `dist/`.
2. `vite build` bundles the renderer React app to `dist/renderer/`.
3. Electron loads `dist/main/main.js` as the entry point.

## Data Storage

All user data is stored under `app.getPath('userData')/knowledge-base-data/`:

```
knowledge-base-data/
  documents-meta.json     # Document metadata array
  content/
    <doc-id>.txt          # Extracted text content per document
  chunks/
    <doc-id>.json         # Chunk array per document
  index/
    index-meta.json       # Mapping of document IDs to chunk IDs
  qa-history.json         # Q&A interaction log
```
