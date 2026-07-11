# Product Description -- Knowledge Base

## What Is This?

A desktop application for managing a personal knowledge base. Users import text and Markdown documents, the system indexes them into searchable chunks, and a question-answering interface provides grounded answers with citations.

## Core Features

### Document Management
- Import `.txt` and `.md` files into a local data store.
- View document metadata: title, filename, size, import date, indexing status.
- Browse a list of all imported documents in a sidebar panel.
- Delete documents and their associated data.

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

### Status Bar
- Real-time display of index status (idle, indexing, ready, error).
- Document count and last activity timestamp.

## Technical Requirements

- Runs as a desktop application via Electron.
- No external API dependencies -- all processing is local.
- TypeScript throughout with strict mode.
- React 18 for the UI with a dark theme.
- Data stored locally in the user's application data directory.

## User Interface

The interface has a three-panel layout:

```
+------------------+----------------------------------------+
| Header           |                                Refresh |
+------------------+----------------------------------------+
| Document List    | Document Detail / Welcome              |
| (sidebar)        |                                        |
|                  | Q&A Response                           |
| [+ Import]       |                                        |
+------------------+----------------------------------------+
| Question Input                              [Ask]         |
+-----------------------------------------------------------+
| Status: idle | Documents: 0                                |
+-----------------------------------------------------------+
```

## Constraints

- Maximum supported file size: 10 MB.
- Supported formats: `.txt`, `.md`.
- Q&A uses mock patterns -- no LLM integration in this version.
- All data is local; no network requests.
