from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from fastapi import Request, HTTPException , status
from src.auth.utils import decode_access_token
class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error = auto_error)
        
    async def __call__(self, request: Request):

        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_access_token(token)

        if not self.token_valid(token):
            raise HTTPException(...)

        self.verify_token(token_data)

        return token_data
    def token_valid(self,token : str ) -> bool : 
        token_data = decode_access_token(token)
        return True if token else False
    def verify_token(self, token_data):
        raise NotImplementedError("Please Override this method in dependencies")
    
class AcessTokenBearer(TokenBearer):
    def verify_token(self, token_data : dict):
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail = "Please Provide an access token"
            )
    
class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data : dict):
        if token_data and not token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail  = "Please Provide a refresh token")
        
    