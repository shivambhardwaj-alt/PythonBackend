import hashlib
import hmac 
import secrets
from config import Settings
from src.database.redis import redis_client

OTP_TTL_SECONDS = 600 
MAX_ATTEMPTS =  5 
RESEND_COOLDOWN_SECONDS =  60
settings = Settings()  # type: ignore

def _key(kind : str , email : str) ->str :
    return f'{kind}:{email}'
def generate_otp() :
    return f'{secrets.randbelow(1_000_000):06d}'
    
def hashOtp(email : str, otp : str) -> str : 
    message = f'{email.lower()}:{otp}'.encode()
    return hmac.new(settings.JWT_SECRET.encode(), message, hashlib.sha256).hexdigest()
async def can_send_otp(email : str) -> bool : 
    created = await redis_client.set(
        _key("otp_cooldown", email), "1", ex=RESEND_COOLDOWN_SECONDS, nx=True
    )
    return bool(created) 
async def store_top(email : str , otp : str) -> None : 
    await redis_client.set(_key("otp", email), hashOtp(email,otp), ex=OTP_TTL_SECONDS)
    await redis_client.delete(_key("otp_attempts", email))
    
async def check_otp(email : str , otp : str) ->   str: 
    stored_hash : str = await redis_client.get(_key("otp" , email)) # pyright: ignore[reportAssignmentType]
    if stored_hash is None : 
        return "expired"
    attempts = await redis_client.incr(_key("otp_attempts" ,email))
    if attempts == 1 : 
        await redis_client.expire(_key("otp_attempts" , email), OTP_TTL_SECONDS)
    if attempts > MAX_ATTEMPTS:
        await redis_client.delete(_key("otp" , email) , _key("otp_attempts" , email))
        return "too many"
    if hmac.compare_digest(stored_hash, hashOtp(email, otp)):
        await redis_client.delete(_key("otp", email), _key("otp_attempts", email))
        return "ok"
    return "invalid"
        