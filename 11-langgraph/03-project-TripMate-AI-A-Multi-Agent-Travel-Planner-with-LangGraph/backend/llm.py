import os

from langchain_openai import ChatOpenAI

import backend.config  # noqa: F401 — load .env + SSL certs

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is missing. Please add it to your .env file.")

llm = ChatOpenAI(
    model="deepseek-v4-pro",
    api_key=DEEPSEEK_API_KEY,
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    temperature=0.7,
)
