# Clean State Checklist -- Project 03

## Build Verification

- [x] `npm install` completes without errors
- [x] `npm run check` passes with zero TypeScript errors
- [x] `npm run build` produces dist/ output

## Feature Verification

- [x] Window launches with correct dimensions and dark theme
- [x] Document list shows imported documents with empty state
- [x] Import button opens file picker, imports .txt and .md files
- [x] Document detail shows metadata: title, filename, size, import date, word count, line count, file type
- [x] "View Content" button loads and displays full document text
- [x] "Show Chunks" button displays chunked content with metadata
- [x] "Index Document" button triggers chunking and updates status
- [x] StatusBar shows index status with color-coded indicator
- [x] StatusBar shows indexed document count and total chunk count
- [x] Question panel accepts questions and returns answers
- [x] Answers include citations with document title, chunk index, and excerpt
- [x] Answers include confidence scores (0.85 with citations, 0.30 without)
- [x] Documents persist across app restarts
- [x] Delete button removes document and associated data

## Scope Control Verification

- [x] feature_list.json shows all features at "pass"
- [x] Each feature has evidence describing what was implemented
- [x] No feature has status "fail" or "not-started"
- [x] AGENTS.md contains one-feature-at-a-time policy
- [x] Feature dependencies are documented and respected

## Code Quality

- [x] No `any` types without explanatory comments
- [x] All exports are named exports
- [x] IPC channels defined in src/shared/types.ts only
- [x] Renderer never imports Node.js modules
- [x] Services never import renderer code
- [x] All new files follow existing conventions

## Documentation

- [x] docs/ARCHITECTURE.md updated with chunking pipeline and Q&A flow
- [x] docs/PRODUCT.md updated with new features
- [x] session-handoff.md filled out
- [x] claude-progress.md has session logs
