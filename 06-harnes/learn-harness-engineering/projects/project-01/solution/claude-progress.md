# claude-progress.md -- Session Log

## Project 01: Baseline vs Minimal Harness

### Session 1 -- 2026-03-30

**Duration**: ~45 minutes
**Goal**: Establish baseline Electron app with proper harness

**What was done**:
- Verified Electron window launches at 1200x800 with correct webPreferences
- Confirmed document list panel renders with empty state message
- Confirmed question panel accepts input and submits via IPC
- Verified PersistenceService creates data directories under userData
- Updated feature_list.json with all 4 features at status "pass"
- Wrote AGENTS.md with startup rules and layer boundaries
- Wrote docs/ARCHITECTURE.md describing Electron layer structure
- Wrote docs/PRODUCT.md describing knowledge base requirements

**Decisions**:
- Used constructor injection for PersistenceService to keep services testable
- Kept all IPC channel names in a single const object in types.ts
- Window title set to "Knowledge Base" for consistency

**Issues**: None

**Next session**: Proceed to Project 02 to add import, detail view, and persistence features.
