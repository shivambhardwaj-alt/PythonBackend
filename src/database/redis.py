import redis.asyncio as redis
from datetime import datetime, timezone

from config import Settings 
settings = Settings() # type: ignore

BLOCKLIST_PREFIX = "blocklist:"

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

print(f'Checking for the redis Client is : {redis_client.ping()}')
def _seconds_until(exp_timestamp: float) -> int:
    """Seconds from now until the token expires (at least 1, so Redis accepts it)."""
    now = datetime.now(timezone.utc).timestamp()
    remaining = exp_timestamp - now
    return max(int(remaining), 1)


async def add_jti_to_blocklist(jti: str, exp_timestamp: float) -> None:
    """Revoke a token until the moment it would have expired anyway."""
    await redis_client.set(
        f"{BLOCKLIST_PREFIX}{jti}",
        "1",
        ex=_seconds_until(exp_timestamp),
    )


async def token_in_blocklist(jti: str) -> bool:
    """True if this token ID has been revoked."""
    return await redis_client.exists(f"{BLOCKLIST_PREFIX}{jti}") == 1