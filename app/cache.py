import redis.asyncio as aioredis
from app.config import settings

redis_client = None

async def connect_cache():
    global redis_client
    redis_client = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True
    )
    await redis_client.ping()
    print(f"[Cache] Connected to Redis at {settings.redis_host}:{settings.redis_port}")

async def close_cache():
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_cached(key: str):
    return await redis_client.get(f"url:{key}")

async def set_cached(key: str, value: str, ttl: int = None):
    ttl = ttl or settings.redis_ttl
    await redis_client.setex(f"url:{key}", ttl, value)

async def increment_clicks(alias: str):
    await redis_client.incr(f"clicks:{alias}")

async def get_click_count(alias: str):
    val = await redis_client.get(f"clicks:{alias}")
    return int(val) if val else 0