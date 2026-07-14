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

    prompt = "查看当前日期，把当前日期所有的数字求和，并返回结果。"

    print(f"user prompt: {prompt}\n")
    result = plan_and_execute(prompt, llm, tools, max_replans=2, verbose=True)
    print(f"\nFinal Result: {result}")


if __name__ == "__main__":
    main()
