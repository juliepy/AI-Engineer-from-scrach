# Architecture — Schedulr

## Overview

```
app/
├── backend/               FastAPI + SQLAlchemy 2.0 + Alembic, Python 3.12, uv
│   ├── app/
│   │   ├── main.py        App factory: CORS middleware + router registration
│   │   ├── config.py      Settings (pydantic-settings, reads .env)
│   │   ├── database.py    Engine + SessionLocal + Base + get_db() dependency
│   │   ├── models/        ORM models: user, team, meeting, contact, availability
│   │   ├── schemas/       Pydantic I/O schemas: *Create, *Update, *Out per resource
│   │   ├── api/           Route files: routes_<resource>.py; each has one router
│   │   ├── services/      Business logic: meeting_service, export_service, auth_jwt, auth_legacy, security
│   │   ├── utils/         Helpers: timezones.py, misc.py
│   │   └── tests/         pytest; one test file per route/domain
│   └── alembic/           DB migrations
├── frontend/              Next.js 15 App Router, TypeScript, Tailwind
│   ├── app/               Next.js App Router pages and layouts
│   ├── components/        Shared React components
│   └── lib/               API client, utils
└── docker-compose.yml     Postgres 16 (host 5433 → container 5432)
```

## Adding a New Resource

Pattern: mirror `meetings` end-to-end.

1. **Model** (`app/backend/app/models/<resource>.py`) — `Mapped[T]` + `mapped_column()`; add to `app/backend/app/models/__init__.py`.
2. **Schema** (`app/backend/app/schemas/<resource>.py`) — `*Create`, `*Update`, `*Out` dataclasses.
3. **Service** (`app/backend/app/services/<resource>_service.py`) — query helpers and serializers.
4. **Routes** (`app/backend/app/api/routes_<resource>.py`) — `APIRouter(prefix="/api/<resource>", tags=["<resource>"])`.
5. **Register** in `app/backend/app/main.py` — `app.include_router(routes_<resource>.router)`.
6. **Migration** — `uv run alembic revision --autogenerate -m "add <resource>"` in `app/backend/`.

## Key Files

| File | Line range | Purpose |
|------|-----------|---------|
| `app/backend/app/main.py` | 1–27 | Router registration, CORS |
| `app/backend/app/database.py` | — | `get_db()` dependency |
| `app/backend/app/models/meeting.py` | 9–49 | Meeting + MeetingInvitee ORM example |
| `app/backend/app/api/routes_meetings.py` | 1–178 | Full CRUD route pattern |
| `app/backend/app/services/meeting_service.py` | — | Service layer pattern |
