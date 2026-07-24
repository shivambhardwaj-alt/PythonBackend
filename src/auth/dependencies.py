from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from fastapi import Request, HTTPException, status , Depends
from src.auth.utils import decode_access_token
from src.database.redis import token_in_blocklist
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_db

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
  

        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_access_token(token)

    

        if not self.token_valid(token):
            print("Error happened")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or expired"
            )
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN , detail = {
                    "error" : "This token is invalid or has been revoked",
                    "resolution" : "Plase get a new token"
                } 
            )

        self.verify_token(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_access_token(token)
 
        return token_data is not None

    def verify_token(self, token_data):
        raise NotImplementedError("Please Override this method in dependencies")



class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict):
   
        if token_data and token_data.get('refresh'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please Provide an access token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict):
        
        if not token_data or not token_data.get('refresh'):
            print(token_data)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please Provide a refresh token"
            )
def getCurrentUser(token_details : dict = Depends(AccessTokenBearer)):
    print(token_details)
    