#!/usr/bin/env python3
"""
JSON 日志处理完整示例（SDET / Agent 日志场景）

覆盖：
  1. JSONL 逐行读取 + 异常跳过
  2. 字段校验 / 默认值
  3. 过滤（level / module / 关键字）
  4. 投影（只保留需要的字段）
  5. 统计（Counter）
  6. 分组聚合
  7. 嵌套 JSON（tokens / error）
  8. 写出 JSON / JSONL 报告
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
AGENT_LOG = HERE / "agent.log"
TRACE_LOG = HERE.parent / "02-log-process" / "agent_trace.jsonl"
OUT_DIR = HERE / "out"


# ---------------------------------------------------------------------------
# 1. 读取：JSONL 安全加载
# ---------------------------------------------------------------------------
def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """逐行 json.loads；坏行跳过，不炸掉整个脚本。"""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[skip] {path.name}:{lineno} invalid json: {e}")
                continue
            if not isinstance(obj, dict):
                print(f"[skip] {path.name}:{lineno} not an object")
                continue
            records.append(obj)
    return records


# ---------------------------------------------------------------------------
# 2. 校验：必填字段 + 补默认值
# ---------------------------------------------------------------------------
REQUIRED = ("time", "agent_id", "level", "module", "msg")


def validate(record: dict[str, Any]) -> bool:
    missing = [k for k in REQUIRED if k not in record]
    if missing:
        print(f"[invalid] missing {missing}: {record}")
        return False
    return True


def with_defaults(record: dict[str, Any]) -> dict[str, Any]:
    """缺可选字段时补默认，避免后面 KeyError。"""
    out = dict(record)
    out.setdefault("tags", [])
    out.setdefault("trace_id", None)
    return out


# ---------------------------------------------------------------------------
# 3. 过滤 / 投影
# ---------------------------------------------------------------------------
def filter_records(
    records: list[dict[str, Any]],
    *,
    levels: set[str] | None = None,
    modules: set[str] | None = None,
    msg_contains: str | None = None,
) -> list[dict[str, Any]]:
    result = []
    for r in records:
        if levels and r.get("level") not in levels:
            continue
        if modules and r.get("module") not in modules:
            continue
        if msg_contains and msg_contains.lower() not in str(r.get("msg", "")).lower():
            continue
        result.append(r)
    return result


def project(records: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    """只保留需要的字段，减小输出体积。"""
    return [{k: r.get(k) for k in keys} for r in records]


# ---------------------------------------------------------------------------
# 4. 统计 / 分组
# ---------------------------------------------------------------------------
def count_by(records: list[dict[str, Any]], key: str) -> Counter:
    return Counter(r.get(key, "<missing>") for r in records)


def group_by(records: list[dict[str, Any]], key: str) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        groups[str(r.get(key, "<missing>"))].append(r)
    return dict(groups)


# ---------------------------------------------------------------------------
# 5. 写出：JSON 数组 / JSONL
# ---------------------------------------------------------------------------
def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[write] {path} ({path.stat().st_size} bytes)")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[write] {path} ({len(records)} lines)")


# ---------------------------------------------------------------------------
# 6. 嵌套 JSON：agent_trace 风格
# ---------------------------------------------------------------------------
def demo_nested_trace(path: Path) -> None:
    """处理嵌套字段：tokens.prompt / error / tags。"""
    print()
    print("=" * 60)
    print("6. 嵌套 JSON（agent_trace.jsonl）")
    print("=" * 60)

    if not path.exists():
        print(f"[warn] not found: {path}")
        # 内联样例，保证本文件单独也能演示
        samples = [
            {
                "session_id": "s-1",
                "tool": "browser_navigate",
                "status": "error",
                "latency_ms": 5120,
                "tokens": {"prompt": 1800, "completion": 0},
                "tags": ["browser"],
                "error": "net::ERR_CONNECTION_REFUSED",
            },
            {
                "session_id": "s-1",
                "tool": "read_file",
                "status": "success",
                "latency_ms": 22,
                "tokens": {"prompt": 900, "completion": 140},
                "tags": ["fs"],
                "error": None,
            },
        ]
    else:
        samples = load_jsonl(path)

    errors = [r for r in samples if r.get("status") == "error"]
    print(f"total={len(samples)} error={len(errors)}")

    # 安全取嵌套：dict.get 链式，避免 KeyError
    total_prompt = 0
    for r in samples:
        tokens = r.get("tokens") or {}
        total_prompt += int(tokens.get("prompt") or 0)
    print(f"sum(tokens.prompt) = {total_prompt}")

    # 错误明细
    for r in errors[:5]:
        print(
            f"  {r.get('session_id')} | {r.get('tool')} | "
            f"latency={r.get('latency_ms')} | error={r.get('error')}"
        )

    # tags 展开统计
    tag_counter: Counter = Counter()
    for r in samples:
        for tag in r.get("tags") or []:
            tag_counter[tag] += 1
    print("tags:", dict(tag_counter))


# ---------------------------------------------------------------------------
# 7. 对比两段 JSON（断言 Agent 输出时常用）
# ---------------------------------------------------------------------------
def json_equal(a: Any, b: Any, ignore_keys: set[str] | None = None) -> bool:
    """递归比较；可忽略时间戳等不稳定字段。"""
    ignore_keys = ignore_keys or set()

    if isinstance(a, dict) and isinstance(b, dict):
        keys_a = {k for k in a if k not in ignore_keys}
        keys_b = {k for k in b if k not in ignore_keys}
        if keys_a != keys_b:
            return False
        return all(json_equal(a[k], b[k], ignore_keys) for k in keys_a)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(json_equal(x, y, ignore_keys) for x, y in zip(a, b))
    return a == b


# ---------------------------------------------------------------------------
# main：串成一条日志处理流水线
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("1. 加载 agent.log")
    print("=" * 60)
    raw = load_jsonl(AGENT_LOG)
    print(f"raw lines -> {len(raw)} objects")

    print()
    print("=" * 60)
    print("2. 校验 + 默认值")
    print("=" * 60)
    records = [with_defaults(r) for r in raw if validate(r)]
    print(f"valid -> {len(records)}")

    print()
    print("=" * 60)
    print("3. 过滤 ERROR / memory")
    print("=" * 60)
    errors = filter_records(records, levels={"ERROR"})
    memory_errs = filter_records(errors, modules={"memory"})
    print(f"ERROR={len(errors)}, memory ERROR={len(memory_errs)}")
    for r in memory_errs:
        print(f"  {r['time']} {r['agent_id']} {r['msg']}")

    print()
    print("=" * 60)
    print("4. 投影字段")
    print("=" * 60)
    slim = project(errors, ("time", "agent_id", "module", "msg"))
    print(json.dumps(slim, indent=2, ensure_ascii=False))

    print()
    print("=" * 60)
    print("5. 统计 / 分组")
    print("=" * 60)
    print("by level :", dict(count_by(records, "level")))
    print("by module:", dict(count_by(records, "module")))
    print("by agent :", dict(count_by(errors, "agent_id")))

    grouped = group_by(errors, "agent_id")
    for aid, items in grouped.items():
        print(f"  {aid}: {len(items)} errors -> {[i['msg'] for i in items]}")

    print()
    print("=" * 60)
    print("7. JSON 对比（忽略 time）")
    print("=" * 60)
    a = {"agent_id": "agent_01", "level": "ERROR", "time": "t1", "msg": "x"}
    b = {"agent_id": "agent_01", "level": "ERROR", "time": "t2", "msg": "x"}
    print("equal ignore time:", json_equal(a, b, ignore_keys={"time"}))
    print("equal strict     :", json_equal(a, b))

    # 嵌套 trace
    demo_nested_trace(TRACE_LOG)

    print()
    print("=" * 60)
    print("8. 写出报告")
    print("=" * 60)
    report = {
        "source": str(AGENT_LOG.name),
        "total": len(records),
        "error_count": len(errors),
        "by_level": dict(count_by(records, "level")),
        "by_agent_error": dict(count_by(errors, "agent_id")),
        "errors": slim,
    }
    write_json(OUT_DIR / "error_report.json", report)
    write_jsonl(OUT_DIR / "errors.jsonl", slim)

    print()
    print("done. 打开 out/error_report.json 看结果。")


if __name__ == "__main__":
    main()
