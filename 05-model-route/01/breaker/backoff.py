import random


def exponential_backoff(attempt: int, base: float = 0.5, cap: float = 8.0) -> float:
    jitter = random.random() * 0.25
    return min(cap, base * (2**attempt) + jitter)
