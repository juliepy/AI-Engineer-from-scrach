from agent import build_default_tools, create_deepseek_llm, reflect_until_success


def main() -> None:
    tools = build_default_tools()
    llm = create_deepseek_llm(
        system_prompt=(
            "You are a Reflection agent assistant. "
            "Follow the requested output format exactly. "
            "Use the same language as the task."
        )
    )
    task = "请帮我计算 21+21，并统计答案字符串有多少个字符。"

    print(f"Task: {task}\n")
    result = reflect_until_success(
        task,
        llm,
        tools,
        max_trials=3,
        max_action_steps=6,
        max_reflections=5,
        verbose=True,
    )
    print(f"\nFinal Result: {result}")


if __name__ == "__main__":
    main()
