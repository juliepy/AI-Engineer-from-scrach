from functools import lru_cache

from .fingerprint import request_fingerprint

# 生产环境请用 Redis；此处演示用内存 dict
_STORE: dict[str, str] = {}


@lru_cache(maxsize=1024)
def cached_exact(system: str, user: str, model: str) -> str | None:
    key = request_fingerprint(system, user, model)
    return _STORE.get(key)


def set_exact_cache(system: str, user: str, model: str, response: str) -> None:
    key = request_fingerprint(system, user, model)
    # redis.setex(key, ttl, response)
    _STORE[key] = response
    cached_exact.cache_clear()  # 演示用，勿在生产使用
