def run(text: str) -> str:
    text = text.strip()
    if not text:
        return "字符数: 0, 词数: 0"
    return f"字符数: {len(text)}, 词数: {len(text.split())}"
