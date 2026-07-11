"""Tool: reverse_string — 将输入字符串反转后返回。"""


def reverse_string(text: str) -> str:
    """反转字符串并返回结果。"""
    text = (text or "").strip()
    if not text:
        return "ERROR: text is required"
    result = text[::-1]
    return result


# ── JSON Schema（供 OpenAI tools 参数使用）─────────────────────────────────────

SCHEMA = {
    "type": "function",
    "function": {
        "name": "reverse_string",
        "description": "将给定的字符串反转后返回，例如 'hello' → 'olleh'。",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "需要反转的原始字符串。",
                }
            },
            "required": ["text"],
        },
    },
}
