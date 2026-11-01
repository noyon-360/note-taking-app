import re

from pydantic import EmailStr, Field, ValidationInfo, field_validator

from app.common.schemas import APIModel, Name
from app.modules.user.schemas import UserResponse


class RegisterSchema(APIModel):
    name: Name
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    confirm_password: str = Field(max_length=128)
    interests: list[str] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("password must contain at least one letter and one number")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        # password is missing from info.data when it already failed its own checks.
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v


class LoginSchema(APIModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.strip().lower()


class AuthResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
