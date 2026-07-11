# =============================================================================
#  6.4 多 Agent 任务阶段状态机（enum + 显式迁移）
# =============================================================================
#
#  用小型状态机约束多 Agent 流水线：INIT → PLAN → EXEC → VERIFY → DONE
#  VERIFY 不通过可打回 EXEC 重做。可对接持久化层（DB / Redis）保存 phase。
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#    INIT ──► PLAN ──► EXEC ──► VERIFY ──► DONE
#                              │    ▲
#                              └────┘  验证失败，打回重做
#
#    TaskState.move(nxt)
#       │
#       ▼
#    nxt in ALLOWED[current]？ ──否──► ValueError（非法迁移）
#       │ 是
#       ▼
#    self.phase = nxt  （可在此 hook 持久化）
#
# =============================================================================

import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Set

sys.stdout.reconfigure(encoding="utf-8")


class Phase(Enum):
    INIT = auto()
    PLAN = auto()
    EXEC = auto()
    VERIFY = auto()
    DONE = auto()


ALLOWED: Dict[Phase, Set[Phase]] = {
    Phase.INIT: {Phase.PLAN},
    Phase.PLAN: {Phase.EXEC},
    Phase.EXEC: {Phase.VERIFY},
    Phase.VERIFY: {Phase.DONE, Phase.EXEC},  # 不通过可打回重做
    Phase.DONE: set(),
}


@dataclass
class TaskState:
    phase: Phase = Phase.INIT

    def move(self, nxt: Phase) -> None:
        if nxt not in ALLOWED[self.phase]:
            raise ValueError(f"illegal {self.phase.name} -> {nxt.name}")
        self.phase = nxt

    def snapshot(self) -> dict:
        """便于对接持久化层：序列化当前阶段。"""
        return {"phase": self.phase.name}


def restore_task(data: dict) -> TaskState:
    """从持久化记录恢复状态。"""
    return TaskState(phase=Phase[data["phase"]])


if __name__ == "__main__":
    task = TaskState()

    print("=== 正常流转 ===")
    for nxt in (Phase.PLAN, Phase.EXEC, Phase.VERIFY, Phase.DONE):
        task.move(nxt)
        print(f"  → {task.phase.name}")
    print("快照:", task.snapshot())
    print()

    print("=== 验证失败，打回 EXEC ===")
    task2 = TaskState(phase=Phase.VERIFY)
    task2.move(Phase.EXEC)
    print(f"  VERIFY → {task2.phase.name}")
    task2.move(Phase.VERIFY)
    task2.move(Phase.DONE)
    print(f"  再次验证通过 → {task2.phase.name}")
    print()

    print("=== 非法迁移（应报错）===")
    done_task = TaskState(phase=Phase.DONE)
    try:
        done_task.move(Phase.EXEC)
    except ValueError as e:
        print(f"  捕获: {e}")
