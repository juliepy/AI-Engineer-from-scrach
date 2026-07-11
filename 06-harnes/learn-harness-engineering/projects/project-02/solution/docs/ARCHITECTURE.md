# Architecture -- Knowledge Base Electron App

## System Overview

The Knowledge Base is an Electron desktop application built with TypeScript and React. It provides document import with file picker, text indexing with chunking, content viewing, and grounded question answering with citations.

## Layer Diagram

```
+-----------------------------------------------------------+
|                     Renderer (React)                       |
|  App.tsx -> DocumentList, DocumentDetail, ImportPanel,    |
|             QuestionPanel, StatusBar                       |
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

- **Window management**: Creates `BrowserWindow` instances with secure web preferences.
- **IPC registration**: Maps IPC channel names to service methods via `registerIpcHandlers()`.
- **Service initialization**: Constructs all services with dependency injection.

### Preload (`src/preload/`)

The preload script exposes a typed API via `contextBridge`:

```typescript
window.knowledgeBase = {
  documents: { list, import, get, getContent, delete },
  indexing:   { start, status, chunks },
  qa:         { ask, history },
}
```

### Renderer (`src/renderer/`)

React 18 application bundled by Vite:

- `App.tsx` -- Root layout with import toggle, document selection, and Q&A.
- `DocumentList` -- Sidebar listing of imported documents.
- `DocumentDetail` -- Shows metadata, full content, chunks, and delete button.
- `ImportPanel` -- File input for importing .txt and .md documents.
- `QuestionPanel` -- Text input for asking questions.
- `StatusBar` -- Shows index status and document count.

### Services (`src/services/`)

- `PersistenceService` -- Low-level JSON/text file I/O with atomic writes.
- `DocumentService` -- Document CRUD with content storage and cleanup.
- `IndexingService` -- Paragraph-aware chunking (~500 chars) and index management.
- `QaService` -- Mock Q&A with keyword-based retrieval and citations.

## Import Flow

The document import flow demonstrates the full IPC data path:

```
1. User clicks "Import" button in App.tsx
2. ImportPanel renders file input
3. User selects a .txt or .md file
4. ImportPanel calls onImport(file.path)
5. App.tsx calls window.knowledgeBase.documents.import(filePath)
6. Preload bridge invokes ipcRenderer.invoke('documents:import', filePath)
7. ipc-handlers.ts delegates to DocumentService.importDocument(filePath)
8. DocumentService:
   a. Validates the file exists
   b. Reads file content and stats
   c. Creates Document metadata object
   d. Copies file to documents directory via PersistenceService
   e. Stores extracted text content via PersistenceService
   f. Appends to documents-meta.json
9. Result flows back through IPC
10. App.tsx calls refreshDocuments() to update the list
11. DocumentList re-renders with the new document
```

## Content Retrieval Flow

Document content viewing adds a dedicated IPC channel:

```
1. User clicks "View Content" in DocumentDetail
2. DocumentDetail calls window.knowledgeBase.documents.getContent(id)
3. Preload invokes 'documents:get-content' IPC
4. ipc-handlers delegates to DocumentService.getDocumentContent(id)
5. PersistenceService reads content/<id>.txt
6. Content flows back to renderer for display in pre-wrap container
```

## Data Storage

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
