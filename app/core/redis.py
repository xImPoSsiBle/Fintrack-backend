from redis import asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(
    settings.redis_url, 
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
    )

async def get_redis() -> aioredis.Redis:
    return redis_client