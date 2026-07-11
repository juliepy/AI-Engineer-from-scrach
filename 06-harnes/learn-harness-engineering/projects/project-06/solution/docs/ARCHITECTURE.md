# Architecture -- Knowledge Base Electron App (Capstone)

## System Overview

The Knowledge Base is an Electron desktop application built with TypeScript and React. It provides document import, text indexing with chunking, content viewing, grounded question answering with citations, feedback collection, conversation history, and runtime observability through structured logging.

This is the capstone project combining all features from the Learn Harness Engineering course.

## Layer Diagram

```
+-----------------------------------------------------------+
|                     Renderer (React)                       |
|  App.tsx -> DocumentList, DocumentDetail, ImportPanel,    |
|             QuestionPanel, ConversationHistory, StatusBar  |
+-----------------------------------------------------------+
         |  window.knowledgeBase.* (typed IPC bridge)
+-----------------------------------------------------------+
|                     Preload Script                         |
|  contextBridge.exposeInMainWorld ->                       |
|    documents, indexing, qa, feedback, app                  |
+-----------------------------------------------------------+
         |  ipcRenderer.invoke(IPC_CHANNELS.*)
+-----------------------------------------------------------+
|                     Main Process                           |
|  main.ts -> createWindow(), initializeServices()          |
|  ipc-handlers.ts -> registerIpcHandlers() (14 channels)   |
+-----------------------------------------------------------+
         |  Service method calls
+-----------------------------------------------------------+
|                     Services Layer                         |
|  DocumentService | IndexingService | QaService             |
|  PersistenceService (filesystem I/O)                       |
|  Logger (structured JSON output)                           |
+-----------------------------------------------------------+
```

## Electron Layers

### Main Process (`src/main/`)

- **Window management**: Creates `BrowserWindow` instances with secure web preferences.
- **IPC registration**: Maps 14 IPC channel names to service methods via `registerIpcHandlers()`.
- **Service initialization**: Constructs all services with dependency injection.
- **Logging**: Logs application lifecycle events (ready, shutdown).

### Preload (`src/preload/`)

The preload script exposes a typed API via `contextBridge`:

```typescript
window.knowledgeBase = {
  documents: { list, import, get, delete },
  indexing:   { start, status, chunks },
  qa:         { ask, history, clearHistory },
  feedback:   { submit, list },
  app:        { resetData },
}
```

### Renderer (`src/renderer/`)

React 18 application bundled by Vite:

- `App.tsx` -- Root layout with view mode switching (documents/history), reset button.
- `DocumentList` -- Sidebar listing of imported documents with status and chunk counts.
- `DocumentDetail` -- Shows metadata, chunks, indexing controls, and delete button.
- `ImportPanel` -- File input for importing .txt and .md documents.
- `QuestionPanel` -- Text input for asking questions.
- `ConversationHistory` -- Chat-style Q&A history with expandable citations, confidence indicators, feedback buttons, and clear history.
- `StatusBar` -- Shows index status, document count, indexed count, and last activity.

### Services (`src/services/`)

- `Logger` -- Structured JSON logging with DEBUG/INFO/WARN/ERROR levels, service tags, and data payloads.
- `PersistenceService` -- Low-level JSON/text file I/O with atomic writes and reset capability.
- `DocumentService` -- Document CRUD with validation, content storage, and cleanup.
- `IndexingService` -- Paragraph-aware chunking (~500 chars), index management, and metrics.
- `QaService` -- Mock Q&A with keyword retrieval, citations, feedback, and duration tracking.

## Full Data Flow

### Document Import Flow

```
1. User selects file via ImportPanel
2. App.tsx calls window.knowledgeBase.documents.import(filePath)
3. Preload bridge invokes ipcRenderer.invoke('documents:import', filePath)
4. ipc-handlers.ts delegates to DocumentService.importDocument(filePath)
5. DocumentService:
   a. Validates file exists and is under 10MB
   b. Reads file content and stats
   c. Creates Document metadata object with UUID
   d. Copies file to documents directory via PersistenceService
   e. Stores extracted text content via PersistenceService
   f. Appends to documents-meta.json
   g. Logs structured event with documentId, filename, size
6. Result flows back through IPC
7. App.tsx calls refreshDocuments() to update the list
```

### Q&A Flow with Observability

```
1. User types question in QuestionPanel
2. App.tsx calls window.knowledgeBase.qa.ask(question)
3. QaService.ask():
   a. Logs question with length
   b. Simulates processing delay (100-500ms)
   c. Gets all chunks from IndexingService
   d. Tokenizes question into keywords (length > 2)
   e. Scores each chunk by keyword overlap count
   f. Selects top 2 chunks as citations
   g. Generates answer from mock patterns or fallback
   h. Creates QAResponse with confidence score
   i. Saves to qa-history.json
   j. Logs answer with confidence, citationCount, durationMs
4. Result flows to renderer
5. App.tsx displays answer with citations and feedback buttons
```

### Feedback Flow

```
1. User clicks thumbs up/down on a response
2. App.tsx calls window.knowledgeBase.feedback.submit(timestamp, question, rating)
3. QaService.submitFeedback():
   a. Creates FeedbackEntry with UUID, timestamp, rating
   b. Appends to feedback.json
   c. Logs structured event
4. Feedback persists across sessions
```

### Clean State Reset Flow

```
1. User clicks Reset button in header
2. Confirmation dialog appears
3. App.tsx calls window.knowledgeBase.app.resetData()
4. PersistenceService.resetAll():
   a. Removes entire data directory (rmSync recursive)
   b. Recreates directory structure
   c. Logs reset event
5. App.tsx clears all React state
6. refreshDocuments() reloads empty state
```

## IPC Channels (14 total)

| Channel | Direction | Handler | Purpose |
|---------|-----------|---------|---------|
| `documents:list` | R -> M | DocumentService.listDocuments | List all documents |
| `documents:import` | R -> M | DocumentService.importDocument | Import a file |
| `documents:get` | R -> M | DocumentService.getDocument | Get document by ID |
| `documents:delete` | R -> M | DocumentService.deleteDocument | Delete document |
| `indexing:start` | R -> M | IndexingService.startIndexing | Start indexing |
| `indexing:status` | R -> M | IndexingService.getStatus | Get indexing status |
| `indexing:chunks` | R -> M | IndexingService.getChunksForDocument | Get chunks |
| `qa:ask` | R -> M | QaService.ask | Ask a question |
| `qa:history` | R -> M | QaService.getHistory | Get Q&A history |
| `qa:clear-history` | R -> M | QaService.clearHistory | Clear history |
| `feedback:submit` | R -> M | QaService.submitFeedback | Submit feedback |
| `feedback:list` | R -> M | QaService.getFeedback | Get all feedback |
| `app:reset` | R -> M | PersistenceService.resetAll | Reset all data |
| `app:status` | R -> M | IndexingService.getStatus | Get app status |

## Data Storage

```
knowledge-base-data/
  documents-meta.json     # Document metadata array
  content/
    <doc-id>.txt          # Extracted text content per document
  documents/
    <filename>            # Original file copies
  chunks/
    <doc-id>.json         # Chunk array per document
  index/
    index-meta.json       # Mapping of document IDs to chunk IDs
  qa-history.json         # Q&A interaction log
  feedback.json           # Feedback entries
```

## Logging

All log entries follow this JSON structure:

```json
{
  "timestamp": "2026-03-30T12:00:00.000Z",
  "level": "INFO",
  "service": "document-service",
  "message": "Document imported successfully",
  "data": {
    "documentId": "abc-123",
    "filename": "design-notes.md",
    "sizeBytes": 2048,
    "contentLength": 1980,
    "totalDocuments": 3
  }
}
```

Log levels:
- **DEBUG**: Routine data access (listing, reading files, chunk retrieval)
- **INFO**: Significant events (import, indexing, Q&A, feedback, reset)
- **WARN**: Missing but non-critical data (skipped documents, content not found)
- **ERROR**: Failures (file not found, parse errors)
