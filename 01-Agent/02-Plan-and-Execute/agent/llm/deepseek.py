import os
from typing import Callable

from openai import OpenAI

from agent.config import load_env
from agent.llm.log import print_message, print_messages


def create_deepseek_llm(
    model: str = "deepseek-chat",
    api_key: str | None = None,
    base_url: str = "https://api.deepseek.com",
    system_prompt: str = "You are a helpful assistant. Follow instructions precisely.",
) -> Callable[[str], str]:
    """创建 DeepSeek 调用函数（OpenAI 兼容接口）。"""
    load_env()
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError(
            "未找到 API Key。请在项目根目录创建 .env 并设置 DEEPSEEK_API_KEY，"
            "或设置系统环境变量，或在 create_deepseek_llm(api_key=...) 中传入。"
        )

    client = OpenAI(api_key=key, base_url=base_url)

    def llm(prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        print("\n====>>> LLM request\n")
        print_messages(messages)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        msg = response.choices[0].message

        print("\n====<<< LLM response\n")
        print_message(msg)

        print(f"\nModel>\t {msg.content}\n")
        return msg.content or ""

    return llm
