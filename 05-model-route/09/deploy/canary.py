import hashlib


def pick_canary_version(user_id: str, canary_pct: int = 10) -> str:
    """金丝雀：按 user_id 哈希稳定分流 small % 到新版本。"""
    bucket = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
    return "v2-canary" if bucket < canary_pct else "v1-stable"


def describe_canary() -> str:
    return (
        "金丝雀：新版本接 5%~10% 流量，观察错误率/latency/成本后逐步放量；"
        "适合模型/API 频繁迭代。"
    )
