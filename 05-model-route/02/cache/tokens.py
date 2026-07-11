try:
    import tiktoken
except ImportError:
    tiktoken = None


def approx_token_count(text: str, model: str = "gpt-4o") -> int:
    if tiktoken is None:
        return max(1, len(text) // 4)
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))
