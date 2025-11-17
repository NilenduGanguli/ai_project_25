"""
Wrapper to run synchronous Oracle database operations in async context
"""
import asyncio
from functools import wraps
from typing import Callable, Any


def run_in_threadpool(func: Callable) -> Callable:
    """Decorator to run synchronous database operations in a thread pool"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper
