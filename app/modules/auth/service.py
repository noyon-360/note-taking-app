from fastapi import status

from app.common.enum import UserRole
from app.core.exceptions import AppError
from app.core.security import DUMMY_HASH, create_access_token, hash_pass, verify_pass
from app.modules.auth.schemas import AuthResponse, RegisterSchema
from app.modules.user.schemas import UserResponse
from app.modules.user.services import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def _build_auth_response(self, user) -> AuthResponse:
        token = create_access_token(str(user.id), user.role.value)
        return AuthResponse(access_token=token, user=UserResponse.model_validate(user))

    async def register(self, data: RegisterSchema):
        pass_hash = await hash_pass(data.password)
        user = await self.user_service.create_user(
            name=data.name,
            email=data.email,
            pass_hash=pass_hash,
            role=UserRole.USER,
            interests=data.interests,
        )
        return self._build_auth_response(user)

    async def login(self, email: str, password: str):
        user = await self.user_service.get_user_by_email(email)
        hashed = user.pass_hash if user else DUMMY_HASH
        password_valid = await verify_pass(password, hashed)

        if user is None or not password_valid:
            raise AppError("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
        return self._build_auth_response(user)
