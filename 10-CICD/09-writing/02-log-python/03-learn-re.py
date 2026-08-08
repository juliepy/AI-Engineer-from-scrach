#!/usr/bin/env python3
"""从 agent.log 加载日志，用正则查找 / 提取字段。"""

import re
from pathlib import Path

LOG_PATH = Path(__file__).with_name("agent.log")

# 读入全部行（去掉空行）
lines = [
    line.strip()
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

print(f"loaded {len(lines)} lines from {LOG_PATH.name}\n")

# ---------------------------------------------------------------------------
# 1. search：找「第一条」ERROR
# ---------------------------------------------------------------------------
print("=" * 50)
print("1. search：第一条 ERROR")
print("=" * 50)

for line in lines:
    m = re.search(r'"level"\s*:\s*"ERROR"', line)
    if m:
        print(line)
        break

# ---------------------------------------------------------------------------
# 2. findall：统计所有 agent_id
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("2. findall：所有 agent_id")
print("=" * 50)

# 有捕获组时，findall 只返回括号里的内容
agent_ids = re.findall(r'"agent_id"\s*:\s*"(agent_\d+)"', "\n".join(lines))
print(agent_ids)

# ---------------------------------------------------------------------------
# 3. 命名组：逐行抽出字段
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("3. 命名组：逐行解析")
print("=" * 50)

# JSON 行上的正则（学习用；生产环境优先 json.loads）
field_pat = re.compile(
    r'"agent_id"\s*:\s*"(?P<agent>agent_\d+)".*?'
    r'"level"\s*:\s*"(?P<level>\w+)".*?'
    r'"module"\s*:\s*"(?P<module>\w+)".*?'
    r'"msg"\s*:\s*"(?P<msg>[^"]+)"'
)

for line in lines:
    m = field_pat.search(line)
    if not m:
        print("[skip]", line[:40], "...")
        continue
    d = m.groupdict()
    print(f'{d["agent"]:10} {d["level"]:5} {d["module"]:8} {d["msg"]}')

# ---------------------------------------------------------------------------
# 4. 过滤：只打印 ERROR，且 msg 含 timeout / fail
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("4. 过滤：ERROR 且 msg 含 timeout|fail")
print("=" * 50)

error_keyword = re.compile(
    r'"level"\s*:\s*"ERROR".*"msg"\s*:\s*"[^"]*(timeout|fail)[^"]*"',
    re.IGNORECASE,
)

for line in lines:
    if error_keyword.search(line):
        # 再抽 msg 方便看
        msg = re.search(r'"msg"\s*:\s*"([^"]+)"', line)
        aid = re.search(r'"agent_id"\s*:\s*"([^"]+)"', line)
        print(f'{aid.group(1)} -> {msg.group(1)}')

# ---------------------------------------------------------------------------
# 5. sub：把 ERROR 标红前缀（演示替换，不改文件）
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("5. sub：给 ERROR 行加标记")
print("=" * 50)

for line in lines:
    marked = re.sub(
        r'("level"\s*:\s*")ERROR(")',
        r'\1***ERROR***\2',
        line,
    )
    if marked != line:
        print(marked)

print("\n改 LOG_PATH 或 pattern 继续练。")
