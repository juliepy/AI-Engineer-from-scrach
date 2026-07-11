# SOP: Chrome DevTools Validation Loop

Use this SOP when UI work depends on actual runtime interaction and screenshots,
DOM state, and console output matter more than code inspection alone.

## Goal

Turn UI validation into a repeatable interaction loop the agent can run until
the journey is clean.

## Core Loop

1. Select the target page or app instance.
2. Clear stale console noise.
3. Capture the BEFORE state.
4. Trigger the UI path.
5. Observe runtime events during interaction.
6. Capture the AFTER state.
7. Apply the fix and restart the app if needed.
8. Re-run validation until the journey is clean.

## Required Inputs

- a stable startup command
- a reproducible UI journey
- a way to snapshot DOM, console, or screenshots
- a rule for what counts as "clean"

## Execution SOP

1. Write the target journey in the active plan.
2. Define success in observable terms: text present, button enabled, error gone,
   console clean, request succeeded.
3. Snapshot the initial state before interaction.
4. Trigger exactly one path at a time.
5. Record runtime events, DOM changes, and visible output.
6. If the journey fails, fix the smallest responsible layer and restart.
7. Re-run the same path and compare BEFORE/AFTER evidence.

## Clean Criteria

- intended visible state is present
- unexpected errors are absent
- console noise is understood or cleared
- rerunning the same path gives the same result

## Repo Artifacts To Update

- active execution plan
- `docs/RELIABILITY.md` if the journey becomes a golden path
- product spec if the visible behavior changed
