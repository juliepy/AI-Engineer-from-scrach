#!/usr/bin/env python3
"""
异步入门小 demo：看时间戳，理解「等待时去做别的事」。

运行:
  python 01-async-demo.py

你会看到：
  - 同步版：任务一个接一个，总耗时 ≈ 0.3 + 0.3 = 0.6 秒
  - gather：两个同时等，总耗时 ≈ 0.3 秒（在 gather 那一行一直等到齐）
  - create_task：先甩出去跑，主流程立刻继续；结束前再 await
"""

from __future__ import annotations

import asyncio
import time


def log(msg: str) -> None:
    """带时间戳的打印，方便看谁先谁后。"""
    now = time.strftime("%H:%M:%S")
    ms = int((time.time() % 1) * 1000)
    print(f"[{now}.{ms:03d}] {msg}")


# ---------------------------------------------------------------------------
# 1. 同步：傻等（对比用）
# ---------------------------------------------------------------------------
def sync_fetch(name: str, delay: float) -> str:
    log(f"{name} 开始（同步）")
    time.sleep(delay)  # 整个人卡住，谁也干不了
    log(f"{name} 结束（同步） 用了 {delay}s")
    return f"{name}-ok"


def run_sync() -> None:
    log("===== 同步开始 =====")
    t0 = time.perf_counter()

    a = sync_fetch("任务A", 0.3)
    b = sync_fetch("任务B", 0.3)

    cost = time.perf_counter() - t0
    log(f"同步结果: {a}, {b}")
    log(f"同步总耗时: {cost:.2f}s  （约 0.6，因为串行）")
    print()


# ---------------------------------------------------------------------------
# 2. 异步 gather：创建后立刻等齐
# ---------------------------------------------------------------------------
async def async_fetch(name: str, delay: float) -> str:
    log(f"{name} 开始（异步）")
    # await = 「我要等 delay 秒，你们先忙」
    await asyncio.sleep(delay)
    log(f"{name} 结束（异步） 用了 {delay}s")
    return f"{name}-ok"


async def run_async_gather() -> None:
    log("===== gather：创建后立刻等齐 =====")
    t0 = time.perf_counter()

    # 这行会卡住，直到 A、B 都结束，函数才继续
    a, b = await asyncio.gather(
        async_fetch("任务A", 0.3),
        async_fetch("任务B", 0.3),
    )

    cost = time.perf_counter() - t0
    log(f"gather 结果: {a}, {b}")
    log(f"gather 总耗时: {cost:.2f}s  （约 0.3）")
    print()


# ---------------------------------------------------------------------------
# 3. create_task：先甩出去，主流程继续；结束前再等
# ---------------------------------------------------------------------------
async def run_async_create_task() -> None:
    log("===== create_task：先启动，主流程继续 =====")
    t0 = time.perf_counter()

    # 只启动，这里不 await → 马上往下走
    task_a = asyncio.create_task(async_fetch("任务A", 0.3))
    task_b = asyncio.create_task(async_fetch("任务B", 0.3))
    log("主流程：任务已甩出，我继续干别的（A/B 还在跑）")

    # 模拟主流程自己的事（此时 A/B 在后台跑）
    await asyncio.sleep(0.05)
    log("主流程：顺便干完一件小事")

    # 离开前必须等它们。
    # 若这里不 await，asyncio.run 结束时会取消还没跑完的任务。
    a = await task_a
    b = await task_b

    cost = time.perf_counter() - t0
    log(f"create_task 结果: {a}, {b}")
    log(f"create_task 总耗时: {cost:.2f}s  （约 0.3；中间穿插了主流程）")
    print()


def main() -> None:
    run_sync()

    # 异步世界要靠 asyncio.run 启动
    asyncio.run(run_async_gather())
    asyncio.run(run_async_create_task())

    log("看完对比就懂了：")
    log("  同步 sleep              → 卡住整程序")
    log("  await gather            → 创建后立刻等到齐，再往下")
    log("  create_task 再 await    → 先甩出去跑，主流程可穿插；结束前要等齐")


if __name__ == "__main__":
    main()
