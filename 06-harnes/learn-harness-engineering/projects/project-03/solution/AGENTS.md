# AGENTS.md -- Project 03: Multi-Session Continuity with Scope Control

## Startup Rules

Before writing any code, complete these steps in order:

1. **Read this file completely.** It defines the boundaries and conventions for this project.
2. **Read `docs/ARCHITECTURE.md`** to understand the Electron layer structure, chunking, and Q&A flow.
3. **Read `docs/PRODUCT.md`** to understand the feature requirements.
4. **Run `npm install && npm run check`** to verify the project builds cleanly.
5. **Read `feature_list.json`** to see the current state of all features.

## One-Feature-at-a-Time Policy

**This is the core discipline of Project 03.**

When implementing features, you MUST follow this workflow:

1. **Pick exactly one feature** from `feature_list.json` with status `"not-started"`.
2. **Implement only that feature.** Do not touch code unrelated to the chosen feature.
3. **Verify the feature works** by running `npm run check` and testing the behavior.
4. **Update `feature_list.json`** -- set the feature status to `"pass"` and add evidence.
5. **Commit the change** with a message referencing the feature ID.
6. **Only then** move to the next feature.

Violating this policy -- implementing multiple features in a single pass, or editing files outside the scope of the current feature -- is the most common cause of bugs and regression in this project.

### Feature Dependencies

```
metadata-extraction  -->  document-chunking  -->  indexing-status-ui
                                                  |
                                                  v
                                           grounded-qa
```

- `metadata-extraction` must be done before `document-chunking` (chunks need metadata).
- `document-chunking` must be done before `indexing-status-ui` (status tracks chunks).
- `document-chunking` must be done before `grounded-qa` (Q&A needs indexed chunks).
- `indexing-status-ui` and `grounded-qa` can be done in either order after chunking.

## Docs Hierarchy

The `docs/` directory is organized for agent readability:

```
docs/
  ARCHITECTURE.md   -- Electron layers, data flow, chunking pipeline, Q&A flow
  PRODUCT.md        -- Feature requirements and user-facing behavior
```

When adding new features, update the relevant doc before writing code.

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
- New IPC channels follow the pattern: `namespace:action`.

## Clean State Checklist

Before declaring the project complete, verify every item in `clean-state-checklist.md`.

## Session Handoff

When resuming work, read `session-handoff.md` for context from the previous session. When finishing a session, update it with:

- What was accomplished
- What remains
- Any blockers or decisions made
- Files that were modified
