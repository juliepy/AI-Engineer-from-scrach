# Architecture -- Knowledge Base Electron App

## System Overview

The Knowledge Base is an Electron desktop application built with TypeScript and React. It provides document import with file picker, metadata extraction, text indexing with paragraph-aware chunking, content viewing, and grounded question answering with citations and confidence scores.

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
- **Service initialization**: Constructs all services with dependency injection. The `IndexingService` is shared between `ipc-handlers` and `QaService` so that Q&A can retrieve chunks.

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

- `App.tsx` -- Root layout with import toggle, document selection, Q&A, and status polling.
- `DocumentList` -- Sidebar listing of imported documents.
- `DocumentDetail` -- Shows metadata (including extracted word/line/paragraph counts), full content, chunks, and indexing controls.
- `ImportPanel` -- File input for importing .txt and .md documents.
- `QuestionPanel` -- Text input for asking questions.
- `StatusBar` -- Shows index status (color-coded), document count, indexed count, total chunks.

### Services (`src/services/`)

- `PersistenceService` -- Low-level JSON/text file I/O with atomic writes.
- `DocumentService` -- Document CRUD with content storage, metadata extraction, and cleanup.
- `IndexingService` -- Paragraph-aware chunking (~500 chars) and index management.
- `QaService` -- Mock Q&A with keyword-based retrieval and citation generation.

## Import Flow with Metadata Extraction

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
   c. Extracts metadata: wordCount, lineCount, fileType, paragraphCount, charCount
   d. Creates Document metadata object with extracted metadata
   e. Copies file to documents directory via PersistenceService
   f. Stores extracted text content via PersistenceService
   g. Appends to documents-meta.json
9. Result flows back through IPC
10. App.tsx calls refreshDocuments() to update the list
11. DocumentList re-renders with the new document
```

## Chunking Pipeline

The indexing pipeline processes document content into searchable chunks:

```
1. User clicks "Index Document" in DocumentDetail (or app indexes all)
2. IPC call: indexing:start(documentId)
3. IndexingService.startIndexing(documentId):
   a. Read content from content/<docId>.txt
   b. Split on double newlines (paragraph boundaries)
   c. Merge short paragraphs until buffer reaches ~500 characters
   d. Create Chunk objects with metadata (charCount, wordCount)
   e. Write chunks to chunks/<docId>.json
   f. Update index-meta.json with chunk IDs
4. Return updated IndexStatus to renderer
5. StatusBar reflects new indexing state
```

### Chunking Algorithm

```
function chunkDocument(documentId, content):
  paragraphs = split on /\n\s*\n/
  buffer = ''
  chunkIndex = 0
  
  for each paragraph:
    if buffer.length + paragraph.length > 500 AND buffer.length > 0:
      emit chunk(buffer, chunkIndex++)
      buffer = paragraph
    else:
      buffer += paragraph
  
  if buffer not empty:
    emit chunk(buffer, chunkIndex)
```

## Grounded Q&A Flow

The Q&A service retrieves relevant chunks and generates grounded answers:

```
1. User types question in QuestionPanel, clicks "Ask"
2. IPC call: qa:ask(question)
3. QaService.ask(question):
   a. Simulate processing delay (100-500ms)
   b. Retrieve all chunks from IndexingService.getAllChunks()
   c. Tokenize question into words (filter < 3 chars)
   d. Score each chunk by keyword overlap count
   e. Take top 2 scored chunks as citations
   f. Look up document titles for citations
   g. Generate answer from mock patterns or fallback
   h. Compute confidence (0.85 with citations, 0.30 without)
   i. Save to qa-history.json
4. Return QAResponse to renderer
5. App.tsx displays answer with citations panel
```

### Citation Format

Each citation includes:
- `documentId` -- Reference to the source document
- `documentTitle` -- Human-readable document name
- `chunkIndex` -- Position of the chunk within the document
- `excerpt` -- First 200 characters of the chunk content

## Content Retrieval Flow

```
1. User clicks "View Content" in DocumentDetail
2. DocumentDetail calls window.knowledgeBase.documents.getContent(id)
3. Preload invokes 'documents:get-content' IPC
4. ipc-handlers delegates to DocumentService.getDocumentContent(id)
5. PersistenceService reads content/<id>.txt
6. Content flows back to renderer for display in pre-wrap container
```

## Data Storage

All user data is stored under `app.getPath('userData')/knowledge-base-data/`:

```
knowledge-base-data/
  documents-meta.json     # Document metadata array (includes extracted metadata)
  content/
    <doc-id>.txt          # Extracted text content per document
  chunks/
    <doc-id>.json         # Chunk array per document
  index/
    index-meta.json       # Mapping of document IDs to chunk IDs
  qa-history.json         # Q&A interaction log
```

## Build Pipeline

1. `tsc -p tsconfig.node.json` compiles main, preload, shared, and services to `dist/`.
2. `vite build` bundles the renderer React app to `dist/renderer/`.
3. Electron loads `dist/main/main.js` as the entry point.
