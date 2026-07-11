#!/usr/bin/env python3
"""Stop hook — 验证门。

从 stdin 读取 Claude Code 的 Stop hook JSON。
如果 stop_hook_active 为 True（说明此 hook 已触发过一次阻止，
Claude 正在被询问是否继续），立即退出 0 避免无限循环。

否则运行 pytest 质量门。失败时输出 JSON block decision，
让 Claude 知道原因并修复；通过时静默退出 0。

连接到：Stop
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str) -> tuple[bool, str]:
    """运行命令，返回 (是否通过, 摘要文本)。"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    passed = result.returncode == 0
    out = (result.stdout + result.stderr).strip()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    summary = "\n".join(lines[:20]) if lines else "(no output)"
    return passed, summary


def main() -> None:
    # 读取 hook JSON（解析失败则放行，不阻塞会话）
    try:
        data: dict = json.load(sys.stdin)
    except Exception as exc:
        print(f"[stop-hook] 无法解析 hook JSON: {exc}", file=sys.stderr)
        sys.exit(0)

    # 防止无限循环：hook 已激活过一次则直接放行
    if data.get("stop_hook_active"):
        sys.exit(0)

    project_dir = Path(".").resolve()
    failures: list[str] = []

    # --- pytest（via validate.py）---
    passed, summary = run(
        [sys.executable, "scripts/validate.py"],
        cwd=str(project_dir),
    )
    if not passed:
        failures.append(f"pytest 失败:\n{summary}")

    if failures:
        reason = "验证门未通过: " + " | ".join(
            f.replace("\n", " ") for f in failures
        )
        reason += "。请修复问题后继续。"
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)

    # 全部绿色——允许停止
    sys.exit(0)


if __name__ == "__main__":
    main()
