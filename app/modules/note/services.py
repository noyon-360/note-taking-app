from beanie import PydanticObjectId

from app.modules.note.models import Note
from app.modules.note.schemas import NoteCreateSchema, NoteResponse, NoteUpdateSchema
from app.modules.user.models import User


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

    async def get_note_by_id(self, note_id: str) -> Note:
        return await self.note_repository.get_note_by_id(note_id)

    async def update_note(self, note_id: str, note_update: NoteUpdateSchema) -> Note:
        return await self.note_repository.update_note(note_id, note_update)

    async def delete_note(self, note_id: str) -> None:
        await self.note_repository.delete_note(note_id)

    async def list_all_notes(self, skip: int, limit: int) -> tuple[list[NoteResponse], int]:
        notes = await Note.find_all().sort("-_id").skip(skip).limit(limit).to_list()
        total = await Note.get_pymongo_collection().estimated_document_count()



        return [NoteResponse.model_validate(note) for note in notes], total