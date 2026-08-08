#!/usr/bin/env python3
"""数据统计 / 字典计数：从 agent.log 统计，对应 shell awk。"""

import json
from collections import Counter, defaultdict
from pathlib import Path

LOG_PATH = Path(__file__).with_name("agent.log")

# ---------------------------------------------------------------------------
# 加载日志
# ---------------------------------------------------------------------------
records = []
with LOG_PATH.open("r", encoding="utf-8") as f:
    for lineno, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"[skip] line {lineno}: invalid json")

print(f"loaded {len(records)} records\n")

# ---------------------------------------------------------------------------
# 1. 手写字典计数（笔试万能模板）
# ---------------------------------------------------------------------------
print("=" * 50)
print("1. 手写 dict：每个 agent 的 ERROR 数")
print("=" * 50)

error_counter = {}
for r in records:
    if r.get("level") != "ERROR":
        continue
    aid = r["agent_id"]
    if aid not in error_counter:
        error_counter[aid] = 0
    error_counter[aid] += 1

for aid, n in error_counter.items():
    print(f"{aid}: {n}")

# ---------------------------------------------------------------------------
# 2. defaultdict：少写 if key not in
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("2. defaultdict：按 module 计数")
print("=" * 50)

module_counter = defaultdict(int)
for r in records:
    module_counter[r["module"]] += 1

for module, n in sorted(module_counter.items(), key=lambda x: -x[1]):
    print(f"{module}: {n}")

# ---------------------------------------------------------------------------
# 3. Counter：一行统计 + 排行
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("3. Counter：按 level 计数")
print("=" * 50)

level_counter = Counter(r["level"] for r in records)
print(dict(level_counter))
print("最多:", level_counter.most_common(1))
print("排行:", level_counter.most_common())

# ---------------------------------------------------------------------------
# 4. 组合统计：agent × level
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("4. 组合：每个 agent 各 level 数量")
print("=" * 50)

# key = (agent_id, level)
pair_counter = Counter((r["agent_id"], r["level"]) for r in records)
for (aid, level), n in sorted(pair_counter.items()):
    print(f"{aid:10} {level:5} {n}")

# ---------------------------------------------------------------------------
# 5. 汇总输出（面试常写这种小报告）
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("5. 汇总")
print("=" * 50)

print(f"总行数     : {len(records)}")
print(f"ERROR 总数 : {level_counter['ERROR']}")
print(f"出错 agent : {sorted(error_counter)}")
print(f"错误最多   : {max(error_counter, key=error_counter.get)} "
      f"({max(error_counter.values())})")
