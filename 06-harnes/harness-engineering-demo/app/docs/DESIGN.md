# Schedulr — Demo Codebase Design Spec

> **⚠️ THIS IS A DELIBERATELY BROWNFIELD DEMO CODEBASE.**
> It is the demo workhorse for the free 2-hour "AI-Native Engineering Org" workshop.
> The intentional smells are **load-bearing**. The workshop transforms this code *live*.
> See "Intentional Smells" below — do NOT clean these up.

## What Schedulr is

A B2B meeting-scheduling SaaS — "Calendly for sales teams, with CRM integration."
A Series-A-stage product (~35 fictional engineers, ~6 months post-MVP) with the
quality state you'd expect: shipping slows, incidents creep up, review burnout.

- **Backend:** Python + FastAPI + Postgres (SQLAlchemy 2.0 + Alembic)
- **Frontend:** Next.js (TypeScript, App Router) + Tailwind CSS + shadcn-style components
- **Tooling story (added later, in stages):** Jira + Confluence + GitHub + Actions CI

## Core domains

| Domain | Entities | Notes |
|---|---|---|
| Accounts | `User`, `Team` | Users belong to teams; a team is the billing/tenant boundary |
| Scheduling | `Meeting`, `MeetingInvitee`, `AvailabilitySlot` | Meetings have a host, invitees, start/end, timezone |
| CRM | `Contact`, `ContactMeetingLink` | Sales contacts linked to meetings |
| Export | `ExportService` (+ `PDFExport`) | The pattern CSV export mirrors in the demo |

## Pages

| Route | Description |
|---|---|
| `/` | Login page (JWT + legacy session both issued) |
| `/dashboard` | Operational KPIs: upcoming meetings, this week, contacts, team size; recent activity |
| `/meetings` | Meeting list with filters (date range, host, status, search), pagination, PDF export |
| `/meetings/[id]` | Meeting detail: invitees + RSVP, notes editor, mark complete, cancel |
| `/schedule` | Create/book a meeting — wires the POST /meetings endpoint; contact picker |
| `/availability` | Weekly availability editor — wires the AvailabilitySlot model |
| `/contacts` | CRM contact list with stage filter; inline create modal |
| `/contacts/[id]` | Contact detail with edit form, pipeline stage, linked meetings |
| `/team` | Team members, roles, timezones, invite, role management |
| `/settings` | Profile, timezone, password change, notifications (stub), CRM integrations (stub) |

## API endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | /api/auth/login | — | JWT login |
| POST | /api/auth/legacy-login | — | Legacy session token (smell) |
| GET | /api/auth/me | JWT | Current user |
| PATCH | /api/auth/me/profile | JWT | Update name/timezone |
| POST | /api/auth/me/change-password | JWT | Change password |
| GET | /api/meetings | JWT | List with filters: host_id, status, search, contact_id, pagination |
| POST | /api/meetings | JWT | Create meeting |
| GET | /api/meetings/export | JWT | PDF export only (CSV is SCH-142, not built) |
| GET | /api/meetings/{id} | JWT | Meeting detail + invitees |
| PATCH | /api/meetings/{id} | JWT | Update (host or admin only) |
| DELETE | /api/meetings/{id} | JWT | Cancel (sets status=cancelled) |
| PATCH | /api/meetings/{id}/invitees/{inv_id}/rsvp | JWT | Update RSVP response |
| GET | /api/contacts | Legacy | List contacts (smell: uses legacy auth) |
| POST | /api/contacts | Legacy | Create contact |
| GET | /api/contacts/{id} | Legacy | Contact detail |
| PATCH | /api/contacts/{id} | Legacy | Update contact |
| DELETE | /api/contacts/{id} | Legacy | Delete contact |
| GET | /api/availability | JWT | Current user's availability |
| GET | /api/availability/user/{user_id} | JWT | Any team member's availability |
| POST | /api/availability | JWT | Add slot |
| PUT | /api/availability | JWT | Bulk replace all slots |
| DELETE | /api/availability/{slot_id} | JWT | Delete slot |
| GET | /api/teams/me | JWT | Team + members |
| POST | /api/teams/me/members | JWT admin | Invite member |
| PATCH | /api/teams/me/members/{id}/role | JWT admin | Change role |
| DELETE | /api/teams/me/members/{id} | JWT admin | Remove member |

## The meetings-list page

The frontend's `/meetings` page lists a team's meetings with filters (date range,
host, status, search, contact). **This is where SCH-142 "Add CSV export to meetings page"
lands.** There is a PDF export button — but NO CSV. The workshop adds it.

## Timezone convention

There is a helper, `app/utils/timezones.py::TimezoneAwareTime`, that is the *intended*
way to render meeting times in a user's timezone. The rule (encoded in `CLAUDE.md` at
stage-1): **never format meeting datetimes with raw `datetime`/naive strftime — always
go through `TimezoneAwareTime`.**

**Timezone handling is now CORRECT in this codebase.** Both `meeting_service.py` and
`export_service.py` use `TimezoneAwareTime`. The multi-timezone demo users (dana=Chicago,
lukas=Berlin, mei=Singapore) showcase correct per-viewer rendering.

## The Q3 Workshop Build Targets (NOT built — the live-build surface)

These are intentionally left out so the workshop builds them live:

1. **SCH-142 CSV export** — `GET /api/meetings/export?format=csv` does not exist.
   The `ExportService` protocol + `PDFExport` class in `export_service.py` are the
   seam. A naive CSV implementation copied from that pattern should escape
   formula-injection (e.g. cells starting with `=`, `+`, `-`, `@`).
   **The formula-injection escaping is the regression guard** the `/system-gap` skill
   catches and prevents in Act 3.
2. **Reporting & Analytics dashboard** — see `docs/specs/q3-reporting-analytics.md`.
3. **Weekly email digest** — scheduled job, not built.
4. **Q3 date-range report filter** — on the future analytics page.

## Intentional Smells (must survive to stage-0)

1. **No root `CLAUDE.md`** or rules file (added at stage-1).
2. **Mixed naming** — `User.createdAt` (camelCase) vs `Team.created_at` (snake_case)
   and similar inconsistencies throughout Python + TypeScript.
3. **Two competing auth patterns** — legacy opaque session token
   (`services/auth_legacy.py`) AND newer JWT (`services/auth_jwt.py`), both live.
   Contacts routes use legacy; meetings/teams routes use JWT. Inconsistency intentional.
4. **No clean test strategy** — comprehensive test suite now exists, but fixture
   style is deliberate brownfield: the `conftest.py` + transaction rollback pattern
   is the "right way" that the workshop can reveal vs. the old ad-hoc style.
5. **Hardcoded env values** in ~4 places in `config.py`: DB URL fallback,
   JWT secret default, CORS origin hardcode, session TTL.
6. **Stale `# TODO: refactor` comments** in `auth_legacy.py` ("filed ~2 years ago").
7. **`utils/misc.py`** hand-rolls `chunk`, `uniq`, `pluck`, `slugify` — all things
   utility libraries already do. Exists to be a "why two ways?" moment.

## Test suite

- **Backend:** `uv run pytest` — 80 tests, all green. Covers auth (JWT + legacy),
  meetings (list/detail/create/update/cancel/RSVP), availability CRUD, contacts,
  teams, export, timezone rendering. Uses real Postgres (schedulr_test) with
  transaction-rollback fixtures.
- **Frontend:** `npm test` — 31 Vitest component/unit tests, all green.
  Playwright e2e specs in `e2e/` cover login, meetings, schedule, availability
  golden paths (validated separately with live stack).

## Git-tagged transformation stages

| Tag | State |
|---|---|
| `stage-0` | This brownfield app. Full UI, all CRUD, 80 backend tests + 31 frontend tests. |
| `stage-1` | + `CLAUDE.md`, `.claude/context/`, `/context-from-jira` skill |
| `stage-2` | + `/plan` `/implement` `/validate` skills, CI, PR template, review agent |
| `stage-3` | + `/system-gap` skill, `/spec` skill, Confluence writeback |

## How to run (local end-to-end)

```bash
# 1. Postgres
docker compose up -d db
# 2. Backend
cd backend && uv sync --extra dev && uv run alembic upgrade head && uv run python -m app.seed
uv run uvicorn app.main:app --reload --port 8000
# 3. Frontend
cd frontend && npm install && npm run dev   # http://localhost:3000
# 4. Run tests
cd backend && uv run pytest                 # 80 backend tests
cd frontend && npm test                     # 31 Vitest unit tests
```

## Demo users

| User | Email | Timezone | Role |
|---|---|---|---|
| Dana Ortiz | dana@acme.test | America/Chicago | admin |
| Lukas Berg | lukas@acme.test | Europe/Berlin | member |
| Mei Tan | mei@acme.test | Asia/Singapore | member |

All use password `password123`. Meeting times are rendered in each viewer's timezone
(correct behavior — demonstrates the `TimezoneAwareTime` helper working as intended).
