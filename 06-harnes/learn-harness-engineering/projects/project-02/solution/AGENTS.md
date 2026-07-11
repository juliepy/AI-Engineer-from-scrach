# AGENTS.md -- Project 02: Agent-Readable Workspace

## Startup Rules

Before writing any code, complete these steps in order:

1. **Read this file completely.** It defines the boundaries and conventions for this project.
2. **Read `docs/ARCHITECTURE.md`** to understand the Electron layer structure and import flow.
3. **Read `docs/PRODUCT.md`** to understand the feature requirements.
4. **Run `npm install && npm run check`** to verify the project builds cleanly.
5. **Read `feature_list.json`** to see the current state of all features.

## Docs Hierarchy

The `docs/` directory is organized for agent readability:

```
docs/
  ARCHITECTURE.md   -- Electron layers, data flow, import pipeline
  PRODUCT.md        -- Feature requirements and user-facing behavior
```

When adding new features, update the relevant doc before writing code. This helps agents understand what has changed between sessions.

## Electron Layer Boundaries

### Main Process (`src/main/`)
- Owns BrowserWindow lifecycle and IPC registration.
- All filesystem access happens here via services.

### Preload (`src/preload/`)
- The ONLY bridge between main and renderer.
- Uses `contextBridge.exposeInMainWorld` to expose typed APIs.

### Renderer (`src/renderer/`)
- React + TypeScript UI layer.
- Communicates exclusively through `window.knowledgeBase` API.
- Never imports Node.js modules.

### Services (`src/services/`)
- Pure TypeScript business logic in the main process.
- Constructor-injected `PersistenceService`.

## Conventions

- TypeScript strict mode. No `any` without a comment explaining why.
- Named exports only.
- IPC channels defined once in `src/shared/types.ts`.
- New IPC channels follow the pattern: `namespace:action` (e.g., `documents:get-content`).

## Definition of Done

A feature is "done" when:

1. TypeScript compiles without errors (`npm run check`).
2. The app launches and the window is visible.
3. The feature appears in `feature_list.json` with status `"pass"` and evidence.
4. The code respects Electron layer boundaries.
5. `docs/ARCHITECTURE.md` and/or `docs/PRODUCT.md` are updated to reflect the change.

## Session Handoff

When resuming work, read `session-handoff.md` for context from the previous session. When finishing a session, update it with:

- What was accomplished
- What remains
- Any blockers or decisions made
- Files that were modified
