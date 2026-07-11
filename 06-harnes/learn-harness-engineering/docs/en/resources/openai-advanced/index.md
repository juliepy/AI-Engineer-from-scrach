# OpenAI Advanced Pack

This folder packages the more opinionated repository shape described in
OpenAI's "Harness engineering: leveraging Codex in an agent-first world"
article into copy-ready starter files.

Use this pack when the minimal harness is no longer enough and your repository
now needs:

- a short routing-style `AGENTS.md`
- durable system-of-record docs inside the repo
- active and completed execution plans
- explicit product, reliability, security, and frontend policy files
- quality scoring by product domain and architectural layer
- model-friendly reference material folders
- standard operating procedures for architecture, knowledge capture, and runtime validation

## Included Starter Layout

The starter pack under [`repo-template/`](./repo-template/index.md) mirrors the
structure below:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## How To Adopt It

1. Start from the minimal pack if your repo is still small.
2. Copy the files in [`repo-template/`](./repo-template/index.md) into your
   own repository once you need stronger structure.
3. Keep `AGENTS.md` short. Treat it as a router into the deeper docs, not as an
   encyclopedia.
4. Update the quality, reliability, and plan docs as part of normal work, not
   as a separate cleanup day.
5. Keep generated artifacts and external references explicit so agents can find
   them without relying on chat history.

## SOP Library

The [`sops/`](./sops/index.md) folder turns the article's diagrams into
step-by-step operating procedures:

- layered domain architecture setup
- encode unseen knowledge into the repository
- local observability stack and feedback-loop workflow
- Chrome DevTools validation loop for UI work

## Design Principles

- Short entrypoint, deeper linked docs
- Repository as system of record
- Mechanical checks beat remembered rules
- Plans and quality history live beside the code
- Cleanup and simplification are first-class responsibilities

This pack is intentionally opinionated, but it should still be adapted to your
project rather than copied blindly.
