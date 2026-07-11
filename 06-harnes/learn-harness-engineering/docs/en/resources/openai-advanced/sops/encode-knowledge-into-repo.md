# SOP: Encode Unseen Knowledge Into The Repo

Use this SOP when important context still lives in Google Docs, chat threads,
tickets, or people's heads.

## Goal

Make agent-invisible knowledge discoverable in the codebase so a fresh session
can act on it without relying on prior conversation.

## Trigger Signals

- The agent keeps asking how the system works.
- Humans say "we decided this in Slack" or "follow what X said last week."
- Reviews reference product or security rules that are not written in-repo.
- New sessions repeat discovery work that should already be settled.

## Execution SOP

1. List the invisible knowledge sources: docs, chats, tacit team rules, verbal decisions.
2. For each source, ask: is this architecture, product behavior, security policy,
   reliability expectation, plan context, or reference material?
3. Encode it into the matching repo artifact:
   - architecture -> `ARCHITECTURE.md`
   - product behavior -> `docs/product-specs/`
   - design rationale -> `docs/design-docs/`
   - execution state -> `docs/exec-plans/`
   - repeated external references -> `docs/references/`
   - quality or reliability expectations -> `docs/QUALITY_SCORE.md` or `docs/RELIABILITY.md`
4. Replace vague statements with operationally useful wording.
5. Remove or deprecate stale copies so the repo keeps one discoverable truth.

## Good Encoding Rules

- Write for discoverability, not for literary completeness.
- Prefer short documents with clear filenames.
- Link related artifacts together.
- Store durable rules, not meeting transcripts.
- Update the repo in the same session that the decision is made.

## Definition Of Done

- A fresh agent can discover the relevant rule without asking a human.
- The same fact is not scattered across multiple contradictory files.
- The new artifact lives close to the code or workflow it governs.
