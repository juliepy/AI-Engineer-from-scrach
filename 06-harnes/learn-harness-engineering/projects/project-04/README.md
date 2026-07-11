# Project 04: Runtime Feedback and Structural Control

Introduce runtime observability and structural boundary checks while debugging a seeded runtime defect.

## Directory Guide

| Directory | Meaning |
|------|------|
| `starter/` | **Starting point**: based on the P3 solution, with logging and structural boundary features still to implement. `IndexingService` contains a hidden seeded bug: files longer than 1000 characters can produce empty chunks. There is no architecture-check script and no final clean-state checklist. |
| `solution/` | **Reference implementation**: structured logging module, architecture boundary-check script, and the seeded bug fixed. |

## How to Use

```sh
cd starter
npm install
# 1. Observe whether the agent can locate the bug through logs
# 2. Import a large file and check whether chunking behaves incorrectly

cd ../solution
npm install
# Compare how structured logs speed up diagnosis
```

## Exact Task Contract

Project 04 is a debugging and guardrail exercise. The starter already contains
the Project 03 product slice, but the runtime is harder to inspect and the seeded
chunking defect should be fixed only after the agent can see enough evidence.

| Feature / artifact | Starter state | Solution evidence |
|------|------|------|
| Structured logging | No shared logger service | `src/services/logger.ts`, logging calls in `main.ts`, `ipc-handlers.ts`, and services |
| Import / indexing diagnostics | Failures are hard to trace from runtime output | Log entries around import, indexing start/completion, and QA failure paths |
| Architecture boundaries | No script checks renderer/main/service boundary drift | `scripts/check-architecture.sh`, `docs/ARCHITECTURE.md`, AGENTS boundary rules |
| Seeded chunking bug | Large files can produce invalid/empty chunk output | Fixed `src/services/indexing-service.ts` paragraph/chunk logic |
| Clean handoff | Starter has no final checklist | `clean-state-checklist.md` |

Use a long sample document to reproduce the bug before and after the fix. A
successful solution should show both code changes and diagnostic evidence, not
only a passing claim.

## Features Covered

- Startup logs
- Import and indexing logs
- Visible QA failure path
- Explicit boundaries between main, preload, renderer, and services layers
- Debugging a seeded runtime defect

## Related Lectures

- [Lecture 07: Why Agents Overreach and Under-Finish](../../docs/en/lectures/lecture-07-why-agents-overreach-and-under-finish/index.md)
- [Lecture 08: Why Feature Lists Are Harness Primitives](../../docs/en/lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
