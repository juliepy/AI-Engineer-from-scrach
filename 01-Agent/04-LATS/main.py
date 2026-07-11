from agent import (
    build_default_tools,
    combined_scorer,
    create_deepseek_llm,
    heuristic_scorer,
    lats_solve,
    make_llm_scorer,
)


def main() -> None:
    tools = build_default_tools()
    llm = create_deepseek_llm(
        system_prompt=(
            "You are a Language Agent Tree Search (LATS) planner. "
            "Propose distinct next actions in the requested format. "
            "Use the same language as the task."
        )
    )
    scorer = combined_scorer(heuristic_scorer, make_llm_scorer(llm), llm_weight=0.25)

    task = "请帮我计算 21+21，并统计答案字符串有多少个字符。"

    print(f"Task: {task}\n")

    print("=" * 60)
    print("1) lats_one_step — 扩展 3 候选，选分最高的一步")
    print("=" * 60)
    state1 = lats_solve(
        task, llm, scorer, tools, mode="one_step", branch_k=3, verbose=True
    )
    print(f"\nState after one step:\n{state1}\n")

    print("=" * 60)
    print("2) lats_mcts — Select / Expand / Simulate / Backpropagate")
    print("=" * 60)
    state2 = lats_solve(
        task,
        llm,
        scorer,
        tools,
        mode="mcts",
        budget=6,
        branch_k=3,
        max_depth=3,
        verbose=True,
    )
    print(f"\nFinal State:\n{state2}")


if __name__ == "__main__":
    main()
