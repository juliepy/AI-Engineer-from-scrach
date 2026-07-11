# Ralph example run - CSV export (SCH-142)

A complete, captured Ralph run, kept as a reference (for the video and for anyone learning the loop). This is a **snapshot of what the loop produces**, not a live run. The `DONE.txt` here lives in this subfolder, so it does NOT affect `python ralph/ralph.py` at the repo root.

## What's here

| File | What it is |
|------|-----------|
| `PROMPT.md` | The spec Ralph was given each iteration (copy of `ralph/PROMPT.md`). |
| `ralph.log` | The loop's append-only log: 4 iterations, one commit per iteration, then `DONE.txt` detected. |
| `fix_plan.md` | The running log Claude maintained across iterations, ending with all 8 spec items checked off. |
| `DONE.txt` | The sentinel Claude wrote once all 8 items passed. Its presence is what ends the loop. |
| `produced-changes.md` | The code the run produced: the `csv_safe()` helper, the `CSVExport` class, the route wiring, and the new tests. |

## How to read it (top to bottom)

1. **`PROMPT.md`** - the 8 spec items are the contract. Everything else is the loop satisfying them.
2. **`fix_plan.md`** - one logical change per iteration, each with its validation result. The final checklist shows every spec item passing.
3. **`ralph.log`** - the mechanical loop: feed spec to a fresh `claude -p`, let it work, commit, check for `DONE.txt`, repeat.
4. **`produced-changes.md`** - the actual output. Every spec item maps to something here.

## The shape of the loop (what to narrate)

Ralph never holds the whole task in one context. Each iteration is a fresh headless Claude that reads the same spec, looks at what's already done (the code + `fix_plan.md`), makes ONE change, validates it, and commits. The loop, not the model, decides when it's finished: only when all 8 items pass does Claude write `DONE.txt`, and the driver stops. That is the across-session harness in its simplest form.
