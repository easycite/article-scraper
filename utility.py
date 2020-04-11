import asyncio
from typing import Awaitable

async def wait_unless_cancelled(coroutine, cancel_event: asyncio.Event):
    task = asyncio.create_task(coroutine)

    done, _ = await asyncio.wait({ task, cancel_event.wait() }, return_when=asyncio.FIRST_COMPLETED)
    if not task in done:
        task.cancel()
    return await task
