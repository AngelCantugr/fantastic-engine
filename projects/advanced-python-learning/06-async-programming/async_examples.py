"""Async Programming Examples"""
import asyncio
from typing import List

async def fetch_data(item_id: int, delay: float = 1.0) -> dict:
    """Simulate async API call."""
    print(f"[START] Fetching item {item_id}")
    await asyncio.sleep(delay)
    print(f"[DONE] Fetched item {item_id}")
    return {"id": item_id, "data": f"Item {item_id} data"}

async def concurrent_fetches():
    """Fetch multiple items concurrently."""
    tasks = [fetch_data(i, 0.5) for i in range(5)]
    results = await asyncio.gather(*tasks)
    return results

async def async_generator(count: int):
    """Async generator example."""
    for i in range(count):
        await asyncio.sleep(0.1)
        yield i

async def consume_async_gen():
    """Consume async generator."""
    async for value in async_generator(5):
        print(f"Generated: {value}")

class AsyncContextManager:
    """Async context manager example."""
    async def __aenter__(self):
        print("[ACQUIRE] Resource")
        await asyncio.sleep(0.1)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        print("[RELEASE] Resource")
        await asyncio.sleep(0.1)

async def rate_limited_task(sem: asyncio.Semaphore, task_id: int):
    """Task with semaphore rate limiting."""
    async with sem:
        print(f"Task {task_id} running")
        await asyncio.sleep(0.5)
        return task_id * 2

async def main():
    print("=== Concurrent Fetching ===")
    results = await concurrent_fetches()
    
    print("\n=== Async Generator ===")
    await consume_async_gen()
    
    print("\n=== Async Context Manager ===")
    async with AsyncContextManager():
        print("Using resource")
    
    print("\n=== Rate Limiting with Semaphore ===")
    sem = asyncio.Semaphore(2)
    results = await asyncio.gather(*[rate_limited_task(sem, i) for i in range(5)])
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
