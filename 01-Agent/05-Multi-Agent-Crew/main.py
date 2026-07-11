from agent import DEFAULT_ORDER, DEFAULT_ROLES, create_deepseek_llm, run_crew


def main() -> None:
    llm = create_deepseek_llm()
    task = (
        "为团队写一段 150 字以内的说明：解释 ReAct Agent 是什么，"
        "以及它为什么需要 Observation。"
    )

    print(f"Task: {task}\n")
    thread = run_crew(
        task,
        DEFAULT_ROLES,
        llm,
        rounds=2,
        order=DEFAULT_ORDER,
        verbose=True,
    )
    print("\n" + "=" * 60)
    print("Final thread:")
    print("=" * 60)
    print(thread)


if __name__ == "__main__":
    main()
