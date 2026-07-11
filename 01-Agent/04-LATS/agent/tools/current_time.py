from datetime import datetime
from zoneinfo import ZoneInfo


def run(tz_name: str) -> str:
    tz = (tz_name or "Asia/Shanghai").strip() or "Asia/Shanghai"
    try:
        now = datetime.now(ZoneInfo(tz))
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as exc:
        return f"ERROR: invalid timezone '{tz}': {exc}"
