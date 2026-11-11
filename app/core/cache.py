from redis.asyncio import Redis
from redis.exceptions import RedisError
import structlog

STATS_TTL = 600

logger = structlog.get_logger(__name__)

async def stats_version(redis: Redis, user_id: int) -> int | None:
    try:
        return int(await redis.get(f"stats_ver:{user_id}") or 0)
    except RedisError:
        logger.warning("stats_version_failed", user_id=user_id)
        return None

async def bump_stats_version(redis: Redis, user_id: int) -> None:
    try:
        await redis.incr(f"stats_ver:{user_id}")
    except RedisError:
        logger.warning("stats_cache_invalidation_failed", user_id=user_id)

async def cache_get(redis: Redis, key: str) -> str | None:
    try:
        return await redis.get(key)
    except RedisError:
        logger.warning("cache_get_failed", key=key)
        return None

async def cache_set(redis: Redis, key: str, value: str | bytes, ttl: int) -> None:
    try:
        await redis.set(key, value, ex=ttl)
    except RedisError:
        logger.warning("cache_set_failed", key=key)