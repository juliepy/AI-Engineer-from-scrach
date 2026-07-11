# =============================================================================
#  三种协作模式对照：Boss-Worker / Pipeline / Joint Discussion
# =============================================================================
#
#  各有瓶颈：
#  - Boss-Worker：Boss 单点调度，上下文与决策压力集中
#  - Pipeline：固定串行，难回溯、难并行
#  - Joint Discussion：多轮讨论，易空转、Token 膨胀
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#  Boss-Worker:  Boss 拆任务 → Worker₁…ₙ → Boss 汇总
#  Pipeline:     A → B → C（单向流水，无回头边）
#  Discussion:   全员轮询发言 × N 轮 → 主席/投票收敛
#
# =============================================================================

import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, List

sys.stdout.reconfigure(encoding="utf-8")

AgentFn = Callable[[str, str], str]


@dataclass
class Worker:
    name: str
    skill: str


def run_boss_worker(
    goal: str,
    workers: List[Worker],
    boss: AgentFn,
    worker_fn: AgentFn,
) -> Dict[str, str]:
    """Boss 拆任务、派工、汇总（Boss 为单点）。"""
    plan = boss("boss", f"拆解目标: {goal}")
    subtasks = [line.strip("- ").strip() for line in plan.splitlines() if line.strip()]
    results: Dict[str, str] = {"boss_plan": plan}
    for i, task in enumerate(subtasks):
        w = workers[i % len(workers)]
        results[f"{w.name}:{task}"] = worker_fn(w.name, f"[{w.skill}] 执行: {task}")
    results["boss_summary"] = boss("boss", "汇总:\n" + "\n".join(results.values()))
    return results


def run_pipeline(stages: List[str], goal: str, stage_fn: AgentFn) -> List[str]:
    """固定流水线：每阶段只吃上一步摘要（难回溯）。"""
    outputs: List[str] = []
    scratch = goal
    for stage in stages:
        out = stage_fn(stage, f"阶段={stage}\n输入摘要:\n{scratch[:200]}")
        outputs.append(f"[{stage}] {out}")
        scratch = out
    return outputs


def run_joint_discussion(
    members: List[str],
    topic: str,
    speak_fn: AgentFn,
    max_rounds: int = 3,
) -> List[str]:
    """多轮讨论：每人每轮发言一次，展示空转风险（无新信息则重复）。"""
    transcript: List[str] = []
    for rnd in range(1, max_rounds + 1):
        for member in members:
            ctx = "\n".join(transcript[-6:])
            msg = speak_fn(member, f"第{rnd}轮 | 议题: {topic}\n近期发言:\n{ctx}")
            line = f"R{rnd}-{member}: {msg}"
            transcript.append(line)
    return transcript


def mock_boss(name: str, prompt: str) -> str:
    if "拆解" in prompt:
        return "- 写用户故事\n- 设计 API\n- 编写测试"
    return "Boss 汇总：三子任务均已完成，可进入联调。"


def mock_worker(name: str, prompt: str) -> str:
    return f"{name} 完成片段（prompt={len(prompt)} 字符）"


def mock_stage(name: str, prompt: str) -> str:
    canned = {
        "analyst": "需求：登录 + JWT",
        "architect": "POST /login, GET /me",
        "coder": "def login(...): ...",
    }
    return canned.get(name, f"{name} 输出")


def mock_discuss(name: str, prompt: str) -> str:
    if "R3" in prompt and name != "pm":
        return "我同意 PM 的方案。"  # 后期趋同，模拟讨论收敛前空转
    return f"{name} 提议方案 v1"


if __name__ == "__main__":
    workers = [
        Worker("dev1", "backend"),
        Worker("dev2", "frontend"),
        Worker("qa1", "testing"),
    ]

    print("=== Boss-Worker（Boss 单点拆派汇）===")
    bw = run_boss_worker("交付登录功能", workers, mock_boss, mock_worker)
    for k, v in bw.items():
        print(f"  {k}: {v[:60]}{'...' if len(v) > 60 else ''}")
    print()

    print("=== Pipeline（固定串行，难回溯）===")
    for line in run_pipeline(["analyst", "architect", "coder"], "登录 API", mock_stage):
        print(f"  {line}")
    print()

    print("=== Joint Discussion（多轮讨论，注意轮次与重复）===")
    for line in run_joint_discussion(
        ["pm", "dev", "qa"], "接口用 REST 还是 gRPC？", mock_discuss, max_rounds=2
    ):
        print(f"  {line}")
