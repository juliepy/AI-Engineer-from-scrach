[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> Related lectures: [Lecture 01. Strong models don't mean reliable execution](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [Lecture 02. What harness actually means](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Template files: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Project 01. Prompt-Only vs. Rules-First: How Much Difference Does It Make

## What You Do

Build a minimal Electron knowledge-base app shell — a window with a document list on the left, a Q&A panel on the right, and a local data directory. The task itself is not complex. What's complex is how you get the agent to complete it.

You run it twice. First time: just a prompt, no preparation. Second time: `AGENTS.md`, `init.sh`, `feature_list.json` pre-placed in the repo. Then compare.

This course scenario uses a short rediscovery/preparation interval as an example, not a fixed measured result.

## Tools

- Claude Code or Codex (pick one, use it for both runs)
- Git (manage branches and compare)
- Node.js + Electron (project stack)
- A timer (record each run's duration)

## Harness Mechanism

Minimal harness: `AGENTS.md` + `init.sh` + `feature_list.json`

## Use the Checked-In Project

Repository path: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Directory | What it contains | How to use it |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | The weak-harness run. It has only [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) as the task description and no `AGENTS.md` or `feature_list.json`. | Give the prompt to your coding agent and measure what it completes without extra structure. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | The same product slice with explicit harness artifacts: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json), and [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | Compare how the same task is made concrete through rules and verification evidence. |

The four concrete features are window launch, document list, question panel, and
local data directory creation. Inspect `solution/feature_list.json` for the
expected evidence for each feature.
