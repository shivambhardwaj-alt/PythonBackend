from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from fastapi import Request, HTTPException , status
from src.auth.utils import decode_access_token
class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error = auto_error)
        
    async def __call__(self, request : Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials 
        token_data =  decode_access_token(token)
        if not self.token_valid(token):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED , detail  = "Unauthorized Action")
        if token_data['refresh']:
            raise HTTPException(status.HTTP_403_FORBIDDEN , detail = "Please Provide new token")
        return creds
    def token_valid(self,token : str ) -> bool : 
        token_data = decode_access_token(token)
        return True if token else False
    
            
        
    