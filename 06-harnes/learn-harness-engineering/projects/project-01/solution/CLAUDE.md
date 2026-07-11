# CLAUDE.md -- Quick Reference for Claude Code

## Project Overview

This is an Electron + TypeScript + React knowledge base application. The codebase is structured into four layers: main process, preload, renderer, and services.

## Build & Run

```bash
npm install        # Install dependencies
npm run check      # Type-check without emitting
npm run build      # Compile main/preload + bundle renderer
npm run dev        # Build + launch Electron
```

## Key Files

| File | Purpose |
|------|---------|
| `src/main/main.ts` | Electron entry point, window creation, service wiring |
| `src/main/ipc-handlers.ts` | IPC channel registration |
| `src/preload/preload.ts` | contextBridge API exposure |
| `src/renderer/App.tsx` | Root React component |
| `src/services/*.ts` | Business logic (document, indexing, QA, persistence) |
| `src/shared/types.ts` | Shared types and IPC channel constants |
| `feature_list.json` | Feature tracking with pass/fail status |

## Architecture Rules

- Renderer never imports Node.js modules.
- All main-renderer communication goes through IPC.
- Services use constructor-injected `PersistenceService`.
- IPC channel names live in `src/shared/types.ts`.

## How to Add a Feature

1. Define the IPC channel in `src/shared/types.ts`.
2. Add the handler in `src/main/ipc-handlers.ts`.
3. Expose the API in `src/preload/preload.ts`.
4. Add the type declaration in `src/renderer/types.d.ts`.
5. Build the UI in `src/renderer/components/`.
6. Update `feature_list.json` with the result.

## Testing

```bash
npm test           # Run vitest suite
npm run test:watch # Run tests in watch mode
```
