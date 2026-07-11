# =============================================================================
#  7.4 LangGraph 风格极简对照：图 = 节点 + 边 + 状态
# =============================================================================
#
#  伪代码级教学，不绑定具体 LangGraph 版本号。
#  设计思想：用有向图编排 Agent 步骤，状态在节点间流转，边决定下一步。
#
#  真实 LangGraph 大致等价于：
#    graph.add_node("plan", plan_fn)
#    graph.add_node("code", code_fn)
#    graph.add_edge("plan", "code")
#    graph.set_entry_point("plan")
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#    state = {"task": "...", "plan": "", "code": ""}
#       │
#       ▼
#    [plan] ──edge──► [code] ──edge──► [test]
#       │                │                │
#       ▼                ▼                ▼
#    更新 state       更新 state       更新 state
#
# =============================================================================

import sys
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")

NodeFn = Callable[[Dict[str, Any]], Dict[str, Any]]


class SimpleGraph:
    """LangGraph 思路的极简模拟：节点 + 边 + 共享 state。"""

    def __init__(self) -> None:
        self._nodes: Dict[str, NodeFn] = {}
        self._edges: Dict[str, List[str]] = defaultdict(list)
        self._entry: Optional[str] = None

    def add_node(self, name: str, fn: NodeFn) -> None:
        self._nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        self._edges[src].append(dst)

    def set_entry_point(self, name: str) -> None:
        self._entry = name

    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if not self._entry:
            raise ValueError("未设置 entry point")
        current = self._entry
        while current:
            if current not in self._nodes:
                raise KeyError(f"节点不存在: {current}")
            state = self._nodes[current](state)
            next_nodes = self._edges.get(current, [])
            current = next_nodes[0] if next_nodes else None
        return state


def plan_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    state["plan"] = "1. 定义 POST /login\n2. 返回 JWT"
    return state


def code_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    state["code"] = "def login(u, p): return {'token': issue_jwt(u)}"
    return state


def test_fn(state: Dict[str, Any]) -> Dict[str, Any]:
    state["test"] = "assert login('a', 'b')['token']"
    return state


def build_demo_graph() -> SimpleGraph:
    graph = SimpleGraph()
    graph.add_node("plan", plan_fn)
    graph.add_node("code", code_fn)
    graph.add_node("test", test_fn)
    graph.add_edge("plan", "code")
    graph.add_edge("code", "test")
    graph.set_entry_point("plan")
    return graph


if __name__ == "__main__":
    graph = build_demo_graph()
    final = graph.invoke({"task": "实现登录 API"})

    print("=== LangGraph 风格：节点 + 边 + 状态 ===")
    for key, value in final.items():
        print(f"  {key}: {value}")
