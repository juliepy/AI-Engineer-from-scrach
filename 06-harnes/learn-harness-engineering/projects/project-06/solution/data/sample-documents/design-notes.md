# Software Design Notes

## Architecture Overview

The knowledge base application follows a layered architecture pattern with clear separation of concerns. The system is divided into four primary layers: the main process, preload scripts, the renderer layer, and services.

## Main Process

The main process is responsible for window management, IPC handler registration, and lifecycle management. It serves as the entry point for the Electron application and coordinates between the operating system and the renderer process.

Key responsibilities:
- BrowserWindow creation and configuration
- IPC channel registration
- Service initialization and dependency injection
- Application lifecycle events (ready, window-all-closed, activate)

## Preload Layer

The preload script acts as a secure bridge between the main and renderer processes. It uses Electron's contextBridge to expose a typed API to the renderer without granting full Node.js access.

The exposed API is organized into namespaces:
- `documents` - CRUD operations for document management
- `indexing` - Document chunking and index management
- `qa` - Question answering with citations
- `feedback` - Q&A response rating
- `app` - Application-level operations (reset data)

## Renderer Layer

The renderer uses React with TypeScript to build the user interface. Components communicate exclusively through the preload bridge API, never directly accessing Node.js APIs or the filesystem.

Key components:
- `App.tsx` - Root layout with view mode switching
- `DocumentList` - Sidebar with document browsing
- `DocumentDetail` - Document viewer with indexing controls
- `ConversationHistory` - Chat-style Q&A history with feedback
- `QuestionPanel` - Question input
- `StatusBar` - Index status and metrics

## Services Layer

Business logic lives in service classes that run in the main process:
- `PersistenceService` - Filesystem read/write operations with JSON and text support
- `DocumentService` - Document import, storage, retrieval, and deletion
- `IndexingService` - Text chunking, index building, and status tracking
- `QaService` - Mock Q&A with keyword retrieval, citations, and feedback
- `Logger` - Structured JSON logging for runtime observability

## Data Flow

1. User action in renderer triggers IPC call via preload bridge
2. IPC handler in main process delegates to appropriate service
3. Service performs business logic using persistence layer
4. Each service logs structured events with timestamps and data
5. Result flows back through IPC to renderer for display

## Observability

All services emit structured JSON log entries with:
- ISO 8601 timestamps
- Log level (DEBUG, INFO, WARN, ERROR)
- Service name tag
- Human-readable message
- Optional structured data payload

This enables runtime debugging and post-hoc analysis of application behavior.
