from beanie import PydanticObjectId, UpdateResponse
from beanie.operators import Set
from fastapi import status

from app.common.enum import UserRole
from app.common.utils import utc_now
from app.core.exceptions import AppError
from app.modules.note.models import Note
from app.modules.note.schemas import NoteCreateSchema, NoteResponse, NoteUpdateSchema
from app.modules.user.models import User


def note_not_found() -> AppError:
    return AppError("Note not found", status.HTTP_404_NOT_FOUND)


class NoteService:
    async def create_note(
        self, owner: User, note_create: NoteCreateSchema
    ) -> NoteResponse:
        note = Note(
            title=note_create.title,
            content=note_create.content,
            owner_id=owner.id,
        )
        await note.insert()
        return NoteResponse.model_validate(note)

    async def list_notes_for_owner(
        self, owner_id: PydanticObjectId, skip: int, limit: int
    ) -> tuple[list[NoteResponse], int]:
        query = Note.find(Note.owner_id == owner_id)
        total = await query.count()

        notes = await query.sort("-_id").skip(skip).limit(limit).to_list()

        return [NoteResponse.model_validate(note) for note in notes], total

    async def get_note_by_id(
        self, note_id: PydanticObjectId, user: User
    ) -> NoteResponse:
        if user.role == UserRole.ADMIN:
            note = await Note.get(note_id)
        else:
            note = await Note.find_one(Note.id == note_id, Note.owner_id == user.id)

        if note is None:
            raise note_not_found()
        return NoteResponse.model_validate(note)

    async def update_note(
        self, note_id: PydanticObjectId, user: User, note_update: NoteUpdateSchema
    ) -> NoteResponse:
        fields = note_update.model_dump(exclude_none=True)

        query = Note.find_one(Note.id == note_id, Note.owner_id == user.id)

        if fields:
            note = await query.update(
                Set({**fields, "updated_at": utc_now()}),
                response_type=UpdateResponse.NEW_DOCUMENT,
            )
        else:
            note = await query

        if note is None:
            raise note_not_found()
        return NoteResponse.model_validate(note)

    async def delete_note(self, note_id: PydanticObjectId, owner: User) -> None:
        result = await Note.find_one(
            Note.id == note_id, Note.owner_id == owner.id
        ).delete()
        if result.deleted_count == 0:
            raise note_not_found()

    async def list_all_notes(
        self, skip: int, limit: int
    ) -> tuple[list[NoteResponse], int]:
        notes = await Note.find_all().sort("-_id").skip(skip).limit(limit).to_list()
        total = await Note.get_pymongo_collection().estimated_document_count()

        return [NoteResponse.model_validate(note) for note in notes], total
