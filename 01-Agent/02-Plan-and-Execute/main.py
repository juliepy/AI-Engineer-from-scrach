from agent import build_default_tools, create_deepseek_llm, plan_and_execute


def main() -> None:
    tools = build_default_tools()
    llm = create_deepseek_llm(
        system_prompt=(
            "You are a Plan-and-Execute agent assistant. "
            "When planning, output numbered steps one per line. "
            "When executing or summarizing, use the same language as the task."
        )
    )
    task = "请帮我计算 21+21，并统计答案字符串有多少个字符。"

    print(f"Task: {task}\n")
    result = plan_and_execute(task, llm, tools, max_replans=2, verbose=True)
    print(f"\nFinal Result: {result}")


if __name__ == "__main__":
    main()
