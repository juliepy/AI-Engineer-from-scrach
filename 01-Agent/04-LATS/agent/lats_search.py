from typing import Callable, Dict, List

from agent.executor import apply_action, is_terminal
from agent.mcts import (
    backpropagate,
    best_child_by_visits,
    expand_node,
    lats_one_step,
    select,
    simulate,
)
from agent.types import Scorer, Tool, TreeNode


def lats_mcts(
    task: str,
    llm: Callable[[str], str],
    scorer: Scorer,
    tools: Dict[str, Tool],
    budget: int = 6,
    branch_k: int = 3,
    max_depth: int = 4,
    exploration: float = 1.4,
    verbose: bool = False,
) -> tuple[str, List[str]]:
    """
    LATS + MCTS：在语言决策树上做 Select → Expand → Simulate → Backpropagate。

    返回 (最终状态文本, 选中的动作序列)。
    """
    root = TreeNode(state=f"Task: {task}")
    tool_names = list(tools.keys())

    for i in range(1, budget + 1):
        leaf = select(root, exploration=exploration)
        depth = len(leaf.path_actions())

        if depth >= max_depth or is_terminal(leaf.state, task):
            reward = 1.0 if is_terminal(leaf.state, task) else 0.4
            backpropagate(leaf, reward)
            if verbose:
                print(f"  [iter {i}] depth={depth} terminal-ish reward={reward:.2f}")
            continue

        if leaf.is_leaf():
            expand_node(leaf, llm, k=branch_k, tool_names=tool_names)
            if not leaf.children:
                backpropagate(leaf, 0.1)
                continue
            child = leaf.children[0]
        else:
            unvisited = [c for c in leaf.children if c.visits == 0]
            child = unvisited[0] if unvisited else leaf.best_child_ucb(exploration)

        reward = simulate(child, scorer, tools, task, llm=llm, rollout_depth=0)
        backpropagate(child, reward)
        if verbose:
            act = child.action or "(root)"
            print(f"  [iter {i}] action={act[:60]}... reward={reward:.2f}")

    path_node = best_child_by_visits(root)
    while path_node.children:
        path_node = best_child_by_visits(path_node)

    actions = path_node.path_actions()
    state = f"Task: {task}"
    for action in actions:
        state = apply_action(state, action, tools)

    return state, actions


def lats_solve(
    task: str,
    llm: Callable[[str], str],
    scorer: Scorer,
    tools: Dict[str, Tool],
    mode: str = "mcts",
    budget: int = 6,
    max_depth: int = 4,
    branch_k: int = 3,
    verbose: bool = False,
) -> str:
    """
    统一入口：mode='one_step' 只扩展一层；mode='mcts' 完整树搜索。
    """
    state = f"Task: {task}"

    if mode == "one_step":
        if verbose:
            print("--- lats_one_step ---")
        best_action = lats_one_step(state, llm, scorer, k=branch_k, tool_names=list(tools.keys()))
        if verbose:
            print(f"Best action: {best_action}")
        state = apply_action(state, best_action, tools)
        return state

    if verbose:
        print(f"--- lats_mcts (budget={budget}, k={branch_k}) ---")
    final_state, actions = lats_mcts(
        task,
        llm,
        scorer,
        tools,
        budget=budget,
        branch_k=branch_k,
        max_depth=max_depth,
        verbose=verbose,
    )
    if verbose:
        print("Selected path:")
        for i, a in enumerate(actions, 1):
            print(f"  {i}. {a}")
    return final_state
