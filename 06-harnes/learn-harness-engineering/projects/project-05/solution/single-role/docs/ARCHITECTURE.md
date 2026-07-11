# Architecture

## Layer Overview

The Knowledge Base application follows a strict layered architecture with four
primary layers. Each layer has well-defined responsibilities and boundaries
that must not be crossed.

```
Renderer (React UI)
    |
    v
Preload (contextBridge)
    |
    v
Main Process (IPC Handlers)
    |
    v
Services (Business Logic)
    |
    v
Persistence (Filesystem)
```

## Layer Boundaries

### Renderer Layer (`src/renderer/`)

**Responsibilities:**
- Render UI components using React
- Handle user input and display results
- Communicate with main process exclusively through `window.knowledgeBase` API

**Constraints:**
- MUST NOT import `fs`, `path`, `os`, `child_process`, or any Node.js core module
- MUST NOT access Electron APIs directly
- MUST NOT contain business logic or data transformation beyond display formatting
- All data access goes through the preload bridge

### Preload Layer (`src/preload/`)

**Responsibilities:**
- Expose a typed API to the renderer via `contextBridge.exposeInMainWorld`
- Map IPC channel names to typed function signatures
- Act as the security boundary between renderer and main process

**Constraints:**
- MUST NOT contain business logic
- MUST NOT import services directly
- Only uses `ipcRenderer.invoke` for communication

### Main Process (`src/main/`)

**Responsibilities:**
- Create and manage BrowserWindow instances
- Register IPC handlers that delegate to services
- Initialize services and manage their lifecycle
- Handle application lifecycle events (ready, activate, window-all-closed)

**Constraints:**
- MUST NOT contain business logic beyond request routing
- Delegates all work to service classes
- Does not directly access persistence layer

### Services Layer (`src/services/`)

**Responsibilities:**
- Implement all business logic (document management, indexing, Q&A)
- Use `PersistenceService` for all filesystem operations
- Use `logger` for structured logging

**Constraints:**
- MUST NOT import Electron APIs (`ipcMain`, `BrowserWindow`, etc.)
- MUST NOT import React or renderer components
- All filesystem access goes through `PersistenceService`

## IPC Channels

All IPC communication uses named channels defined in `src/shared/types.ts`:

| Channel | Direction | Purpose |
|---------|-----------|---------|
| `documents:list` | Renderer -> Main | List all documents |
| `documents:import` | Renderer -> Main | Import a file |
| `documents:get` | Renderer -> Main | Get document by ID |
| `documents:delete` | Renderer -> Main | Delete a document |
| `indexing:start` | Renderer -> Main | Start indexing |
| `indexing:status` | Renderer -> Main | Get indexing status |
| `indexing:chunks` | Renderer -> Main | Get chunks for document |
| `qa:ask` | Renderer -> Main | Ask a question |
| `qa:history` | Renderer -> Main | Get Q&A history |

## Data Flow

1. User action in renderer triggers a call to `window.knowledgeBase.*`
2. Preload bridge converts the call to `ipcRenderer.invoke(channel, ...args)`
3. Main process IPC handler receives the call and delegates to the appropriate service
4. Service executes business logic using PersistenceService for storage
5. Result flows back through IPC to the renderer for display

## Architecture Verification

Run `bash scripts/check-architecture.sh` to verify that no layer boundary
violations exist. This script checks that:
- No `fs` or `path` imports in renderer code
- No Electron IPC imports in service code
- No React imports in services or main process
