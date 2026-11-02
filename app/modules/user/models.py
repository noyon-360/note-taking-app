from typing import ClassVar

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel

from app.common.enum import UserRole
from app.common.schemas import Name


class User(Document):
    name: Name
    email: EmailStr
    pass_hash: str
    role: UserRole = UserRole.USER
    interests: list[str] = Field(default_factory=list)

    class Settings:
        name = "users"
        indexes: ClassVar[list[IndexModel]] = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("interests", ASCENDING)]),
        ]
