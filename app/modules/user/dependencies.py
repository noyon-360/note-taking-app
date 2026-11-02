from typing import Annotated

from fastapi import Depends

from app.modules.user.services import UserService


def get_user_service() -> UserService:
    return UserService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
