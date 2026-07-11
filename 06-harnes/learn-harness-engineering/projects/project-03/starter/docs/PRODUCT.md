# Product Description -- Knowledge Base

## What Is This?

A desktop application for managing a personal knowledge base. Users import text and Markdown documents via a file picker, view document content, and the system indexes them into searchable chunks for grounded Q&A with citations.

## Core Features

### Document Management
- Import `.txt` and `.md` files through a file picker in the ImportPanel.
- View document metadata: title, filename, size, import date, indexing status.
- View full document content in a scrollable text viewer.
- Browse a list of all imported documents in a sidebar panel.
- Delete documents and their associated data (content file, original copy).

### Text Indexing
- Split documents into ~500-character chunks at paragraph boundaries.
- Store chunks with metadata (character count, word count).
- Track indexing status per document and overall.
- Support indexing individual documents or the full library.

### Grounded Q&A
- Ask natural language questions about the document library.
- Receive answers with citations pointing to specific document chunks.
- Confidence scores indicate answer reliability (0.85 with citations, 0.30 without).
- Full Q&A history is persisted across sessions.

### Persistence
- All imported documents persist across application restarts.
- Document list loads automatically on application startup.
- Data stored locally in the user's application data directory.

### Status Bar
- Real-time display of index status (idle, indexing, ready, error).
- Document count and last activity timestamp.

## User Interface

```
+------------------+----------------------------------------+
| Header           |                                Refresh |
+------------------+----------------------------------------+
| Document List    | ImportPanel / Document Detail          |
| (sidebar)        |   - View Content button                |
|                  |   - Show Chunks toggle                 |
| [+ Import]       |   - Index Document button              |
|                  |   - Delete button                      |
+------------------+----------------------------------------+
| Question Input                              [Ask]         |
+-----------------------------------------------------------+
| Status: idle | Documents: N                                |
+-----------------------------------------------------------+
```

## Constraints

- Maximum supported file size: 10 MB.
- Supported formats: `.txt`, `.md`.
- Q&A uses mock patterns -- no LLM integration in this version.
- All data is local; no network requests.
