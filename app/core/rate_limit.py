import time
from math import ceil
import uuid

from fastapi import HTTPException, status
from redis import RedisError
from redis.asyncio import Redis
import structlog


logger = structlog.get_logger(__name__)

async def check_rate_limit(redis: Redis, key: str, limit: int, window: int) -> None:
    now_ms = int(time.time() * 1000)
    
    try:
        async with redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, now_ms - window * 1000)
            pipe.zcard(key)
            pipe.zrange(key, 0, 0, withscores=True)
            _, count, oldest = await pipe.execute()
    except RedisError:
        logger.warning("rate_limit_check_failed", key=key, exc_info=True)
        return

    if count >= limit:
        oldest_ms = int(oldest[0][1])
        retry_after = max(1, ceil((oldest_ms + window*1000 - now_ms)/ 1000)) 
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Слишком много попыток входа, попробуйте позже",
            headers={"Retry-After": str(retry_after)},
        )

async def register_failure(redis: Redis, key: str, window: int) -> None:
    now_ms = int(time.time() * 1000)
    try:
        async with redis.pipeline(transaction=True) as pipe:
            pipe.zadd(key, {uuid.uuid4().hex: now_ms})
            pipe.expire(key, window)
            await pipe.execute()
    except RedisError:
        logger.warning("rate_limit_register_failed", key=key, exc_info=True)


async def clear_failures(redis: Redis, key: str) -> None:
    try:
        await redis.delete(key)
    except RedisError:
        logger.warning("rate_limit_clear_failed", key=key, exc_info=True)