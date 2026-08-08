#!/usr/bin/env python3
"""
解析非 JSON 文本日志（对应 shell grep/sed/awk）

覆盖：
  1. app 日志：时间 / level / [module] / key=value 字段
  2. access 日志：IP / 状态码 / URL / 耗时
  3. 时间窗过滤
  4. 轻量清洗：IP 脱敏、空白压缩、去重

用法:
  python 07-parse-text-log.py
  python 07-parse-text-log.py --start "2026-08-01 09:00:00" --end "2026-08-01 12:00:00"
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_APP = HERE.parent / "02-log-process" / "app-2026-08-01.log"
DEFAULT_ACCESS = HERE.parent / "02-log-process" / "access.log"

# 2026-08-01 09:00:01 INFO  [agent-core] session=s-1001 msg="..."
APP_LINE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"\[(?P<module>[^\]]+)\]\s*"
    r"(?P<rest>.*)$"
)
KV = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')

# 10.0.0.1 - - [02/Aug/2026:09:58:12 +0800] "GET /api/chat HTTP/1.1" 200 1532 0.312 ...
ACCESS_LINE = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+'
    r'"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<proto>[^"]+)"\s+'
    r"(?P<status>\d+)\s+(?P<bytes>\d+)\s+(?P<latency>\d+\.\d+)"
)

WS_COLLAPSE = re.compile(r"[ \t]+")


def parse_app_line(line: str) -> dict | None:
    m = APP_LINE.match(line.strip())
    if not m:
        return None
    rec = m.groupdict()
    for key, quoted, bare in KV.findall(rec.pop("rest")):
        rec[key] = quoted if quoted else bare
    return rec


def parse_access_line(line: str) -> dict | None:
    m = ACCESS_LINE.match(line.strip())
    if not m:
        return None
    rec = m.groupdict()
    rec["status"] = int(rec["status"])
    rec["bytes"] = int(rec["bytes"])
    rec["latency"] = float(rec["latency"])
    return rec


def mask_ip(ip: str) -> str:
    """末段脱敏：10.0.0.9 -> 10.0.0.x"""
    parts = ip.split(".")
    if len(parts) == 4 and all(p.isdigit() for p in parts):
        return ".".join(parts[:3] + ["x"])
    return ip


def collapse_ws(text: str) -> str:
    return WS_COLLAPSE.sub(" ", text).strip()


def in_window(ts: str, start: str | None, end: str | None) -> bool:
    # 定长 "YYYY-MM-DD HH:MM:SS" 可直接字符串比较（与 time_filter.sh 同思路）
    if start and ts < start:
        return False
    if end and ts > end:
        return False
    return True


def demo_app(path: Path, start: str | None, end: str | None) -> None:
    print("=" * 60)
    print(f"1. 解析 app 日志: {path.name}")
    print("=" * 60)
    if not path.exists():
        print(f"[warn] not found: {path}")
        return

    records: list[dict] = []
    skipped = 0
    for lineno, line in enumerate(path.open(encoding="utf-8"), start=1):
        line = line.strip()
        if not line:
            continue
        rec = parse_app_line(line)
        if not rec:
            skipped += 1
            print(f"[skip] line {lineno}")
            continue
        if not in_window(rec["ts"], start, end):
            continue
        records.append(rec)

    print(f"parsed={len(records)} skipped={skipped}")

    levels = Counter(r["level"] for r in records)
    modules = Counter(r["module"] for r in records)
    print("by level :", dict(levels))
    print("by module:", dict(modules))

    print("\n-- ERROR / timeout 行（字段已结构化）--")
    for r in records:
        if r["level"] != "ERROR" and r.get("status") != "timeout":
            continue
        host = r.get("host")
        if host:
            r = {**r, "host": mask_ip(host)}
        print(
            f"{r['ts']} {r['level']:5} [{r['module']}] "
            f"session={r.get('session', '-')} "
            f"msg={r.get('msg', r.get('status', ''))}"
            + (f" host={r['host']}" if host else "")
        )

    # 去重演示：同一 session+msg 只保留首次
    print("\n-- 去重：session+msg 首次出现 --")
    seen: set[tuple[str, str]] = set()
    for r in records:
        key = (r.get("session", ""), r.get("msg", ""))
        if not key[1] or key in seen:
            continue
        seen.add(key)
        if r["level"] in {"ERROR", "WARN"}:
            print(f"  {key[0]} | {collapse_ws(key[1])}")


def demo_access(path: Path) -> None:
    print()
    print("=" * 60)
    print(f"2. 解析 access 日志: {path.name}")
    print("=" * 60)
    if not path.exists():
        print(f"[warn] not found: {path}")
        return

    records: list[dict] = []
    for line in path.open(encoding="utf-8"):
        rec = parse_access_line(line)
        if rec:
            records.append(rec)

    print(f"parsed={len(records)}")
    status_hist = Counter(r["status"] for r in records)
    print("status:", dict(sorted(status_hist.items())))

    bad = [r for r in records if r["status"] >= 400]
    print(f"\n-- 4xx/5xx Top（脱敏 IP）共 {len(bad)} --")
    for r in bad[:8]:
        print(
            f"{r['status']} {r['method']:4} {r['path']:<18} "
            f"{r['latency']:6.3f}s  ip={mask_ip(r['ip'])}"
        )

    chat = [r for r in records if r["path"] == "/api/chat"]
    if chat:
        avg = sum(r["latency"] for r in chat) / len(chat)
        print(f"\n/api/chat count={len(chat)} avg_latency={avg:.3f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse plain-text app/access logs")
    parser.add_argument("--app", type=Path, default=DEFAULT_APP)
    parser.add_argument("--access", type=Path, default=DEFAULT_ACCESS)
    parser.add_argument("--start", type=str, default=None, help="时间窗起（含）")
    parser.add_argument("--end", type=str, default=None, help="时间窗止（含）")
    args = parser.parse_args()

    demo_app(args.app, args.start, args.end)
    demo_access(args.access)
    print("\ndone.")


if __name__ == "__main__":
    main()
