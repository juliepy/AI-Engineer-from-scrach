# Clean State Checklist

Run this checklist before committing and at the end of each session.

## Build

- [ ] `npm run check` passes with no type errors
- [ ] `npm run build` completes successfully
- [ ] No TypeScript warnings about unused variables or imports

## Architecture

- [ ] No `fs` or `path` imports in renderer code (`src/renderer/`)
- [ ] No Electron IPC in service code (`src/services/`)
- [ ] No React imports in services or main process
- [ ] All IPC channels defined in `src/shared/types.ts`
- [ ] All new APIs exposed in `src/preload/preload.ts`

## Runtime

- [ ] Application starts without errors (`npm run dev`)
- [ ] Structured JSON log output appears in console at startup
- [ ] Document import works (check logs for "Document imported" event)
- [ ] Batch indexing works (check logs for "Batch indexing complete" event)
- [ ] Q&A returns answers with citations (check logs for "Answer generated" event)
- [ ] Conversation history displays in chat-style layout
- [ ] Feedback buttons appear on Q&A responses
- [ ] Reset button clears all data with confirmation dialog
- [ ] Status bar shows correct document count and index status

## Logging

- [ ] All log entries are valid JSON (parseable)
- [ ] Log entries include timestamp, level, service, and message
- [ ] Document import emits INFO log with documentId, filename, size
- [ ] Indexing emits INFO log with chunkCount, durationMs
- [ ] Q&A emits INFO log with confidence, citationCount, durationMs
- [ ] IPC handlers log channel invocations

## Data Integrity

- [ ] No empty chunks in indexed documents (verify with GET_CHUNKS)
- [ ] Q&A history persists across restarts
- [ ] Feedback entries persist across restarts
- [ ] Document metadata is consistent with actual files
- [ ] Clean state reset removes all data files

## Performance

- [ ] `bash scripts/benchmark.sh` runs without errors
- [ ] Import throughput is reasonable (3 files under 1 second)
- [ ] Indexing completes for sample data (under 1 second)
- [ ] Query latency is under 1 second per question

## Repository

- [ ] No unintended files in git status
- [ ] No sensitive data (.env, credentials) staged
- [ ] No files in `dist/` committed
- [ ] `claude-progress.md` updated with current state
- [ ] `feature_list.json` reflects actual feature status
- [ ] `session-handoff.md` updated if session is ending

## Scripts

- [ ] `bash scripts/cleanup-scanner.sh` reports no stale artifacts
- [ ] `bash scripts/benchmark.sh` completes the full task suite
- [ ] `bash init.sh` passes all verification steps
