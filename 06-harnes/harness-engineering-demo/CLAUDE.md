# Schedulr — Harness Engineering Demo

Schedulr is a B2B meeting-scheduling SaaS for sales teams. Stack: **Next.js 15 App Router + TypeScript** (frontend, `app/frontend/`) and **FastAPI + SQLAlchemy 2.0 + Alembic + Python 3.12** (backend, `app/backend/`). Postgres on host port **5433** (container 5432) via `app/docker-compose.yml`.

---

## Naming Conventions

| Layer | Convention | Example |
|-------|-----------|---------|
| Python files | `snake_case` | `routes_meetings.py`, `export_service.py` |
| Python classes | `PascalCase` | `MeetingCreate`, `PDFExport` |
| Python functions/vars | `snake_case` | `list_meetings`, `viewer_tz` |
| SQLAlchemy columns | `snake_case` (exception: legacy `createdAt` on `users`) | `start_time`, `team_id` |
| TS files/components | `kebab-case` files, `PascalCase` components | `meeting-list.tsx`, `MeetingList` |
| API routes | `/api/<resource>` plural noun | `/api/meetings`, `/api/contacts` |

---

## Core Code Patterns

**Pydantic schemas** (in `app/backend/app/schemas/`): one file per resource; `*Create`, `*Update`, `*Out` naming. All schema classes inherit `BaseModel`.

**SQLAlchemy 2.0 mapped columns** (`app/backend/app/models/`): use `Mapped[T]` + `mapped_column()` throughout — no legacy `Column()` calls.

**Structured errors**: raise `HTTPException(status_code=..., detail="...")` in route handlers; services raise `ValueError` for business-rule violations that routes catch.

**DB sessions**: injected via `Depends(get_db)` (`app/backend/app/database.py`); always call `db.commit()` then `db.refresh(obj)` after mutations.

**Datetime storage**: always UTC, `DateTime(timezone=True)`. Render to viewer timezone only at serialization time via `TimezoneAwareTime` (`app/backend/app/utils/timezones.py`). Never call `.strftime()` on a raw UTC datetime.

**CSV/export escaping**: any user-supplied string written to a CSV cell MUST be prefixed with `'` if it starts with `=`, `+`, `-`, or `@` to prevent formula injection. See `app/backend/app/services/export_service.py` and `.claude/context/export-pattern.md`.

---

## Build & Validation Commands

| Step | Command | Working Directory |
|------|---------|------------------|
| Backend lint | `uv run ruff check app` | `app/backend` |
| Backend type check | `uv run mypy app` | `app/backend` |
| Backend tests | `uv run pytest` | `app/backend` |
| Frontend lint | _none configured — `next lint` prompts interactively (no ESLint in this brownfield app); use type check below_ | `app/frontend` |
| Frontend type check | `npx tsc --noEmit` | `app/frontend` |
| Frontend unit tests | `npm run test` | `app/frontend` |
| Frontend build | `npm run build` | `app/frontend` |

Run the full gate with `/validate` before any PR.

---

## On-Demand Context

Load these modules only when the task touches the relevant area:

| Module | Load when... |
|--------|-------------|
| `.claude/context/architecture.md` | Adding a new resource, service, or route |
| `.claude/context/auth.md` | Any authentication or authorization work |
| `.claude/context/codebase-search.md` | Using the MCP tools to navigate by symbol |
| `.claude/context/export-pattern.md` | Any export feature (CSV, PDF, XLSX, etc.) |
| `.claude/context/testing.md` | Writing or modifying tests |
| `.claude/context/timezones.md` | Any datetime display, serialization, or storage |

---

## Hard Rules

- Run the full validation gate (`/validate`) before opening a PR.
- Never commit secrets, `.env` files, or JWT secrets to version control. A PreToolUse hook (`.claude/hooks/security_guard.py`) hard-blocks reading/editing any `.env` (use `.env.example`) and recursive directory deletes; do not try to work around it.
- Alembic migrations must be reversible — every `upgrade()` must have a working `downgrade()`.
- Escape user-supplied fields before writing them to any CSV cell (formula-injection risk — see export-pattern context).
- New code follows the **forward** auth pattern (`auth_jwt.py`), not the legacy session token. Do not add new routes that depend on `auth_legacy.py`.

---

## Symbol Navigation

Navigate by symbol using the `codebase-search` MCP server (`.mcp.json`) instead of grep. The three tools — `find_references`, `where_is`, `outline` — parse the Python AST and return only real definitions and call sites, with no false hits from comments or strings. Use them whenever you need to:

- Verify a dependency is actually wired into a new route (`find_references("get_current_user")`)
- Locate a function before reading its file (`where_is("list_meetings")`)
- Check a service's public API before adding a method (`outline("export_service")`)

See `.claude/context/codebase-search.md` for full tool descriptions.

---

## Miscellaneous / Gotchas

- Postgres runs on host port **5433** (not 5432). Connection string: `postgresql+psycopg://schedulr:schedulr@localhost:5433/schedulr`. The config falls back to this when `DATABASE_URL` is unset (`app/backend/app/config.py:14`).
- Two auth systems coexist: JWT (`app/backend/app/services/auth_jwt.py`) is the forward one; legacy session token (`app/backend/app/services/auth_legacy.py`) is still used by some routes. Prefer JWT on all new routes.
- `User.createdAt` uses camelCase as the column name — brownfield smell, do not replicate (`app/backend/app/models/user.py:24`).
- `uv.lock` is committed; always use `uv run <cmd>` to execute Python tools so the locked environment is used.
- Frontend `node_modules` are NOT committed; run `npm install` in `app/frontend/` before any frontend work.
