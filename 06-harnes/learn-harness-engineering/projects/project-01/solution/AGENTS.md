# AGENTS.md -- Project 01: Baseline vs Minimal Harness

## Startup Rules

Before writing any code, complete these steps in order:

1. **Read this file completely.** It defines the boundaries and conventions for this project.
2. **Read `docs/ARCHITECTURE.md`** to understand the Electron layer structure.
3. **Read `docs/PRODUCT.md`** to understand the feature requirements.
4. **Run `bash init.sh`** to verify the project builds cleanly. If it fails, fix build errors before proceeding.
5. **Read `feature_list.json`** to see the current state of all features.

## Electron Layer Boundaries

This project has four strict layers. Code must respect these boundaries:

### Main Process (`src/main/`)
- Owns the `BrowserWindow` lifecycle and IPC registration.
- Imports services but never renderer code.
- All filesystem access happens here via services.

### Preload (`src/preload/`)
- The ONLY bridge between main and renderer.
- Uses `contextBridge.exposeInMainWorld` to expose typed APIs.
- Never imports React or renderer code.

### Renderer (`src/renderer/`)
- React + TypeScript UI layer.
- Communicates with main process exclusively through `window.knowledgeBase` API.
- Never imports Node.js modules (`fs`, `path`, `electron`).
- Uses the type declarations in `types.d.ts`.

### Services (`src/services/`)
- Pure TypeScript business logic running in the main process.
- Services may import from `src/shared/` but never from `src/renderer/`.
- Each service receives `PersistenceService` via constructor injection.

## Conventions

- TypeScript strict mode is enabled. No `any` types without a comment explaining why.
- Use named exports (no default exports).
- IPC channel names are defined once in `src/shared/types.ts` (`IPC_CHANNELS`).
- All async operations return Promises; never use synchronous I/O in the renderer.

## Definition of Done

A feature is "done" when all of the following are true:

1. TypeScript compiles without errors (`npm run check`).
2. The app launches and the window is visible (`npm run dev`).
3. The feature appears in `feature_list.json` with status `"pass"` and evidence.
4. The code respects Electron layer boundaries defined above.
5. No console errors during normal operation.

## Working with the Feature List

The `feature_list.json` file is the source of truth for project progress:

- Each feature has a `status`: `"pass"`, `"fail"`, `"not-started"`.
- When implementing a feature, update its status to `"pass"` with evidence.
- If a feature is blocked, set status to `"fail"` with a reason.
- Never delete features from the list.
