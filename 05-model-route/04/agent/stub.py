import json

from .fake_llm import FakeLLM


def run_agent_stub(user_goal: str, tools: dict, llm: FakeLLM) -> str:
    """最小编排：第一轮让模型返回 tool JSON，第二轮返回最终答案。"""
    first = llm.chat([])
    # 简化：假定 first 就是要调用的 JSON 字符串
    action = json.loads(first)
    obs = tools[action["tool"]](**action["args"])
    second = llm.chat([{"role": "user", "content": str(obs)}])
    return second
