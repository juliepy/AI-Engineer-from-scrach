#!/usr/bin/env python3
"""读取 agent.log（JSONL），校验字段，筛出 ERROR 并格式化输出。"""

import json
from pathlib import Path
 
LOG_PATH = Path(__file__).with_name("agent.log")
REQUIRED_FIELDS = ("agent_id", "level", "msg")


def has_required_fields(record: dict) -> bool:
    return all(key in record for key in REQUIRED_FIELDS)


errors = []

with LOG_PATH.open("r", encoding="utf-8") as f:
    for lineno, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"[skip] line {lineno}: invalid json")
            continue

        if not has_required_fields(record):
            print(f"[skip] line {lineno}: missing field")
            continue

        if record["level"] == "ERROR":
            errors.append(record)

print(f"ERROR count: {len(errors)}")
print(json.dumps(errors, indent=2, ensure_ascii=False))
