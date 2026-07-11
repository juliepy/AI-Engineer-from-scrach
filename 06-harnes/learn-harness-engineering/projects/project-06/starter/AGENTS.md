# AGENTS.md -- Project 06: Runtime Observability and Debugging (Capstone)

## Startup Rules

1. Read this file.
2. Run `npm install && npm run check` to verify the build.
3. The app should launch with `npm run dev`.

## Project Description

This is the capstone project for the Learn Harness Engineering course. It combines all features from previous projects:
- Document import, indexing, and Q&A
- Conversation history view
- Clean state management for testing

This starter intentionally has a weak harness surface. It does not include
`CLAUDE.md`, `feature_list.json`, `init.sh`, `session-handoff.md`, benchmark
scripts, or cleanup scripts. Use it as the baseline for comparison with
`../solution/`.

## What to Evaluate or Improve

The baseline should be evaluated against the solution on:

1. ConversationHistory completeness
2. Feedback buttons on Q&A responses (thumbs up/down)
3. Structured logging coverage
4. Clean state reset behavior
5. Harness artifacts and benchmark automation that exist in `../solution/`

## Conventions

- TypeScript strict mode.
- Named exports only.
- IPC channels defined in `src/shared/types.ts`.
- Services use constructor-injected `PersistenceService`.
