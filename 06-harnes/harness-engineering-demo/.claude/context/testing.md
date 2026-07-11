# Testing — Schedulr

## Backend (pytest)

**Framework:** pytest 8.x  
**Config:** `app/backend/pyproject.toml` — `testpaths = ["app/tests"]`, `pythonpath = ["."]`  
**Run:** `cd app/backend && uv run pytest`

### Test Files

| File | What it tests |
|------|--------------|
| `app/tests/test_auth.py` | Login, token validation, 401 cases |
| `app/tests/test_meetings.py` | CRUD, team isolation, status transitions |
| `app/tests/test_contacts.py` | Contact CRUD, team scoping |
| `app/tests/test_teams.py` | Team management |
| `app/tests/test_availability.py` | Availability rules |
| `app/tests/test_export.py` | Export service unit tests (no DB needed) |
| `app/tests/test_timezone.py` | `TimezoneAwareTime` rendering |

### Fixtures (`app/tests/conftest.py`)

- `db` — in-memory SQLite session (overrides `get_db` dependency).
- `client` — `TestClient` with dependency overrides applied.
- `auth_headers` — convenience fixture that logs in and returns `Authorization` headers.

### Patterns

```python
# Route test pattern (from test_meetings.py)
def test_create_meeting(client, auth_headers):
    resp = client.post("/api/meetings", json={...}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "..."

# Unit test (no HTTP, no DB) — from test_export.py
def test_render_returns_bytes():
    exporter = PDFExport()
    result = exporter.render([])
    assert isinstance(result, bytes)
```

### What Tests Do NOT Cover

- End-to-end browser flows (no Playwright backend tests yet; frontend has `e2e/` with Playwright).
- No coverage minimum is enforced in CI — coverage is aspirational.

## Frontend (Vitest + Playwright)

**Unit tests:** Vitest (`npm run test` in `app/frontend/`); config in `vitest.config.ts`.  
**E2E:** Playwright (`app/frontend/e2e/`); config in `playwright.config.ts`.  
**Component tests:** in `app/frontend/__tests__/`.

## Adding Tests for a New Feature

1. Backend: add `app/backend/app/tests/test_<resource>.py` — mirror `test_export.py` for pure-unit, `test_meetings.py` for HTTP+DB.
2. For timezone-sensitive code: always test with at least one non-UTC timezone (see `test_export.py:TestFormatWhen.test_berlin_format`).
3. For exports: include a formula-injection test (see `.claude/context/export-pattern.md`).
