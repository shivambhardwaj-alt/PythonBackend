from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status
from src.auth.utils import decode_access_token


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
  

        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_access_token(token)
    

        if not self.token_valid(token):
            print("Error happened")
            # FIXED: `raise HTTPException(...)` was using literal Ellipsis (...) 
            # instead of real arguments — this would crash instead of returning 
            # a proper 401 response.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or expired"
            )

        self.verify_token(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_access_token(token)
        # FIXED: was checking `token` (the raw string, always truthy) instead of
        # `token_data` (the decoded payload). This meant invalid/expired tokens
        # would always pass validation as long as *some* string was sent.
        return token_data is not None

    def verify_token(self, token_data):
        raise NotImplementedError("Please Override this method in dependencies")


# FIXED: typo `AcessTokenBearer` -> `AccessTokenBearer` (missing "c")
class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict):
        # FIXED: `token_data['refresh']` would raise KeyError if "refresh" key
        # is missing from the payload — switched to `.get()` for safety.
        if token_data and token_data.get('refresh'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please Provide an access token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict):
        # FIXED: same KeyError risk as above, fixed with `.get()`
        if not token_data or not token_data.get('refresh'):
            print(token_data)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please Provide a refresh token"
            )