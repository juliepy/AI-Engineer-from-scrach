# =============================================================================
#  agent.py — Function Calling 编排（工具执行 + 对话循环）
# =============================================================================

import json

from openai import OpenAI

from agent.prompt import SYSTEM_PROMPT
from llm.llm import append_assistant, call_llm
from tools import TOOL_HANDLERS


def _execute_tool(name: str, arguments: str) -> str:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return f"ERROR: unknown tool '{name}'"
    try:
        args = json.loads(arguments or "{}")
        return str(handler(**args))
    except Exception as exc:
        return f"ERROR: {exc}"


def chat_with_tools(client: OpenAI, user_message: str, model: str = "deepseek-v4-pro") -> str:
    """单问题问答：最多 1 次工具调用 + 1 次最终生成。"""
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    msg = call_llm(client, messages, model)
    append_assistant(messages, msg)

    if not msg.tool_calls:
        return msg.content or ""

    for tc in msg.tool_calls:
        result = _execute_tool(tc.function.name, tc.function.arguments)
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    final_msg = call_llm(client, messages, model)
    print(f"Model>\t {final_msg.content or ''}")
    return final_msg.content or ""
