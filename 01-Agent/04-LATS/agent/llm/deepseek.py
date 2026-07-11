import os
from typing import Callable

from openai import OpenAI

from agent.config import load_env


def create_deepseek_llm(
    model: str = "deepseek-chat",
    api_key: str | None = None,
    base_url: str = "https://api.deepseek.com",
    system_prompt: str = "You are a helpful assistant. Follow instructions precisely.",
) -> Callable[[str], str]:
    load_env()
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError(
            "未找到 API Key。请在项目根目录创建 .env 并设置 DEEPSEEK_API_KEY。"
        )

    client = OpenAI(api_key=key, base_url=base_url)

    def llm(prompt: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    return llm
