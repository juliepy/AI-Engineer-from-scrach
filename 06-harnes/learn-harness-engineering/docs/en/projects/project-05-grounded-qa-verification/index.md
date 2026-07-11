[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Related lectures: [Lecture 09. Stop agents from declaring victory early](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Lecture 10. Only a full-pipeline run counts as real verification](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Template files: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Project 05. Make the Agent Verify Its Own Work

## What You Do

Implement role separation — a generator that implements, an evaluator that reviews, and optionally a planner. Run three times to measure the effect of each added role.

Choose a substantive feature upgrade (multi-turn conversation, citation panel redesign, or document filtering) and keep it consistent across all runs.

## Tools

- Claude Code or Codex
- Git
- Node.js + Electron

## Harness Mechanism

Self-verification + grounded Q&A + evidence-based completion

## Use the Checked-In Project

Repository path: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Directory | What it contains | What to compare |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Project 04-based app before the conversation-history upgrade. | Starting point if you want to rerun the three variants yourself. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | One agent plans, implements, and self-reviews. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md) score 1.6/5 and listed defects. |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Generator plus evaluator with revision evidence. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md) score 3.3/5 and revision notes. |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planner plus generator plus evaluator. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md), [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md) score 4.9/5. |

The checked-in feature is multi-turn Q&A conversation history. Keep that feature
constant across all three variants so the only variable is role separation.
