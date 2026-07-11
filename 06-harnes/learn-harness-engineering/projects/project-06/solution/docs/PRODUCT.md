# Product Description -- Knowledge Base (Capstone)

## What Is This?

A desktop application for managing a personal knowledge base. Users import text and Markdown documents, the system indexes them into searchable chunks, and provides grounded question answering with citations. Users can view conversation history, provide feedback on answers, and reset the application to a clean state for testing.

## Core Features

### Document Management
- Import `.txt` and `.md` files through a file picker in the ImportPanel.
- File validation: existence check, 10 MB size limit.
- View document metadata: title, filename, size, import date, indexing status.
- View document chunks with metadata (character count, word count).
- Browse a list of all imported documents in a sidebar panel.
- Delete documents and their associated data (content file, original copy).

### Text Indexing
- Split documents into ~500-character chunks at paragraph boundaries.
- Store chunks with metadata (character count, word count).
- Track indexing status per document and overall.
- Support indexing individual documents or the full library.
- Documents automatically marked as "indexed" after chunking.
- Indexing status visible in sidebar and status bar.

### Grounded Q&A
- Ask natural language questions about the document library.
- Receive answers with citations pointing to specific document chunks.
- Confidence scores indicate answer reliability (0.85 with citations, 0.30 without).
- 8 mock answer patterns covering architecture, import, indexing, retrieval, meetings, logging, feedback, and clean state.
- Full Q&A history is persisted across sessions.
- Query latency typically under 500ms.

### Conversation History
- Chat-style display of all Q&A exchanges.
- User questions shown as purple bubbles (right-aligned).
- Assistant answers shown as dark bubbles (left-aligned).
- Expandable citations for each answer.
- Confidence indicator with color coding (green/yellow/red).
- Timestamps on each exchange.
- Clear history with confirmation dialog.

### Feedback Collection
- Thumbs up/down buttons on each Q&A response in conversation history.
- Thumbs up/down buttons on the latest response in document view.
- Feedback persists across sessions.
- Each feedback entry includes: ID, Q&A timestamp, question, rating, optional comment, submission time.

### Clean State Reset
- Reset button in application header.
- Confirmation dialog before reset.
- Clears all documents, chunks, Q&A history, and feedback.
- Application returns to initial empty state.
- Data directory is removed and recreated.

### Persistence
- All data persists across application restarts.
- Document list loads automatically on application startup.
- Data stored locally in the user's application data directory.
- Four data files: documents-meta.json, qa-history.json, feedback.json, index-meta.json.

### Status Bar
- Real-time display of index status (idle, indexing, ready, error).
- Color-coded status indicator.
- Document count.
- Indexed document count.
- Last activity timestamp.

## User Interface

```
+------------------+----------------------------------------+
| Header           | History | Reset | Refresh              |
+------------------+----------------------------------------+
| Document List    | Document Detail / Conversation History |
| (sidebar)        |   - Metadata display                   |
|                  |   - Show Chunks toggle                 |
| [+ Import]       |   - Index Document button              |
|                  |   - Delete button                      |
| doc1 (Indexed)   |                                        |
|   3.2 KB         | Q&A Response:                          |
| doc2 (Imported)  |   Answer text...                       |
|   1.8 KB         |   Citations: [expandable]              |
|                  |   Confidence: high                     |
|                  |   [+1] [-1] feedback                   |
+------------------+----------------------------------------+
| Ask a question...                              [Ask]       |
+-----------------------------------------------------------+
| Status: Ready | Documents: 3 | Indexed: 3 | 12:34 PM     |
+-----------------------------------------------------------+
```

## Constraints

- Maximum supported file size: 10 MB.
- Supported formats: `.txt`, `.md`.
- Q&A uses mock patterns -- no LLM integration.
- All data is local; no network requests.
- Structured logging outputs to console (no file-based logging in this version).

## Performance Targets

- Import throughput: 10+ files per batch under 1 second.
- Indexing speed: 100+ chunks per second.
- Query latency: under 500ms per question.
- Citation accuracy: top 2 chunks must be relevant.
