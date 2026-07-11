# =============================================================================
#  main.py — 入口文件
#
#  运行方式：
#    cd 01-small-llm-function-call-project
#    python main.py
#
#  依赖：pip install openai python-dotenv
#  环境变量：DEEPSEEK_API_KEY（配置在同目录 .env 文件中）
# =============================================================================

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from agent.agent import chat_with_tools  # noqa: E402（需在 load_dotenv 之后导入）


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中配置。")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    print("=" * 60)
    print("LLM Function Calling 小工程")
    print("可用工具：reverse_string / basic_calculator")
    print("输入 'exit' 或 'quit' 退出")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n[你] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break
        print("\n\n")
        print("*" * 60)
        print(f"User>\t {user_input}")
        print("*" * 60)
        answer = chat_with_tools(client, user_input)
        print("\n\n")
        print("=" * 60)
        print(f"Assistant>\t {answer}")
        print("*" * 60)
        print(f"\n[助手] {answer}\n{'─' * 60}\n")


if __name__ == "__main__":
    main()
