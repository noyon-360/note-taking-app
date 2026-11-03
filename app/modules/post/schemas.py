from datetime import datetime
from typing import Annotated

from beanie import PydanticObjectId
from pydantic import StringConstraints

from app.common.schemas import APIModel


class PostCreateSchema(APIModel):
    title: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]
    content: Annotated[str, StringConstraints(min_length=1, max_length=20_000)]


class PostResponse(APIModel):
    id: PydanticObjectId
    title: str
    content: str
    author_id: PydanticObjectId
    created_at: datetime
