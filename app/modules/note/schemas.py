from datetime import datetime
from typing import Annotated

from beanie import PydanticObjectId
from pydantic import ConfigDict, StringConstraints

from app.common.schemas import APIModel

NoteTitle = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
NoteContent = Annotated[str, StringConstraints(min_length=1, max_length=20_000)]


class NoteCreateSchema(APIModel):
    title: NoteTitle
    content: NoteContent


class NoteUpdateSchema(APIModel):
    title: NoteTitle | None = None
    content: NoteContent | None = None


class NoteResponse(APIModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    title: str
    content: str
    owner_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
