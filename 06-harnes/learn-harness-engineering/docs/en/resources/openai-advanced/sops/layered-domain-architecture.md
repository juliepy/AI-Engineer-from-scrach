# SOP: Layered Domain Architecture

Use this SOP when the agent keeps violating boundaries, duplicating logic across
layers, or producing code that becomes hard to review after a few sessions.

## Goal

Make domain boundaries explicit enough that agents can move quickly without
silently degrading structure.

## Target Model

Within a business domain, prefer this directional flow:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Cross-cutting concerns should enter through explicit providers or adapters.
Shared utils stay outside the domain and should not accumulate domain logic.

## Setup Checklist

- Define the current domains in `ARCHITECTURE.md`.
- Write allowed dependency directions in `ARCHITECTURE.md`.
- Record cross-cutting interfaces such as auth, telemetry, and external APIs.
- Add one short note for the hardest current boundary violation.
- Decide what should be enforced mechanically by lint, tests, or scripts.

## Execution SOP

1. Map the codebase into domains before touching implementation style.
2. For each domain, identify the allowed layer sequence.
3. Identify all cross-cutting concerns and route them through providers or adapters.
4. Move ambiguous shared logic either into the owning domain or into truly generic utils.
5. Document the rules in `ARCHITECTURE.md`.
6. Add one executable guardrail for the highest-cost violation.
7. Update quality scoring after the change.

## Definition Of Done

- A fresh agent can tell which layer owns a change.
- UI code no longer reaches into repo or external side effects directly.
- Cross-cutting concerns have named entry points.
- At least one important boundary is enforced mechanically.

## Repo Artifacts To Update

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- `docs/design-docs/` when the rationale changed
- `docs/PLANS.md` or the active execution plan
