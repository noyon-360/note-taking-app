from datetime import datetime
from typing import ClassVar

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.common.utils import utc_now


class Post(Document):
    title: str
    content: str
    author_id: PydanticObjectId
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "posts"
        indexes: ClassVar[list[IndexModel]] = [
            IndexModel(
                [("author_id", ASCENDING), ("_id", DESCENDING)],
            )
        ]
