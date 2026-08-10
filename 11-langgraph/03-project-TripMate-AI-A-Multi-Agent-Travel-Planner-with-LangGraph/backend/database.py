import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

import backend.config  # noqa: F401 — load .env + SSL certs

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRAVEL_DB_PATH = DATA_DIR / "travel.db"


def create_checkpointer() -> SqliteSaver:
    conn = sqlite3.connect(database=str(TRAVEL_DB_PATH), check_same_thread=False)
    return SqliteSaver(conn)
