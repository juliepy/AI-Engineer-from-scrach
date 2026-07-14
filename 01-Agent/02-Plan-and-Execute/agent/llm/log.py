"""日志工具：content 按原文换行打印，避免 JSON 转义成 \\n。"""

import json


def _to_dict(message) -> dict:
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    if isinstance(message, dict):
        return {k: v for k, v in message.items() if v is not None}
    return {"value": message}


def print_message(message) -> None:
    """打印单条消息；content 单独按多行原文输出，其余字段仍用 JSON。"""
    data = _to_dict(message)
    content = data.pop("content", None)

    extras = {k: v for k, v in data.items() if k != "role"}
    if extras:
        print(json.dumps(extras, indent=2, ensure_ascii=False))

    if content is None:
        return

    print("content:")
    text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    for line in text.strip("\n").splitlines():
        print(f"  {line}")


def print_messages(messages: list) -> None:
    for i, msg in enumerate(messages):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "?")
        print(f"--- [{i}] {role} ---")
        print_message(msg)
