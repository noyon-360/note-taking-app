from datetime import datetime
from typing import ClassVar

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.common.utils import utc_now


class Note(Document):
    title: str
    content: str
    owner_id: PydanticObjectId
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "notes"
        indexes: ClassVar[list[IndexModel]] = [
            IndexModel([("owner_id", ASCENDING), ("created_at", DESCENDING)]),
        ]
