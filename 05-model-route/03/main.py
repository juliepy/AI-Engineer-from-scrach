# =============================================================================
#  6.5 异步 + 信号量 + 简易双层缓存（模型路由 / 高并发调用）
# =============================================================================
#
#  - TwoLevelCache：L1 进程内 dict + L2 Redis（演示用内存 mock）
#  - limited_llm_call：Semaphore 限制并发，防止打爆下游 API
#
# =============================================================================

import asyncio
import sys
import time

from runtime import TwoLevelCache, limited_llm_call

sys.stdout.reconfigure(encoding="utf-8")

CONCURRENCY = 2
CALL_DELAY = 0.3


async def mock_llm(prompt: str) -> str:
    await asyncio.sleep(CALL_DELAY)
    return f"[llm] {prompt}"


async def cached_llm(
    cache: TwoLevelCache,
    sema: asyncio.Semaphore,
    key: str,
    prompt: str,
) -> str:
    hit = await cache.get(key)
    if hit is not None:
        return f"{hit} (cache_hit)"

    result = await limited_llm_call(sema, mock_llm, prompt)
    await cache.set(key, result)
    return result


async def main():
    cache = TwoLevelCache()
    sema = asyncio.Semaphore(CONCURRENCY)

    unique = [
        ("q-rag", "什么是 RAG？"),
        ("q-agent", "什么是 Agent？"),
        ("q-route", "什么是模型路由？"),
    ]
    repeat = [
        ("q-rag", "什么是 RAG？"),
        ("q-agent", "什么是 Agent？"),
        ("q-route", "什么是模型路由？"),
    ]

    print(f"=== 阶段 1：{len(unique)} 路并发（上限 {CONCURRENCY}）===")
    t0 = time.perf_counter()
    first = await asyncio.gather(
        *[cached_llm(cache, sema, key, prompt) for key, prompt in unique]
    )
    warm_elapsed = time.perf_counter() - t0
    for (key, prompt), ans in zip(unique, first):
        print(f"  [{key}] {prompt} -> {ans}")
    print(f"  耗时: {warm_elapsed:.2f}s")
    print()

    print("=== 阶段 2：相同 key 再次请求（应全部 L1 命中）===")
    t1 = time.perf_counter()
    second = await asyncio.gather(
        *[cached_llm(cache, sema, key, prompt) for key, prompt in repeat]
    )
    hit_elapsed = time.perf_counter() - t1
    for (key, prompt), ans in zip(repeat, second):
        print(f"  [{key}] {prompt} -> {ans}")
    print(f"  耗时: {hit_elapsed:.2f}s（应接近 0）")
    print(f"L1 条目数: {len(cache.l1)}")


if __name__ == "__main__":
    asyncio.run(main())
