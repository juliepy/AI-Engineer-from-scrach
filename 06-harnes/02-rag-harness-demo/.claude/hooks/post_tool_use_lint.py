#!/usr/bin/env python3
"""PostToolUse 静态检查 hook。

从 stdin 读取 Claude Code hook JSON。文件编辑/写入后：
  - `app/` 或 `tests/` 下的 Python 文件 → ruff check（代码检查）
  - 其他文件 → 跳过

始终退出 0（建议性——发现问题但不阻塞工作）。

连接到：PostToolUse / Edit|Write|MultiEdit
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def _emit(result: subprocess.CompletedProcess, ok: str, bad: str) -> None:
    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr)
    print(f"[lint-hook] {ok}" if result.returncode == 0 else f"[lint-hook] {bad}")


def main() -> None:
    try:
        data: dict = json.load(sys.stdin)
    except Exception as exc:
        print(f"[lint-hook] 无法解析 hook JSON: {exc}", file=sys.stderr)
        sys.exit(0)

    tool_input: dict = data.get("tool_input") or {}
    file_path_raw = tool_input.get("file_path")
    if not file_path_raw:
        sys.exit(0)

    file_path = Path(file_path_raw).resolve()
    project_dir = Path(".").resolve()

    try:
        rel_str = file_path.relative_to(project_dir).as_posix()
    except ValueError:
        sys.exit(0)

    # 只检查 app/ 和 tests/ 下的 Python 文件
    if file_path.suffix != ".py":
        sys.exit(0)
    if not (rel_str.startswith("app/") or rel_str.startswith("tests/")):
        sys.exit(0)

    ruff = shutil.which("ruff")
    if not ruff:
        print("[lint-hook] ruff 未安装，跳过检查（运行 pip install ruff）")
        sys.exit(0)

    print(f"[lint-hook] ruff check → {rel_str}")
    result = subprocess.run(
        [ruff, "check", str(file_path)],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
    )
    _emit(result, ok="ruff: OK", bad="ruff: 发现问题（见上方）——提交前请修复")

    sys.exit(0)  # 建议性 hook，永不阻塞


if __name__ == "__main__":
    main()
