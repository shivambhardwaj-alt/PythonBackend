from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status, Depends
from src.auth.utils import decode_access_token
from src.database.redis import token_in_blocklist


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        print("Request came here [TokenBearer.__init__]")
       
        HTTPBearer.__init__(self, auto_error=auto_error)

    async def __call__(self, request: Request):
        print("Request also came here [TokenBearer.__call__]")

        
        creds: HTTPAuthorizationCredentials = await HTTPBearer.__call__(self, request)

        token = creds.credentials
        print("Credentials extracted:", creds)

        token_data = decode_access_token(token)

        if token_data is None:
            print("Error happened: token could not be decoded")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or expired",
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get a new token",
                },
            )

       
        self.verify_token(token_data)

        return token_data

    def verify_token(self, token_data: dict):
        
        
        raise NotImplementedError("Please override this method in a subclass")


class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict):
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict):
        if not token_data or not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )



access_token_bearer = AccessTokenBearer()


def get_current_user(token_details: dict = Depends(access_token_bearer)):
    print("Inside route handler, token_details =", token_details)
    return token_details