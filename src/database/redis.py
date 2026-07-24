import redis.asyncio as redis
from config import Config

token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True,  
)

JTI_EXPIRY = 3600


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY, 
    )


async def token_in_blocklist(jti: str) -> bool:
    token = await token_blocklist.get(jti)
    return token is not None