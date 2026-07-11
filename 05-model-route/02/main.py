# =============================================================================
#  2.5 tiktoken 计数 + 简单请求哈希缓存（模型路由 / 成本与重复请求优化）
# =============================================================================
#
#  - approx_token_count：估算 prompt token，无 tiktoken 时用 len//4 兜底
#  - request_fingerprint：system + user + model 做 SHA256，作为缓存键
#  - cached_exact / set_exact_cache：精确匹配缓存（演示用 LRU + 内存 dict，生产换 Redis）
#
# =============================================================================

import sys

from cache import (
    approx_token_count,
    cached_exact,
    request_fingerprint,
    set_exact_cache,
)

sys.stdout.reconfigure(encoding="utf-8")

SYSTEM = "你是简洁的技术助手。"
USER = "用三句话解释什么是 RAG。"
MODEL = "gpt-4o"


def call_model(system: str, user: str, model: str) -> str:
    """模拟 LLM 调用：先查缓存，未命中则「生成」并写入。"""
    hit = cached_exact(system, user, model)
    if hit is not None:
        return hit

    response = f"[mock:{model}] RAG 检索增强生成，把外部知识检索后再交给 LLM 回答。"
    set_exact_cache(system, user, model, response)
    return response


if __name__ == "__main__":
    prompt = f"{SYSTEM}\n{USER}"
    tokens = approx_token_count(prompt, MODEL)
    fp = request_fingerprint(SYSTEM, USER, MODEL)

    print("=== Token 计数 ===")
    print(f"  文本长度: {len(prompt)} 字符")
    print(f"  估算 token: {tokens}")
    print(f"  请求指纹: {fp[:16]}...")
    print()

    print("=== 精确缓存 ===")
    r1 = call_model(SYSTEM, USER, MODEL)
    print(f"  第 1 次调用（未命中）: {r1}")

    r2 = call_model(SYSTEM, USER, MODEL)
    print(f"  第 2 次调用（命中）:   {r2}")
    print(f"  两次结果相同: {r1 == r2}")
