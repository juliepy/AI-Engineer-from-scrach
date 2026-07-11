from typing import Callable, Dict, List

from agent.expand import expand_candidates
from agent.executor import apply_action, is_terminal
from agent.scorer import score_action
from agent.types import Scorer, Tool, TreeNode


def select(node: TreeNode, exploration: float = 1.4) -> TreeNode:
    """Select：从根沿 UCB 走到可扩展叶节点。"""
    while not node.is_leaf():
        unvisited = [c for c in node.children if c.visits == 0]
        if unvisited:
            return unvisited[0]
        node = node.best_child_ucb(exploration)
    return node


def expand_node(
    node: TreeNode,
    llm: Callable[[str], str],
    k: int,
    tool_names: List[str],
) -> TreeNode:
    """Expand：为叶节点生成 k 个子分支。"""
    if node.children:
        return node
    for action in expand_candidates(node.state, llm, k=k, tool_names=tool_names):
        child_state = node.state + "\n" + action
        child = TreeNode(state=child_state, action=action, parent=node)
        node.children.append(child)
    return node.children[0] if node.children else node


def simulate(
    node: TreeNode,
    scorer: Scorer,
    tools: Dict[str, Tool],
    task: str,
    llm: Callable[[str], str] | None = None,
    rollout_depth: int = 1,
) -> float:
    """
    Simulate/Rollout：评估从该节点继续的潜力。
    默认对当前边动作打分；可选再展开 1 步取 max 作为粗 rollout。
    """
    if node.action:
        base = score_action(node.parent.state if node.parent else node.state, node.action, scorer)
    else:
        base = 0.5

    if rollout_depth <= 0 or llm is None:
        return base

    state = node.state
    if tools and node.action:
        state = apply_action(node.parent.state, node.action, tools) if node.parent else node.state

    if is_terminal(state, task):
        return 1.0

    candidates = expand_candidates(state, llm, k=2, tool_names=list(tools.keys()))
    if not candidates:
        return base
    scores = [score_action(state, a, scorer) for a in candidates]
    return max(base, max(scores) * 0.9)


def backpropagate(node: TreeNode, value: float) -> None:
    """Backpropagate：将回报沿路径回传。"""
    cur: TreeNode | None = node
    while cur is not None:
        cur.visits += 1
        cur.total_value += value
        cur = cur.parent


def best_child_by_visits(root: TreeNode) -> TreeNode:
    if not root.children:
        return root
    return max(root.children, key=lambda c: c.visits)


def lats_one_step(
    state: str,
    llm: Callable[[str], str],
    scorer: Scorer,
    k: int = 3,
    tool_names: List[str] | None = None,
) -> str:
    """4.5 极度简化版：扩展 k 个候选，选分最高的一条动作。"""
    print(f"--- lats_one_step ---")
    print(f"State: {state}")
    names = tool_names or ["calculator", "word_count", "get_current_time"]
    cands = expand_candidates(state, llm, k=k, tool_names=names)
    best_action = max(cands, key=lambda a: score_action(state, a, scorer))
    print(f"Cands: {cands}")    
    [print(f"Action: {a}") for a in cands]
    print(f"Best action: {best_action}")
    print("=" * 60)
    return best_action
