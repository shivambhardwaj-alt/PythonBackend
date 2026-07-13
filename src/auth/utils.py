from passlib.context import CryptContext
from datetime import datetime, timedelta
from config import Config
import jwt
import uuid
password_context = CryptContext(
    schemes=['bcrypt']
)
def generate_password_hash(password : str):
    return password_context.hash(password)
def verify_password(password : str , hash : str):
    return password_context.verify(password , hash)


def generate_access_token(user_data : dict , expiry : timedelta = timedelta(minutes=15) , refresh : bool  = False):
    payload = {}
    payload["user"] = user_data
    payload['exp'] = datetime.now() + expiry
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh
    token = jwt.encode(payload= payload , key = Config.JWT_SECRET , algorithm=Config.JWT_ALGORITHM)
    return token
    
    
def decode_access_token(token : str) :
    try :  
        token_data = jwt.decode(
            jwt = token,
            key = Config.JWT_SECRET,
            algorithms = [Config.JWT_ALGORITHM] 
            )
        return token_data
    except jwt.PyJWTError as e :
        print(e)
        return None 
        