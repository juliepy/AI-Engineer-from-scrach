from typing import Callable


def run_crew(
    task: str,
    roles: dict[str, str],
    llm: Callable[[str], str],
    rounds: int = 2,
    order: list[str] | None = None,
    verbose: bool = False,
) -> str:
    """
    7.5 多角色轮询：固定顺序在多轮内传递同一条对话线程 thread。

    每轮按 order 依次调用各角色；reply 追加到 thread，供后续角色阅读。
    """
    thread = f"Task: {task}\n"
    role_order = order or ["researcher", "writer", "reviewer"]

    for round_idx in range(1, rounds + 1):
        if verbose:
            print(f"\n========== Round {round_idx}/{rounds} ==========")
        for role_name in role_order:
            if role_name not in roles:
                raise KeyError(f"角色 '{role_name}' 未在 roles 中定义，已有: {list(roles)}")
            prompt = roles[role_name] + "\n\n" + thread
            print("\n\n----------------------------------------------------------------")
            print(f"Crew prompt: {prompt}")
            print("----------------------------------------------------------------")
            reply = llm(prompt)
            print("\n\n----------------------------------------------------------------")
            print(f"Crew out: {reply}")
            print("----------------------------------------------------------------")
            thread += f"\n[{role_name}]:\n{reply}\n"
            if verbose:
                print(f"\n--- [{role_name}] ---\n{reply[:500]}{'...' if len(reply) > 500 else ''}")

    return thread
