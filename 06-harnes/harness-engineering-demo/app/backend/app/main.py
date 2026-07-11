from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import routes_auth, routes_meetings, routes_contacts, routes_teams, routes_availability

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # Allow the configured origin AND 3001 (dev server fallback port)
    allow_origins=[settings.cors_origin, "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_meetings.router)
app.include_router(routes_contacts.router)
app.include_router(routes_teams.router)
app.include_router(routes_availability.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
