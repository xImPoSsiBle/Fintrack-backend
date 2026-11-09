from redis.asyncio import Redis

def _key(user_id: int, jti: str) -> str:
    return f"refresh:{user_id}:{jti}"

async def store_refresh(redis: Redis, user_id: int, jti: str, ttl_seconds: int) -> None:
    await redis.set(_key(user_id, jti), "1", ex=ttl_seconds)

async def consume_refresh(redis: Redis, user_id: int, jti: str) -> bool:
    return await redis.delete(_key(user_id, jti)) == 1