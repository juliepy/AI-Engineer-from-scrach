#!/usr/bin/env python3
"""
argparse 命令行入参示例（对应 01-python-basic.md §4）

用法:
  python 06-argparse-cli.py --level ERROR
  python 06-argparse-cli.py --module memory --level ERROR
  python 06-argparse-cli.py --contains timeout
  python 06-argparse-cli.py --level ERROR --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LOG_PATH = Path(__file__).with_name("agent.log")


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"[skip] line {lineno}: invalid json", file=sys.stderr)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter agent JSONL logs")
    parser.add_argument("--level", type=str, help="按 level 过滤，如 ERROR")
    parser.add_argument("--module", type=str, help="按 module 过滤，如 memory")
    parser.add_argument("--contains", type=str, help="msg 关键字（忽略大小写）")
    parser.add_argument("--json", action="store_true", help="以 JSON 数组输出")
    parser.add_argument(
        "--file",
        type=Path,
        default=LOG_PATH,
        help="日志文件路径（默认本目录 agent.log）",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)

    records = load_records(args.file)
    result = []
    for r in records:
        if args.level and r.get("level") != args.level:
            continue
        if args.module and r.get("module") != args.module:
            continue
        if args.contains and args.contains.lower() not in str(r.get("msg", "")).lower():
            continue
        result.append(r)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"matched: {len(result)}")
        for r in result:
            print(f"{r.get('time')} {r.get('agent_id')} {r.get('level')} {r.get('msg')}")

    # 无匹配时也 exit 0；需要 CI 红灯时可改成 sys.exit(1 if not result else 0)


if __name__ == "__main__":
    main()
