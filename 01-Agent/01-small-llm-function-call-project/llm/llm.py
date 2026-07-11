# =============================================================================
#  llm.py — LLM 调用封装（请求 / 响应 / messages 追加）
# =============================================================================

import json

from openai import OpenAI

from tools import TOOLS


def print_message(message) -> None:
    """格式化打印单条消息（dict 或 ChatCompletionMessage），自动去掉 None 字段。"""
    if hasattr(message, "model_dump"):
        data = message.model_dump(exclude_none=True)
    elif isinstance(message, dict):
        data = {k: v for k, v in message.items() if v is not None}
    else:
        data = message
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_messages(messages: list) -> None:
    for i, msg in enumerate(messages):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "?")
        print(f"--- [{i}] {role} ---")
        print_message(msg)


def call_llm(client: OpenAI, messages: list[dict], model: str):
    print(f"\n=======>>> LLM request ======\n")
    print_messages(messages)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        temperature=0,
    )
    msg = response.choices[0].message

    print(f"\n=======<<< LLM response ======\n")
    print_message(msg)
    return msg


def append_assistant(messages: list[dict], msg) -> None:
    if hasattr(msg, "model_dump"):
        messages.append(msg.model_dump(exclude_none=True))
    else:
        record: dict = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            record["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        messages.append(record)
