[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> Related lectures: [Lecture 05. Keep context alive across sessions](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Lecture 06. Initialize before every agent session](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Template files: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Project 03. Keep the Agent Working Across Session Restarts

## What You Do

Add scope control and verification gates to the agent. Implement document chunking, metadata extraction, indexing progress display, and citation-based Q&A flow. Use `feature_list.json` to track feature status — one feature at a time, no marking as "pass" without verification evidence.

You compare the checked-in starter and solution: the starter has only the early
tracking surface, while the solution adds the stricter restart and handoff
artifacts around the same feature list.

## Tools

- Claude Code or Codex
- Git
- Node.js + Electron

## Harness Mechanism

Progress log + session handoff + multi-session continuity + one-feature-at-a-time verification

## Use the Checked-In Project

Repository path: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Directory | What it contains | What to compare |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Project 02 code with indexing and grounded QA still unfinished. It has a starter [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json), but lacks the final restart/handoff artifacts. | Whether the agent drifts across multiple features or loses state after a restart. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Completed chunking, metadata, index status, and citation-based QA, plus [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md), and [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | Whether each feature has concrete verification evidence before it is marked passing. |

This project is not a generic "multi-session" exercise. The checked-in solution
maps to four specific product features: document chunking, metadata extraction,
indexing status UI, and grounded Q&A with citations.
