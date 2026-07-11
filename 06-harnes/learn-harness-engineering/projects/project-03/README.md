# Project 03: Multi-Session Continuity with Scope Control

Evaluate whether progress logs, session handoff, explicit scope control, and
verification gates improve delivery accuracy across restarts.

## Directory Guide

| Directory | Meaning |
|------|------|
| `starter/` | **Starting point**: based on the P2 solution, with document chunking, metadata extraction, index status, and grounded QA still to implement. It has a starter `feature_list.json`, but lacks the full restart harness (`init.sh`, `session-handoff.md`, `claude-progress.md`, clean-state checklist). |
| `solution/` | **Reference implementation**: all features are implemented. AGENTS.md includes the "one feature at a time" strategy, and the repo adds restart/continuity artifacts (`init.sh`, `session-handoff.md`, `claude-progress.md`, `clean-state-checklist.md`). |

## How to Use

```sh
cd starter
npm install
# Run at least two agent sessions. Stop once mid-task, then resume from repo state.
# Observe whether the agent preserves scope and updates feature_list.json.

cd ../solution
npm install
# Inspect the completed continuity artifacts and feature evidence.
```

## Exact Task Contract

The Project 03 starter is not an empty app. It is Project 02 plus unfinished
indexing and grounded QA work. Complete these items one at a time:

| Feature / artifact | Starter state | Solution evidence |
|------|------|------|
| Document chunking | `IndexingService` needs paragraph-aware chunk creation | `src/services/indexing-service.ts`, `feature_list.json` item `document-chunking` |
| Metadata extraction | Document metadata is incomplete for indexing work | `src/services/document-service.ts`, `DocumentDetail.tsx`, item `metadata-extraction` |
| Indexing status UI | Status bar needs indexed count / total chunks / status colors | `src/renderer/components/StatusBar.tsx`, `App.tsx`, item `indexing-status-ui` |
| Grounded Q&A | QA must cite retrieved chunks with excerpts and confidence | `src/services/qa-service.ts`, `QuestionPanel.tsx`, item `grounded-qa` |
| Continuity harness | Starter lacks final restart/handoff artifacts | `init.sh`, `session-handoff.md`, `claude-progress.md`, `clean-state-checklist.md` |

Do not treat this as "add any multi-session feature." The intended product
slice is indexing plus citation-based QA, and the intended harness slice is
restartable progress tracking.

## Features Covered

- Document chunking (paragraph-aware, about 500 characters)
- Metadata extraction (word count, line count, paragraph count)
- Index status displayed in the UI
- Basic QA flow with source citations

## Related Lectures

- [Lecture 05: Why Long-Running Tasks Lose Continuity](../../docs/en/lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md)
- [Lecture 06: Why Initialization Needs Its Own Phase](../../docs/en/lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
