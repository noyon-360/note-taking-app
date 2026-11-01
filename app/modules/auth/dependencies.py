from typing import Annotated

import jwt
from beanie import PydanticObjectId
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.modules.auth.service import AuthService
from app.modules.user.models import User
from app.modules.user.services import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_service() -> UserService:
    return UserService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(user_service: UserServiceDep) -> AuthService:
    return AuthService(user_service=user_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise AppError(
            "Authorization credentials are missing", status.HTTP_401_UNAUTHORIZED
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise AppError("Invalid token", status.HTTP_401_UNAUTHORIZED)
    user = await User.get(PydanticObjectId(payload["sub"]))
    if user is None:
        raise AppError("User not found", status_code=status.HTTP_401_UNAUTHORIZED)
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
