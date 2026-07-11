# Auth — Schedulr

## Two Auth Systems (Brownfield)

Schedulr has two authentication patterns that coexist. All **new routes** must use JWT.

### 1. JWT (forward / preferred)

**File:** `app/backend/app/services/auth_jwt.py`

- Token issued at `/api/auth/login` (POST, form-encoded `username`/`password`).
- Bearer token via `Authorization: Bearer <token>` header.
- Dependency: `Depends(get_current_user)` — resolves to the `User` ORM object.
- Token payload: `{"sub": "<user_id_str>", "exp": <unix_timestamp>}`.
- Algorithm: `HS256`; secret from `settings.jwt_secret` (env `JWT_SECRET`; falls back to `"dev-secret-change-me"`).
- Expiry: `settings.jwt_expire_minutes` (default 1440 min = 24 h).

```python
# Canonical usage in a route (app/backend/app/api/routes_meetings.py:28)
from app.services.auth_jwt import get_current_user

@router.get("")
def get_meetings(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ...
```

### 2. Legacy session token (do not add new routes here)

**File:** `app/backend/app/services/auth_legacy.py`

- Opaque token in `X-Session-Token` header.
- In-process `dict[str, int]` store — not persistent across restarts.
- Dependency: `Depends(get_user_from_session)`.
- Still used by some older routes; the JWT migration was never completed.

## Authorization

- Team-scoped: every authenticated user has `current.team_id`; queries always filter by it.
- Role check for mutations: `current.role != "admin"` guard before host-only operations (e.g., `routes_meetings.py:116`).
- No middleware-level RBAC; checks are inline in route handlers.

## Password Hashing

**File:** `app/backend/app/services/security.py` — uses `bcrypt` (via `passlib`).

## Frontend Auth Flow

- Login → stores JWT in `localStorage` (see `app/frontend/lib/`).
- API client attaches `Authorization: Bearer` to every request.
