import os
from typing import Callable

from openai import OpenAI
from openai.types.chat.chat_completion_assistant_message_param import ContentArrayOfContentPart

from agent.config import load_env
from agent.llm.log import print_message, print_messages

_SYSTEM_PROMPT = (
    "You are a ReAct agent. Follow the requested format exactly. "
    "Output only ONE turn per response (Thought + Action + Action Input, OR Thought + Final Answer). "
    "Use tools when needed, then give Final Answer in the same language as the question."
)


def create_deepseek_llm(
    model: str = "deepseek-v4-pro",
    api_key: str | None = None,
    base_url: str = "https://api.deepseek.com",
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
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        print("\n====>>> LLM request \n")
        print_messages(messages)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        msg = response.choices[0].message

        print("\n====<<< LLM response\n")
        print_message(msg)
        
        print("\n\n")
        print(f"Model>\t {msg.content}")
        print("\n\n")
        return msg.content or ""

    return llm
