"""JSON 日志工具（与 01-small-llm-function-call-project 风格一致）。"""

import json


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
