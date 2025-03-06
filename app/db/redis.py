import redis.asyncio as aioredis

from app.config import Config

JTI_EXPIRY = 3600

token_blocklist = aioredis.from_url(Config.REDIS_URL)

async def add_sub_to_blocklist(sub: str) -> None:
    await token_blocklist.set(name=sub, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(sub: str) -> bool:
    sub = await token_blocklist.get(sub)
    return sub is not None

