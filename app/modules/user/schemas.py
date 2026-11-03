from beanie import PydanticObjectId
from pydantic import EmailStr, field_validator

from app.common.enum import UserRole
from app.common.schemas import APIModel, Name
from app.modules.post.schemas import PostResponse

# class UserCreateSchema(APIModel):
#     name: Name
#     email: EmailStr
#     password: Password
#     role: UserRole
#     interests: list[str] = Field(default_factory=list)

#     @field_validator("email")
#     @classmethod
#     def lowercase_email(cls, v: str) -> str:
#         return v.strip().lower()


class UserUpdateSchema(APIModel):
    name: Name | None = None
    email: EmailStr | None = None
    interests: list[str] | None = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str | None) -> str | None:
        return v.strip().lower() if v is not None else v


class UserRoleUpdateSchema(APIModel):
    role: UserRole


class UserResponse(APIModel):
    id: PydanticObjectId
    name: Name
    email: EmailStr
    role: UserRole
    interests: list[str]


class UserSummary(APIModel):
    id: PydanticObjectId
    name: str


class InterestGroupResponse(APIModel):
    interest: str
    user_count: int
    users: list[UserSummary]


class UserPostsResponse(APIModel):
    user: UserSummary
    posts: list[PostResponse]
