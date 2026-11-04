from redis.asyncio import Redis

STATS_TTL = 600

async def stats_version(redis: Redis, user_id: int) -> int:
    return int(await redis.get(f"stats_ver:{user_id}") or 0)

async def bump_stats_version(redis: Redis, user_id: int) -> None:
    await redis.incr(f"stats_ver:{user_id}")