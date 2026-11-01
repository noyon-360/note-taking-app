from typing import Annotated

from fastapi import Depends

from app.modules.note.services import NoteService


def get_note_service() -> NoteService:
    return NoteService()


NoteServiceDep = Annotated[NoteService, Depends(get_note_service)]
