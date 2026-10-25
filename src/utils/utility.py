import uuid 
from datetime import datetime , timedelta , timezone 
from enum import Enum
import bcrypt 
import jwt 


from config import Settings


settings = Settings() # type: ignore

class TokenType(str, Enum):
    ACCESS  = 'access'
    REFRESH = 'refresh'
    
class TokenError(Exception):
    def __init__(self,message : str):
        self.message = message
        super().__init__(message)

        
