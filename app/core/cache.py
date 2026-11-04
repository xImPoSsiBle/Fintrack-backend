from redis.asyncio import Redis
from redis.exceptions import RedisError
import structlog

STATS_TTL = 600

logger = structlog.get_logger(__name__)

async def stats_version(redis: Redis, user_id: int) -> int:
    return int(await redis.get(f"stats_ver:{user_id}") or 0)

async def bump_stats_version(redis: Redis, user_id: int) -> None:
    try:
        await redis.incr(f"stats_ver:{user_id}")
    except RedisError:
        logger.warning("stats_cache_invalidation_failed", user_id=user_id, exc_info=True)