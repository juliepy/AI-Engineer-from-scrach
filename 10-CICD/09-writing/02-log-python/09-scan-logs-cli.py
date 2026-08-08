#!/usr/bin/env python3
"""
多文件日志巡检 + 阈值 + CI 退出码（Python 版 check_errors.sh / log_report.sh）

覆盖：
  - 扫目录下 app-*.log / *.jsonl
  - 统计 ERROR / WARN / 关键字
  - TopN 模块 / msg
  - 超阈值 exit 1，否则 exit 0
  - 错误打 stderr

用法:
  python 09-scan-logs-cli.py ../02-log-process
  python 09-scan-logs-cli.py ../02-log-process --threshold 5
  python 09-scan-logs-cli.py ../02-log-process --threshold 100   # 期望绿
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

APP_ERROR = re.compile(r"\bERROR\b")
APP_WARN = re.compile(r"\bWARN\b")
APP_MODULE = re.compile(r"\[([^\]]+)\]")
APP_MSG = re.compile(r'msg="([^"]*)"')


def iter_log_files(directory: Path) -> list[Path]:
    files = sorted(directory.glob("app-*.log"))
    files += sorted(directory.glob("*.jsonl"))
    # 去重保序
    seen: set[Path] = set()
    out: list[Path] = []
    for p in files:
        if p not in seen and p.is_file():
            seen.add(p)
            out.append(p)
    return out


def scan_text_file(path: Path) -> tuple[int, int, Counter, Counter]:
    errors = warns = 0
    modules: Counter = Counter()
    msgs: Counter = Counter()
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if APP_ERROR.search(line):
                errors += 1
                m = APP_MODULE.search(line)
                if m:
                    modules[m.group(1)] += 1
                msg = APP_MSG.search(line)
                if msg:
                    msgs[msg.group(1)] += 1
            elif APP_WARN.search(line):
                warns += 1
    return errors, warns, modules, msgs


def scan_jsonl(path: Path) -> tuple[int, int, Counter, Counter]:
    errors = warns = 0
    modules: Counter = Counter()
    msgs: Counter = Counter()
    with path.open(encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"[skip] {path.name}:{lineno} invalid json", file=sys.stderr)
                continue
            if not isinstance(obj, dict):
                continue
            level = str(obj.get("level") or "").upper()
            status = str(obj.get("status") or "").lower()
            module = str(obj.get("module") or obj.get("tool") or "unknown")
            msg = str(obj.get("msg") or obj.get("error") or "")
            if level == "ERROR" or status == "error":
                errors += 1
                modules[module] += 1
                if msg:
                    msgs[msg] += 1
            elif level == "WARN" or level == "WARNING":
                warns += 1
    return errors, warns, modules, msgs


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan log dir; fail if ERROR > threshold")
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parent.parent / "02-log-process",
        help="日志目录（默认 ../02-log-process）",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=5,
        help="ERROR 总数阈值，超过则 exit 1（默认 5）",
    )
    parser.add_argument("--top", type=int, default=3, help="TopN 模块/消息")
    args = parser.parse_args()

    directory: Path = args.directory
    if not directory.is_dir():
        print(f"目录不存在: {directory}", file=sys.stderr)
        sys.exit(2)

    files = iter_log_files(directory)
    if not files:
        print(f"未找到 app-*.log / *.jsonl: {directory}", file=sys.stderr)
        sys.exit(2)

    total_err = total_warn = 0
    all_modules: Counter = Counter()
    all_msgs: Counter = Counter()

    print(f"scan: {directory}")
    print(f"threshold: {args.threshold}")
    print()

    for path in files:
        if path.suffix == ".jsonl":
            e, w, mods, msgs = scan_jsonl(path)
        else:
            e, w, mods, msgs = scan_text_file(path)
        total_err += e
        total_warn += w
        all_modules.update(mods)
        all_msgs.update(msgs)
        print(f"{path.name:28} ERROR={e:3} WARN={w:3}")

    print()
    print(f"TOTAL ERROR={total_err} WARN={total_warn}")
    print(f"Top{args.top} modules:", all_modules.most_common(args.top))
    print(f"Top{args.top} msgs   :", all_msgs.most_common(args.top))

    if total_err > args.threshold:
        print(
            f"FAIL: ERROR {total_err} > threshold {args.threshold}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: ERROR {total_err} <= threshold {args.threshold}")
    sys.exit(0)


if __name__ == "__main__":
    main()
