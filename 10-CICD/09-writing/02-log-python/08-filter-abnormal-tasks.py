#!/usr/bin/env python3
"""
高频场景：分析运行日志，按 session/task 聚合，筛出异常任务

判定规则（可调）：
  - 任意 status=error / level=ERROR
  - latency_ms >= 阈值（默认 5000）
  - 同 tool 失败次数 >= retry_limit（默认 2）
  - msg/error 命中关键字（timeout|refused|502|quota）

用法:
  python 08-filter-abnormal-tasks.py
  python 08-filter-abnormal-tasks.py --latency-ms 3000 --retry-limit 2 --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_TRACE = HERE.parent / "02-log-process" / "agent_trace.jsonl"
DEFAULT_APP_DIR = HERE.parent / "02-log-process"

ERROR_KW = re.compile(r"timeout|refused|502|quota|fail|exceed", re.I)
APP_LINE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>[A-Z]+)\s+\[(?P<module>[^\]]+)\]\s*(?P<rest>.*)$"
)
KV = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')


@dataclass
class TaskSummary:
    session_id: str
    events: int = 0
    errors: int = 0
    max_latency_ms: int = 0
    tools_failed: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    samples: list[str] = field(default_factory=list)

    @property
    def abnormal(self) -> bool:
        return bool(self.reasons)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[skip] {path.name}:{lineno} {e}", file=sys.stderr)
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def load_app_as_events(app_dir: Path) -> list[dict[str, Any]]:
    """把 app-*.log 转成与 trace 类似的事件，便于统一聚合。"""
    events: list[dict[str, Any]] = []
    for path in sorted(app_dir.glob("app-*.log")):
        for line in path.open(encoding="utf-8"):
            m = APP_LINE.match(line.strip())
            if not m:
                continue
            d = m.groupdict()
            fields = {k: (q or b) for k, q, b in KV.findall(d["rest"])}
            sid = fields.get("session")
            if not sid:
                continue
            status = fields.get("status", "")
            level = d["level"]
            msg = fields.get("msg", "")
            cost = int(fields["cost_ms"]) if fields.get("cost_ms", "").isdigit() else 0
            is_err = level == "ERROR" or status in {"timeout", "error", "fail"}
            events.append(
                {
                    "session_id": sid,
                    "tool": fields.get("tool") or d["module"],
                    "status": "error" if is_err else "success",
                    "latency_ms": cost,
                    "error": msg or status or None,
                    "level": level,
                    "source": path.name,
                }
            )
    return events


def summarize(
    events: list[dict[str, Any]],
    *,
    latency_ms: int,
    retry_limit: int,
) -> list[TaskSummary]:
    by_session: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        sid = e.get("session_id") or e.get("session") or "<unknown>"
        by_session[str(sid)].append(e)

    results: list[TaskSummary] = []
    for sid, items in sorted(by_session.items()):
        s = TaskSummary(session_id=sid, events=len(items))

        for e in items:
            lat = int(e.get("latency_ms") or 0)
            s.max_latency_ms = max(s.max_latency_ms, lat)
            status = str(e.get("status") or "").lower()
            level = str(e.get("level") or "").upper()
            err = str(e.get("error") or e.get("msg") or "")
            tool = str(e.get("tool") or "?")

            if status == "error" or level == "ERROR":
                s.errors += 1
                if tool not in s.tools_failed:
                    s.tools_failed.append(tool)
                if len(s.samples) < 3:
                    s.samples.append(err or f"{tool}:{status or level}")

            if lat >= latency_ms:
                reason = f"slow:{tool}:{lat}ms"
                if reason not in s.reasons:
                    s.reasons.append(reason)
            kw = ERROR_KW.search(err)
            if kw:
                reason = f"keyword:{kw.group(0).lower()}"
                if reason not in s.reasons:
                    s.reasons.append(reason)

        if s.errors:
            s.reasons.append(f"errors:{s.errors}")
        # 整 session 内同 tool 失败次数 >= retry_limit
        tool_fail_counts: Counter = Counter()
        for e in items:
            if str(e.get("status")).lower() == "error" or str(e.get("level")).upper() == "ERROR":
                tool_fail_counts[str(e.get("tool") or "?")] += 1
        for tool, fails in tool_fail_counts.items():
            if fails >= retry_limit:
                reason = f"retry:{tool}x{fails}"
                if reason not in s.reasons:
                    s.reasons.append(reason)

        results.append(s)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter abnormal sessions/tasks")
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--app-dir", type=Path, default=DEFAULT_APP_DIR)
    parser.add_argument("--latency-ms", type=int, default=5000)
    parser.add_argument("--retry-limit", type=int, default=2)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--source",
        choices=("trace", "app", "both"),
        default="both",
        help="数据源：JSONL trace / 文本 app / 两者",
    )
    args = parser.parse_args()

    events: list[dict[str, Any]] = []
    if args.source in {"trace", "both"} and args.trace.exists():
        events.extend(load_jsonl(args.trace))
    if args.source in {"app", "both"} and args.app_dir.is_dir():
        events.extend(load_app_as_events(args.app_dir))

    if not events:
        print("无可用事件", file=sys.stderr)
        sys.exit(2)

    summaries = summarize(
        events, latency_ms=args.latency_ms, retry_limit=args.retry_limit
    )
    abnormal = [s for s in summaries if s.abnormal]

    if args.json:
        payload = {
            "total_sessions": len(summaries),
            "abnormal_sessions": len(abnormal),
            "threshold_latency_ms": args.latency_ms,
            "retry_limit": args.retry_limit,
            "tasks": [asdict(s) for s in abnormal],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"sessions={len(summaries)} abnormal={len(abnormal)}")
        print(f"rules: latency>={args.latency_ms}ms OR errors OR retry>={args.retry_limit}")
        print()
        for s in abnormal:
            print(f"[{s.session_id}] events={s.events} errors={s.errors} "
                  f"max_lat={s.max_latency_ms}ms")
            print(f"  reasons : {', '.join(s.reasons)}")
            print(f"  tools   : {', '.join(s.tools_failed) or '-'}")
            for sample in s.samples:
                print(f"  sample  : {sample}")
            print()

    # 有异常任务时 exit 1，方便 CI / 笔试演示红灯
    sys.exit(1 if abnormal else 0)


if __name__ == "__main__":
    main()
