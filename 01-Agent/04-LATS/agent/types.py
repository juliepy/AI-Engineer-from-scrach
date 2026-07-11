from dataclasses import dataclass, field
from typing import Callable, List, Optional


Scorer = Callable[[str, str], float]


@dataclass
class Tool:
    name: str
    description: str
    run: Callable[[str], str]


@dataclass
class TreeNode:
    """搜索树节点：状态 + 父边动作 + MCTS 统计量。"""

    state: str
    action: Optional[str] = None
    parent: Optional["TreeNode"] = field(default=None, repr=False)
    children: List["TreeNode"] = field(default_factory=list)
    visits: int = 0
    total_value: float = 0.0

    def ucb(self, exploration: float = 1.4) -> float:
        if self.visits == 0:
            return float("inf")
        exploit = self.total_value / self.visits
        parent_visits = self.parent.visits if self.parent else 1
        import math

        explore = exploration * math.sqrt(math.log(parent_visits + 1) / self.visits)
        return exploit + explore

    def best_child_ucb(self, exploration: float = 1.4) -> "TreeNode":
        return max(self.children, key=lambda c: c.ucb(exploration))

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def path_actions(self) -> List[str]:
        actions: List[str] = []
        node: Optional[TreeNode] = self
        while node and node.action:
            actions.append(node.action)
            node = node.parent
        actions.reverse()
        return actions
