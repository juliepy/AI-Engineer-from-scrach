# =============================================================================
#  7.5 pytest 集成测试（Mock LLM）
# =============================================================================
#
#  FakeLLM：按预设 replies 顺序返回，替代真实 API
#  run_agent_stub：两轮编排 —— tool JSON → 执行工具 → 最终答案
#
#  运行：cd 05-model-route/04 && pytest -v
#
# =============================================================================

import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=__import__("pathlib").Path(__file__).resolve().parent,
    )
    raise SystemExit(result.returncode)
