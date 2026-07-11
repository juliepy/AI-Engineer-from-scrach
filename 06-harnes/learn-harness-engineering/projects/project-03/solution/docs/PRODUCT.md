# Product Description -- Knowledge Base

## What Is This?

A desktop application for managing a personal knowledge base. Users import text and Markdown documents via a file picker, the system extracts metadata and indexes them into searchable chunks, and a question-answering interface provides grounded answers with citations and confidence scores.

## Core Features

### Document Management
- Import `.txt` and `.md` files through a file picker in the ImportPanel.
- View document metadata: title, filename, size, import date, word count, line count, file type, paragraph count.
- View full document content in a scrollable text viewer.
- Browse a list of all imported documents in a sidebar panel.
- Delete documents and their associated data (content file, original copy, chunks).

### Metadata Extraction
- On import, automatically extract metadata from document content:
  - Word count
  - Line count
  - File type (txt or md)
  - Paragraph count
  - Character count
- Metadata displayed in DocumentDetail panel alongside other document properties.

### Text Indexing
- Split documents into ~500-character chunks at paragraph boundaries.
- Store chunks with metadata (character count, word count).
- Track indexing status per document and overall.
- Support indexing individual documents or the full library.
- Indexed document count and total chunk count visible in StatusBar.

### Grounded Q&A
- Ask natural language questions about the document library.
- Receive answers with citations pointing to specific document chunks.
- Citations include document title, chunk index, and text excerpt.
- Confidence scores indicate answer reliability (0.85 with citations, 0.30 without).
- Visual distinction between well-grounded and speculative answers.
- Full Q&A history is persisted across sessions.

### Persistence
- All imported documents persist across application restarts.
- Document list loads automatically on application startup.
- Data stored locally in the user's application data directory.

### Status Bar
- Real-time display of index status (idle, indexing, ready, error).
- Color-coded status indicator: gray (idle), yellow (indexing), green (ready), red (error).
- Document count, indexed document count, and total chunk count.
- Last activity timestamp.

## User Interface

```
+------------------+----------------------------------------+
| Header           |                                Refresh |
+------------------+----------------------------------------+
| Document List    | ImportPanel / Document Detail          |
| (sidebar)        |   - Metadata section                   |
|                  |   - View Content button                |
| [+ Import]       |   - Show Chunks toggle                 |
|                  |   - Index Document button              |
|                  |   - Delete button                      |
|                  |                                        |
|                  | Q&A Response                           |
|                  |   - Answer text                        |
|                  |   - Citations with excerpts            |
|                  |   - Confidence indicator               |
+------------------+----------------------------------------+
| Question Input                              [Ask]         |
+-----------------------------------------------------------+
| Status: ready | Docs: 3 | Indexed: 3 | Chunks: 12        |
+-----------------------------------------------------------+
```

## Constraints

- Maximum supported file size: 10 MB.
- Supported formats: `.txt`, `.md`.
- Q&A uses mock patterns with keyword-based retrieval -- no LLM integration in this version.
- All data is local; no network requests.
- Chunking is synchronous and blocking (suitable for documents under 10 MB).
