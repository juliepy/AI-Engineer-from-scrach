import asyncio
from typing import Any, Awaitable, Callable


async def limited_llm_call(
    sema: asyncio.Semaphore,
    fn: Callable[..., Awaitable[Any]],
    *args,
    **kwargs,
):
    async with sema:
        return await fn(*args, **kwargs)
