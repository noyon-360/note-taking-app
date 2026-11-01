from pydantic import EmailStr, Field, field_validator

from app.common.enum import UserRole
from app.common.schemas import APIModel, Name, Password


class UserCreateSchema(APIModel):
    name: Name
    email: EmailStr
    password: Password
    role: UserRole
    interests: list[str] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.strip().lower()


class UserUpdateSchema(APIModel):
    name: Name | None = None
    email: EmailStr | None = None
    password: Password | None = None
    role: UserRole | None = None
    interests: list[str] | None = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(APIModel):
    id: str
    name: Name
    email: EmailStr
    role: UserRole
    interests: list[str]

    @classmethod
    def from_user(cls, user) -> "UserResponse":
        return cls(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            interests=user.interests,
        )
