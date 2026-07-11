# Project 05: Evaluator Loops and Three-Role Upgrades

Measure how role separation (single role, generator plus evaluator, planner plus generator plus evaluator) changes implementation quality.

## Directory Guide

| Directory | Meaning |
|------|------|
| `starter/` | **Starting point**: based on the P4 solution, with multi-turn QA history still to implement. |
| `solution/single-role/` | **Variant A**: one agent does all work (planning, implementation, and self-review). Baseline quality. |
| `solution/gen-eval/` | **Variant B**: generator plus evaluator pattern. Higher quality, with revision evidence. |
| `solution/plan-gen-eval/` | **Variant C**: planner plus generator plus evaluator. Highest quality, with a sprint contract and scoring criteria. |

## How to Use

```sh
# Start from starter if you want to run the exercise yourself.
cd starter
npm install
# Implement the same ConversationHistory upgrade three times using the role setup below.

# Inspect the three reference variants independently
cd solution/single-role && npm install  # single-role mode
cd solution/gen-eval && npm install     # generator plus evaluator mode
cd solution/plan-gen-eval && npm install # full three-role mode

# Compare the three variants:
# - Code quality (evaluator-rubric.md score)
# - Number of defects found
# - Amount of rework required
```

## Exact Task Contract

The product upgrade for the checked-in solutions is fixed: implement multi-turn
Q&A history through `ConversationHistory`. The three solution directories are
not sequential stages; they are three independent runs of the same feature with
different harness roles.

| Variant | What it demonstrates | Evidence to inspect |
|------|------|------|
| `starter/` | P4-based app before the conversation-history upgrade | `src/renderer/components/ConversationHistory.tsx`, `App.tsx` |
| `solution/single-role/` | One agent plans, implements, and self-reviews | `evaluator-rubric.md` score 1.6/5 and listed defects |
| `solution/gen-eval/` | Separate generator and evaluator with revision evidence | `evaluator-rubric.md` score 3.3/5 and revision notes |
| `solution/plan-gen-eval/` | Planner + generator + evaluator with a sprint contract | `sprint-contract.md`, `evaluator-rubric.md` score 4.9/5 |

Keep the feature constant when you rerun the project. Changing the feature
between variants invalidates the comparison because role separation is the only
intended variable.

## Features Covered

- Multi-turn QA history (conversational UI)
- Sprint contract
- Evaluator rubric tuning

## Related Lectures

- [Lecture 09: Why Agents Declare Victory Too Early](../../docs/en/lectures/lecture-09-why-agents-declare-victory-too-early/index.md)
- [Lecture 10: Why End-to-End Testing Changes Results](../../docs/en/lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
