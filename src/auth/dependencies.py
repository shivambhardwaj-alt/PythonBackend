
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.service import UserService
from src.auth.utils import TokenError, TokenType, decode_access_token
from src.database.database import AsyncSession, get_db
from src.database.redis import token_in_blocklist

user_service = UserService()



def unauthorized(message: str) -> HTTPException:
    
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(message: str) -> HTTPException:
  
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )



class TokenBearer(HTTPBearer):
    

    expected_type: TokenType

    def __init__(self):
        
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> dict:
        
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if credentials is None:
            raise unauthorized("Missing 'Authorization: Bearer <token>' header")

      
        try:
            payload = decode_access_token(credentials.credentials)
        except TokenError as error:
            raise unauthorized(error.message)
        if payload.get("type") != self.expected_type.value:
            raise unauthorized(f"Please provide an {self.expected_type.value} token")

        if await token_in_blocklist(payload["jti"]):
            raise unauthorized("Token has been revoked. Please log in again")

        return payload


class AccessTokenBearer(TokenBearer):
    
    expected_type = TokenType.ACCESS


class RefreshTokenBearer(TokenBearer):
    
    expected_type = TokenType.REFRESH



access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()



async def get_current_user(
    token_payload: dict = Depends(access_token_bearer),
    db: AsyncSession = Depends(get_db),
):
   
    email = token_payload.get("email")
    if not email:
        raise unauthorized("Token does not contain an email")

    user = await user_service.get_user_by_email(email, db)
    if user is None:
        raise unauthorized("User no longer exists")
    return user



class RoleChecker:
    

    def __init__(self, *allowed_roles: str):
        if not allowed_roles:
            raise ValueError("RoleChecker needs at least one role")
        self.allowed_roles = set(allowed_roles)

    async def __call__(self, current_user=Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise forbidden("You are not allowed to perform this action")
        return current_user

