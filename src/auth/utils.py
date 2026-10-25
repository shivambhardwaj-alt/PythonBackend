from passlib.context import CryptContext
from datetime import datetime, timedelta , timezone
from fastapi import HTTPException
from config import Config
from config import Settings
from enum import Enum
import jwt
import uuid
password_context = CryptContext(
    schemes=['bcrypt']
)
def generate_password_hash(password : str):
    return password_context.hash(password)
def verify_password(password : str , hash : str):
    return password_context.verify(password , hash)


settings = Settings() # type: ignore
class TokenType (str, Enum ):
    ACCESS  = "access" 
    REFRESH = "refresh"


class TokenError(Exception):
    def __init__(self, message):
        self.message = message 
        super().__init__(message) 
   

EXPIRY = timedelta(hours= 24)

def create_token( user_data : dict , type : str ):
    now = datetime.now(timezone.utc)
    payload = {
    "sub" : user_data['user_uid'],
    "email" : user_data['email'],
    "role" : user_data['role'],
    "type" : type,
    "jti" : str(uuid.uuid4()),
    "iat" : now ,
    "exp": now + EXPIRY
    
    }
    
    
    return jwt.encode(payload= payload,key = settings.JWT_SECRET , algorithm  = settings.JWT_ALGORITHM)

def generate_access_token( user_data : dict , type : str):
    return create_token(user_data , type)
def generate_refresh_token(user_data: dict, type : str ):
    return create_token(user_data, type)

def decode_access_token(token : str) :
    try :  
        token_data = jwt.decode(
            jwt = token,
            key = Config.JWT_SECRET,
            algorithms = [Config.JWT_ALGORITHM] 
            )
        return token_data
    except jwt.PyJWTError as e :
        raise Exception("Jwt is not working fine !!!")

        