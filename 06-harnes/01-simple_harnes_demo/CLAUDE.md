# Agent Rules for Simple Harness Demo

## Mission

Deliver small, safe, test-backed changes in this repository.

The demo app is a password strength checker in `app/password.py`.

## Coding rules

- Keep code simple and readable.
- Add tests for behavior changes.
- Do not break existing tests.
- Avoid broad refactors for small requests.

## Workflow rules

- Use `/plan` before `/implement`.
- During `/implement`, validate after each completed task.
- Before finishing, run full validation (`python scripts/validate.py`).

## Safety rules

- Do not read or write real `.env` files.
- Do not delete directories recursively.

## Definition of done

A task is done only when:

1. feature works
2. tests pass
3. validation passes
