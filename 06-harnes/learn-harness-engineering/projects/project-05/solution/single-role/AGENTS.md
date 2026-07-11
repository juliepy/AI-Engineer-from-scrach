# AGENTS.md

This Project 05 variant demonstrates a single-role implementation of
ConversationHistory. It includes the completed code and evaluator rubric, but it
does not include the full capstone harness files.

## Startup Workflow

Before writing code:

1. Confirm the working directory with `pwd`.
2. Read `docs/ARCHITECTURE.md` for the Electron layer boundaries.
3. Read `evaluator-rubric.md` to understand this variant's quality evidence.
4. Read `clean-state-checklist.md`.
5. Run `npm install` if dependencies are missing.
6. Run `npm run check`.
7. Run `bash scripts/check-architecture.sh`.

If baseline verification is already failing, fix that first. Do not stack new
feature work on top of a broken starting state.

## Working Rules

- Work on one feature at a time.
- Do not mark a feature complete just because code was added.
- Keep changes within the selected feature scope unless a blocker forces a
  narrow supporting fix.
- Do not silently change verification rules during implementation.
- Prefer durable repo artifacts over chat summaries.

## Runtime Observability

All services use structured logging via `src/services/logger.ts`. Log output is
JSON-formatted with timestamp, level, service name, and message. Log levels:
DEBUG, INFO, WARN, ERROR.

When debugging, check logs for:
- Service initialization events at startup
- IPC channel invocations and their parameters
- Indexing chunk counts and content lengths
- Q&A confidence scores and citation counts

## Architecture Constraints

The following layer boundaries are enforced by `scripts/check-architecture.sh`:

- **Renderer** must not import `fs`, `path`, or any Node.js core modules.
- **Services** must not import Electron IPC or renderer-specific modules.
- **Preload** must only expose the typed API via contextBridge.

Run `bash scripts/check-architecture.sh` before committing.

## Required Artifacts

- `AGENTS.md`: operating rules for this project
- `docs/ARCHITECTURE.md`: layer boundaries and data flow
- `scripts/check-architecture.sh`: boundary guard
- `clean-state-checklist.md`: pre-commit repository health check
- `evaluator-rubric.md`: quality evidence for this variant

Do not assume `feature_list.json`, `claude-progress.md`, `init.sh`, or
`session-handoff.md` exist in this variant.

## Definition Of Done

A feature is done only when all of the following are true:

- the target behavior is implemented
- the required verification actually ran
- evidence is recorded in `evaluator-rubric.md` or the final summary
- the repository remains restartable from the standard startup path
- `scripts/check-architecture.sh` passes with no violations

## End Of Session

Before ending a session:

1. Record any unresolved risk or blocker in your final summary.
2. Run `npm run check`.
3. Run `bash scripts/check-architecture.sh`.
4. Commit with a descriptive message once the work is in a safe state.
5. Leave the repo clean enough for the next session to run the startup workflow.
