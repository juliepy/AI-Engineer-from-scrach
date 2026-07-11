[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Related lectures: [Lecture 07. Draw clear task boundaries for agents](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Lecture 08. Use feature lists to constrain what the agent does](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Template files: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Project 04. Use Runtime Feedback to Correct Agent Behavior

## What You Do

Add runtime observability (startup logs, import/indexing logs, error states) and architecture constraints to prevent cross-layer violations. Plant a runtime bug for the agent to fix.

You compare the checked-in starter and solution: the starter has weak diagnostics
and no architecture guard script, while the solution adds structured logs,
boundary checks, and the bug fix.

## Tools

- Claude Code or Codex
- Git
- Node.js + Electron

## Harness Mechanism

Runtime feedback + scope control + incremental indexing

## Use the Checked-In Project

Repository path: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Directory | What it contains | What to compare |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Project 03 code with weak diagnostics. A seeded indexing defect can make large-file chunking fail, and there is no architecture-check script. | How long the agent takes to find the root cause without runtime signals. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Structured logger, architecture boundary docs and script, fixed chunking logic, and [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Whether logs and boundary checks make the fix faster and less invasive. |

The concrete files to inspect are [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts),
[`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh),
[`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), and
[`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).
