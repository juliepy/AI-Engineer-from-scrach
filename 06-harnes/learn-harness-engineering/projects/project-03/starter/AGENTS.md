# AGENTS.md -- Project 03: Multi-Session Continuity with Scope Control

## Quick Start

1. Run `npm install && npm run check` to verify the build.
2. Read `docs/ARCHITECTURE.md` for layer structure.
3. Read `docs/PRODUCT.md` for feature requirements.
4. Check `feature_list.json` for what needs to be done.

## Layers

- Main: `src/main/` -- window, IPC, services
- Preload: `src/preload/` -- bridge API
- Renderer: `src/renderer/` -- React UI
- Services: `src/services/` -- business logic

## Conventions

- TypeScript strict mode. No `any` without comment.
- Named exports only.
- IPC channels in `src/shared/types.ts`.

## Features to Implement

The new features for this project are:

1. **Document Chunking** -- IndexingService splits documents into ~500 char chunks
2. **Metadata Extraction** -- Extract word count, line count, file type on import
3. **Indexing Status UI** -- StatusBar shows indexing progress with counts
4. **Grounded Q&A** -- QaService returns answers with citations and confidence

Check `feature_list.json` for current status.

## Definition of Done

A feature is "done" when:

1. TypeScript compiles without errors (`npm run check`).
2. The app launches and the feature works.
3. The feature appears in `feature_list.json` with status `"pass"` and evidence.

## Session Handoff

When resuming work, first check whether `session-handoff.md` exists. The starter
does not include it by default; if it is missing, reconstruct state from
`feature_list.json`, `docs/ARCHITECTURE.md`, `docs/PRODUCT.md`, and the current
git diff.
