from dataclasses import dataclass
from typing import List


@dataclass
class ReconcileRow:
    request_id: str
    estimated: int
    billed: int
    diff: int
    diff_pct: float
    alert: bool


def reconcile(
    request_id: str,
    estimated: int,
    usage: "UsageFromAPI",
    alert_threshold_pct: float = 10.0,
) -> ReconcileRow:
    billed = usage.total
    diff = billed - estimated
    base = max(estimated, 1)
    diff_pct = round(abs(diff) / base * 100, 2)
    alert = diff_pct > alert_threshold_pct
    return ReconcileRow(request_id, estimated, billed, diff, diff_pct, alert)


def summarize(rows: List[ReconcileRow]) -> dict:
    alerts = [r for r in rows if r.alert]
    return {
        "requests": len(rows),
        "alerts": len(alerts),
        "max_diff_pct": max((r.diff_pct for r in rows), default=0),
    }
