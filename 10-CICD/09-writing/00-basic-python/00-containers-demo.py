#!/usr/bin/env python3
"""
list / dict / set + 过滤 / 去重 / 计数 手练脚本（对应 00-python-core.md §1～§3）

运行:
  python 00-containers-demo.py
"""

from __future__ import annotations

from collections import Counter, defaultdict

# 模拟几条日志记录（真实场景里来自 json.loads）
RECORDS = [
    {"agent_id": "a01", "level": "ERROR", "module": "memory", "msg": "oom"},
    {"agent_id": "a01", "level": "INFO", "module": "memory", "msg": "ok"},
    {"agent_id": "a02", "level": "ERROR", "module": "tool", "msg": "timeout"},
    {"agent_id": "a02", "level": "WARN", "module": "tool", "msg": "retry"},
    {"agent_id": "a01", "level": "ERROR", "module": "memory", "msg": "oom"},
    {"agent_id": "a03", "level": "ERROR", "module": "browser", "msg": "nav fail"},
]


def demo_list_filter() -> None:
    print("=" * 50)
    print("1. list 过滤：只要 ERROR")
    print("=" * 50)

    errors: list[dict] = []
    for r in RECORDS:
        if r["level"] != "ERROR":
            continue
        errors.append(r)

    # 等价：errors = [r for r in RECORDS if r["level"] == "ERROR"]
    print(f"ERROR count: {len(errors)}")
    for r in errors:
        print(f"  {r['agent_id']} {r['module']} {r['msg']}")


def demo_set_dedupe() -> None:
    print()
    print("=" * 50)
    print("2. set 去重：出过错的 agent")
    print("=" * 50)

    bad_agents: set[str] = set()
    for r in RECORDS:
        if r["level"] == "ERROR":
            bad_agents.add(r["agent_id"])

    print(f"unique agents with ERROR: {sorted(bad_agents)}")
    print(f"'a01' in set? {'a01' in bad_agents}")


def demo_dict_count() -> None:
    print()
    print("=" * 50)
    print("3. 手写 dict 计数：每个 agent 的 ERROR 数")
    print("=" * 50)

    counter: dict[str, int] = {}
    for r in RECORDS:
        if r["level"] != "ERROR":
            continue
        aid = r["agent_id"]
        if aid not in counter:
            counter[aid] = 0
        counter[aid] += 1

    for aid, n in sorted(counter.items()):
        print(f"  {aid}: {n}")


def demo_defaultdict_counter() -> None:
    print()
    print("=" * 50)
    print("4. defaultdict / Counter")
    print("=" * 50)

    by_module: defaultdict[str, int] = defaultdict(int)
    for r in RECORDS:
        by_module[r["module"]] += 1
    print("defaultdict module:", dict(by_module))

    levels = Counter(r["level"] for r in RECORDS)
    print("Counter levels:", dict(levels))
    print("Top:", levels.most_common())


def demo_combine() -> None:
    print()
    print("=" * 50)
    print("5. 组合：按 agent 收集 ERROR msg（defaultdict(list)）")
    print("=" * 50)

    msgs: defaultdict[str, list[str]] = defaultdict(list)
    for r in RECORDS:
        if r["level"] == "ERROR":
            msgs[r["agent_id"]].append(r["msg"])

    for aid, items in sorted(msgs.items()):
        # set 去掉同一 agent 的重复 msg
        unique = list(dict.fromkeys(items))
        print(f"  {aid}: {unique}")


if __name__ == "__main__":
    demo_list_filter()
    demo_set_dedupe()
    demo_dict_count()
    demo_defaultdict_counter()
    demo_combine()
    print()
    print("done. 下一步: python 04-count-stats.py")
