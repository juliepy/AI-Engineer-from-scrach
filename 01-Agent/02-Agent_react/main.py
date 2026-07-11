import sys

from agent import build_default_tools, create_deepseek_llm, react_loop

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    tools = build_default_tools()
    llm = create_deepseek_llm()
    question = "请帮我计算 21+21，并统计答案字符串有多少个字符, 并且打印当前时间。"

    print("=" * 60)
    print("ReAct Agent 示例")
    print("可用工具：calculator / get_current_time / word_count")
    print("=" * 60)
    print("\n")
    print("*" * 60)
    print(f"User>\t {question}")
    print("*" * 60)

    result = react_loop(question, tools, llm)

    print("\n")
    print("=" * 60)
    print(f"Assistant>\t {result}")
    print("=" * 60)


if __name__ == "__main__":
    main()
