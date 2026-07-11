from dataclasses import dataclass


def approx_token_count(text: str) -> int:
    """本地估算（tiktoken 不可用时的兜底）。"""
    return max(1, len(text) // 4)


@dataclass
class UsageFromAPI:
    prompt_tokens: int
    completion_tokens: int

    @property
    def total(self) -> int:
        return self.prompt_tokens + self.completion_tokens
