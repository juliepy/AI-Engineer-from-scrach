"""Write startup diagnostics to logs/startup.log (visible even when Streamlit hides stderr)."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "startup.log"


def startup_log(msg: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {msg}"
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
    except OSError:
        pass
    print(line, file=sys.stderr, flush=True)
