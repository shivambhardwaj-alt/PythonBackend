"""
Auth dependencies for FastAPI.

Order of checks on a protected request:
    1. TokenBearer reads "Authorization: Bearer <token>"
    2. decode_token() verifies the signature and expiry
    3. The token type is checked (access vs refresh)
    4. The token's jti is checked against the Redis blocklist
    5. get_current_user() loads the user from the database
    6. RoleChecker compares the user's role with the allowed roles
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.service import UserService
from src.auth.utils import TokenError, TokenType, decode_token
from src.database.database import AsyncSession, get_db
from src.database.redis import token_in_blocklist

user_service = UserService()


# ─────────────────────────────────────────────────────────────
# Error helpers
# ─────────────────────────────────────────────────────────────
def unauthorized(message: str) -> HTTPException:
    """401: we don't know who you are (missing / bad / expired token)."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(message: str) -> HTTPException:
    """403: we know who you are, but you're not allowed to do this."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


# ─────────────────────────────────────────────────────────────
# Token checking
# ─────────────────────────────────────────────────────────────
class TokenBearer(HTTPBearer):
    """
    Base class with all the checking logic.
    Subclasses only set `expected_type`.
    Returns the decoded token payload (a dict).
    """

    expected_type: TokenType

    def __init__(self):
        # auto_error=False: return None for a missing header, so we can raise our own 401
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> dict:
        # 1. Read the header
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if credentials is None:
            raise unauthorized("Missing 'Authorization: Bearer <token>' header")

        # 2. Verify signature and expiry
        try:
            payload = decode_token(credentials.credentials)
        except TokenError as error:
            raise unauthorized(error.message)

        # 3. Right kind of token for this endpoint?
        if payload.get("type") != self.expected_type.value:
            raise unauthorized(f"Please provide an {self.expected_type.value} token")

        # 4. Revoked by logout?
        if await token_in_blocklist(payload["jti"]):
            raise unauthorized("Token has been revoked. Please log in again")

        return payload


class AccessTokenBearer(TokenBearer):
    """Accepts only access tokens. Use on normal API routes."""
    expected_type = TokenType.ACCESS


class RefreshTokenBearer(TokenBearer):
    """Accepts only refresh tokens. Use only on /refresh_token."""
    expected_type = TokenType.REFRESH


# Create once, reuse everywhere
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()


# ─────────────────────────────────────────────────────────────
# Current user
# ─────────────────────────────────────────────────────────────
async def get_current_user(
    token_payload: dict = Depends(access_token_bearer),
    db: AsyncSession = Depends(get_db),
):
    """Load the user who owns the access token. The role comes from the database."""
    email = token_payload.get("email")
    if not email:
        raise unauthorized("Token does not contain an email")

    user = await user_service.get_user_by_email(email, db)
    if user is None:
        raise unauthorized("User no longer exists")
    return user


# ─────────────────────────────────────────────────────────────
# Roles
# ─────────────────────────────────────────────────────────────
class RoleChecker:
    """
    admin_only = RoleChecker("admin")
    any_user   = RoleChecker("admin", "user")

    @router.delete("/{id}", dependencies=[Depends(admin_only)])
    async def route(user = Depends(admin_only)):   # also gives you the user
    """

    def __init__(self, *allowed_roles: str):
        if not allowed_roles:
            raise ValueError("RoleChecker needs at least one role")
        self.allowed_roles = set(allowed_roles)

    async def __call__(self, current_user=Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise forbidden("You are not allowed to perform this action")
        return current_user


admin_only = RoleChecker("admin")
any_user = RoleChecker("admin", "user")