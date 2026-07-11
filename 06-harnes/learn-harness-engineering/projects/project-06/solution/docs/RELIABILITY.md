# Reliability -- Observability, Clean State, and Benchmarking

## Structured Logging

### Overview

All services in the application emit structured JSON log entries. This enables runtime debugging, post-hoc analysis, and automated monitoring of application behavior.

### Log Format

Every log entry is a single-line JSON object:

```json
{
  "timestamp": "2026-03-30T12:00:00.000Z",
  "level": "INFO",
  "service": "document-service",
  "message": "Document imported successfully",
  "data": {
    "documentId": "abc-123",
    "filename": "design-notes.md",
    "sizeBytes": 2048
  }
}
```

### Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Routine data access, file reads | "Retrieved chunks for document" |
| INFO | Significant events | "Document imported", "Batch indexing complete" |
| WARN | Missing but non-critical data | "Content not found for document" |
| ERROR | Failures | "File not found during import" |

### Service Logging Points

**PersistenceService:**
- Directory initialization
- File read/write operations (DEBUG)
- Clean state reset (WARN)

**DocumentService:**
- Document import with size and metadata
- Document deletion with remaining count
- Document metadata updates
- File not found errors
- Size limit violations

**IndexingService:**
- Single and batch indexing start
- Per-document indexing progress
- Batch completion with throughput metrics
- Content not found warnings

**QaService:**
- Question processing start
- Answer generation with confidence and duration
- Feedback submission
- History clear

**IPC Handlers:**
- Every channel invocation (INFO for mutations, DEBUG for reads)
- All registered channels at startup

### Configuring Log Level

Set the `LOG_LEVEL` environment variable:
```bash
LOG_LEVEL=INFO npm run dev  # Only INFO, WARN, ERROR
LOG_LEVEL=WARN npm run dev  # Only WARN and ERROR
LOG_LEVEL=ERROR npm run dev # Only ERROR
```

Default: `DEBUG` (all messages).

## Clean State Management

### Purpose

Clean state management ensures that testing and benchmarking start from a known, empty state. This prevents accumulated data from affecting test results or causing unexpected behavior.

### Reset Mechanism

The application provides a `RESET_DATA` IPC channel that:

1. Removes the entire data directory (`knowledge-base-data/`)
2. Recreates the directory structure
3. Returns a success response
4. The renderer clears all React state and refreshes

### When to Use Clean State

- Before running benchmarks
- After a debugging session
- Before testing a new feature
- When the data directory becomes corrupted

### Clean State Verification

Use the `clean-state-checklist.md` to verify:
- Build passes without errors
- Architecture boundaries are respected
- Runtime behavior is correct
- Logging output is as expected
- Data integrity is maintained

## Benchmarking

### Overview

The `scripts/benchmark.sh` script measures application performance across key operations. It uses file-based simulation to test the services layer without launching the Electron window.

### Benchmark Tasks

| Task | What It Measures | Target |
|------|------------------|--------|
| `import` | Document import throughput | 3 files in <1s |
| `index` | Batch indexing speed | 14 chunks in <1s |
| `query` | Q&A response latency | <500ms per question |
| `verify` | Data integrity checks | 0 errors |

### Running Benchmarks

```bash
bash scripts/benchmark.sh
```

Output example:
```
=== Benchmark Results ===
[import] 3 files: 120ms (25.0 files/sec)
[index]  3 documents: 80ms (175.0 chunks/sec)
[query]  5 questions: 1250ms (250.0ms avg)
[verify] Data integrity: PASS
=== Summary: 4/4 tasks passed ===
```

### Interpreting Results

- If import is slow: check file size and disk I/O.
- If indexing is slow: check chunk size and paragraph boundaries.
- If query is slow: check number of chunks and keyword matching.
- If verify fails: run `scripts/cleanup-scanner.sh` to identify issues.

## Cleanup Scanner

### Overview

The `scripts/cleanup-scanner.sh` script checks the data directory for stale or inconsistent artifacts.

### Checks Performed

| Check | Description |
|-------|-------------|
| Orphaned content files | Content files without a matching document in metadata |
| Dangling chunk files | Chunk files without a matching index entry |
| Missing content files | Documents in metadata without a content file |
| Inconsistent metadata | Documents marked as indexed without chunk files |
| Empty data files | JSON files with empty arrays that should have data |
| Stale Q&A history | History entries referencing deleted documents |

### Running the Scanner

```bash
bash scripts/cleanup-scanner.sh
```

Output example:
```
=== Cleanup Scanner ===
[OK] No orphaned content files
[OK] No dangling chunk files
[OK] No missing content files
[OK] All indexed documents have chunk files
[OK] No stale Q&A references
=== Result: CLEAN (0 issues) ===
```
