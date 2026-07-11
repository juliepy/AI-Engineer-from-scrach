# SOP: Observability Feedback Loop

Use this SOP when debugging is slow, agents keep claiming success without
evidence, or runtime behavior is harder to inspect than the code itself.

## Goal

Give the agent a local feedback loop over logs, metrics, traces, and runnable
workloads so it can reason from execution, not only from code inspection.

## Minimum Stack

- application emits structured logs
- application emits metrics and traces when feasible
- local fan-out or collection layer
- query interfaces for logs, metrics, and traces
- repeatable workload or user journey to rerun after each change

## Execution SOP

1. Define the golden runtime journeys that matter most.
2. Add structured logs to startup and the critical path.
3. Add metrics for latency, failure counts, or queue depth where useful.
4. Add traces or timing markers for slow or multi-step flows.
5. Make the signals queryable from the local dev environment.
6. Give the agent one repeatable workload or scenario to rerun.
7. Require the loop: query -> correlate -> reason -> implement -> restart ->
   rerun -> verify.

## Debug Session Checklist

- What failed?
- Which signal proves the failure?
- Which layer owns the failure?
- What changed after the fix?
- Did the app restart cleanly?
- Did the same workload pass after rerun?

## Definition Of Done

- The agent can explain a failure mode from runtime evidence.
- The same workload can be rerun after each change.
- Restart and rerun are part of the normal task loop.
- Reliability signals are documented in `docs/RELIABILITY.md`.
