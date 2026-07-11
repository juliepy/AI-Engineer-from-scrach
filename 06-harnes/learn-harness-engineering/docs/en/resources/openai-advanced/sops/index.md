# OpenAI Advanced SOPs

These SOPs translate the article's operating patterns into concrete execution
playbooks you can follow or adapt.

## Included SOPs

- [`layered-domain-architecture.md`](./layered-domain-architecture.md):
  establish explicit layers and cross-cutting boundaries
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md):
  move invisible knowledge from chat, docs, and memory into repo-local files
- [`observability-feedback-loop.md`](./observability-feedback-loop.md):
  give agents logs, metrics, traces, and a repeatable debug loop
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md):
  use browser automation and snapshots to validate UI behavior until clean

## How To Use Them

1. Pick the SOP that matches your current bottleneck.
2. Use the checklist to set up the missing artifacts or tooling.
3. Encode the resulting rules into your copied `repo-template/` docs.
4. Convert repeated review comments into checks, scripts, or guardrails.

These are not meant to be followed blindly. They are meant to make the harness
more legible, enforceable, and repeatable.
